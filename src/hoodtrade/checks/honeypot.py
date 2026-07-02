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
            msg = str(exc).lower()
            if "revert" in msg or "execution reverted" in msg:
                return [
                    CheckResult(
                        check=self.id,
                        severity=Severity.DANGER,
                        score=90,
                        title="Honeypot risk — transfer() reverts",
                        detail=(
                            "A simulated transfer(deadAddress, 1) reverted. This is a strong "
                            "signal that the token blocks transfers for non-whitelisted addresses, "
                            "meaning you can buy but cannot sell."
                        ),
                        evidence={"error": str(exc)[:200]},
                    )
                ]
            return [
                CheckResult(
                    check=self.id,
                    severity=Severity.INFO,
                    score=5,
                    title="Transfer simulation inconclusive",
                    detail=f"The simulated transfer did not complete cleanly: {str(exc)[:150]}",
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
            msg = str(exc).lower()
            if "revert" in msg or "execution reverted" in msg:
                return [
                    CheckResult(
                        check=self.id,
                        severity=Severity.WARN,
                        score=25,
                        title="Approve simulation reverts",
                        detail=(
                            "approve(address, maxUint) reverted. Some honeypots block approval to "
                            "prevent the victim from selling via a DEX router. Could also be a "
                            "non-standard approval implementation."
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
