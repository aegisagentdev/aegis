"""Honeypot detection checks.

A honeypot token lets you buy but blocks or taxes sells. The classic technique is
to include a revert, a blacklist, or a hidden fee in the transfer/approve path that
only triggers on non-whitelisted addresses. This check simulates a sell by calling
``transfer(dead_address, 1)`` via ``eth_call`` (a read-only simulation) and inspects
whether the call reverts. It does NOT execute an actual transaction.

Limitations: some honeypots only trigger after a cooldown timer or once the pool
reaches a certain TVL; a static eth_call simulation won't catch those. But it does
catch the most common pattern (revert on transfer for non-owner) cheaply and with
zero risk.
"""

from __future__ import annotations

from ..models import CheckResult, Severity
from .base import Context

DEAD = "0x000000000000000000000000000000000000dEaD"

# The simulation runs from a zero-balance sender, so a compliant ERC-20 *should*
# revert with an insufficient-balance error. That is expected, healthy behavior —
# NOT a honeypot. We only escalate when the revert reason names a transfer
# restriction (blacklist, pause, trading-gate). This keeps normal tokens from
# false-flagging while still catching the classic "buy but can't sell" pattern.
_BALANCE_REVERTS = (
    "insufficient",
    "exceeds balance",
    "exceeds allowance",
    "transfer amount exceeds",
    "underflow",
    "subtraction",
    "0x11",  # Solidity panic(0x11): arithmetic overflow/underflow
    "erc20insufficientbalance",
)
_RESTRICTION_REVERTS = (
    "blacklist",
    "blocked",
    "whitelist",
    "not allowed",
    "not enabled",
    "paused",
    "pause",
    "trading",
    "forbidden",
    "bot",
    "cooldown",
    "restrict",
    "max wallet",
    "max tx",
    "banned",
    "frozen",
    "excluded",
)


def _classify_revert(msg: str) -> str:
    """Return 'restriction', 'balance', or 'unknown' for an eth_call revert."""
    m = msg.lower()
    if any(h in m for h in _RESTRICTION_REVERTS):
        return "restriction"
    if any(h in m for h in _BALANCE_REVERTS):
        return "balance"
    return "unknown"


def _encode_transfer(to: str, amount: int) -> str:
    selector = "0xa9059cbb"  # transfer(address,uint256)
    addr_word = to.lower().removeprefix("0x").rjust(64, "0")
    amt_word = hex(amount)[2:].rjust(64, "0")
    return selector + addr_word + amt_word


def _encode_approve(spender: str, amount: int) -> str:
    selector = "0x095ea7b3"  # approve(address,uint256)
    addr_word = spender.lower().removeprefix("0x").rjust(64, "0")
    amt_word = hex(amount)[2:].rjust(64, "0")
    return selector + addr_word + amt_word


class HoneypotTransferCheck:
    """Simulate a small transfer to the dead address. If the token reverts, selling
    is likely blocked for regular holders."""

    id = "CONTRACT-HONEYPOT"

    async def run(self, ctx: Context) -> list[CheckResult]:
        if ctx.cache.get("token_code_size") == 0:
            return []

        try:
            data = _encode_transfer(DEAD, 1)
            await ctx.rpc.eth_call(ctx.request.token, data)
        except Exception as exc:
            kind = _classify_revert(str(exc))
            if kind == "restriction":
                return [
                    CheckResult(
                        check=self.id,
                        severity=Severity.DANGER,
                        score=90,
                        title="Honeypot risk — transfer blocked",
                        detail=(
                            "A simulated transfer reverted with a restriction error (blacklist / "
                            "pause / trading-gate). This is a strong signal the token blocks "
                            "transfers for ordinary holders — you could buy but not sell."
                        ),
                        evidence={"error": str(exc)[:200]},
                    )
                ]
            if kind == "balance":
                # Expected for a zero-balance sender: the token correctly refuses.
                return [
                    CheckResult(
                        check=self.id,
                        severity=Severity.OK,
                        score=0,
                        title="Transfer behaves normally",
                        detail="transfer() reverted on insufficient balance, as a compliant ERC-20 should.",
                    )
                ]
            return [
                CheckResult(
                    check=self.id,
                    severity=Severity.INFO,
                    score=0,
                    title="Transfer simulation inconclusive",
                    detail=(
                        "A zero-balance transfer simulation reverted without a clear reason. This "
                        "cannot confirm sellability either way — rely on the GoPlus honeypot signal "
                        f"and real trade history. ({str(exc)[:120]})"
                    ),
                )
            ]

        return [
            CheckResult(
                check=self.id,
                severity=Severity.OK,
                score=0,
                title="Transfer simulation passed",
                detail="A simulated transfer(deadAddress, 1) did not revert.",
            )
        ]


class HoneypotApproveCheck:
    """Simulate an approve() call. Some tokens block approvals for non-owner addresses."""

    id = "CONTRACT-APPROVE"

    async def run(self, ctx: Context) -> list[CheckResult]:
        if ctx.cache.get("token_code_size") == 0:
            return []

        try:
            data = _encode_approve(DEAD, 2**255)
            await ctx.rpc.eth_call(ctx.request.token, data)
        except Exception as exc:
            # approve() takes no balance, so it should not revert. A restriction
            # revert is a real signal; anything else is inconclusive, not a flag.
            if _classify_revert(str(exc)) == "restriction":
                return [
                    CheckResult(
                        check=self.id,
                        severity=Severity.WARN,
                        score=25,
                        title="Approve blocked by a restriction",
                        detail=(
                            "approve(address, maxUint) reverted with a restriction error. Some "
                            "honeypots block approval to stop the victim selling via a DEX router."
                        ),
                        evidence={"error": str(exc)[:200]},
                    )
                ]
            return []

        return [
            CheckResult(
                check=self.id,
                severity=Severity.OK,
                score=0,
                title="Approve simulation passed",
                detail="approve(deadAddress, maxUint) did not revert.",
            )
        ]
