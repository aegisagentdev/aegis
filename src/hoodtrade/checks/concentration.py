"""Holder-concentration checks.

When a small number of wallets control a large share of the token supply, the rug
risk is high: those wallets can dump and crater the price. This check reads the
totalSupply and probes a configurable list of "big holder" patterns. Since there is
no on-chain index of all holders, we use a heuristic: check balanceOf for the token
contract itself (self-held supply / tax-on-transfer patterns), the pool address, and
the zero-address (burned supply). A production version would augment this with an
indexer (Blockscout / Dune) — this version is a first-order local signal.
"""

from __future__ import annotations

from ..models import CheckResult, Severity
from ..rpc import decode_uint, encode_call
from .base import Context

ZERO = "0x" + "0" * 40


class TokenSelfHoldingCheck:
    """Flag tokens where the contract itself holds a large share of supply. Common in
    tax/reflection tokens and sometimes a sign of an unreleased supply controlled by
    the deployer."""

    id = "CONC-SELF"

    async def run(self, ctx: Context) -> list[CheckResult]:
        if ctx.cache.get("token_code_size") == 0:
            return []

        try:
            supply_raw = await ctx.rpc.eth_call(ctx.request.token, encode_call("totalSupply"))
            supply = decode_uint(supply_raw)
            if supply == 0:
                return []

            self_raw = await ctx.rpc.eth_call(
                ctx.request.token,
                encode_call("balanceOf", ctx.request.token),
            )
            self_balance = decode_uint(self_raw)
        except Exception:
            return []

        ratio = self_balance / supply if supply else 0
        ctx.cache["self_hold_ratio"] = ratio

        if ratio >= 0.5:
            return [
                CheckResult(
                    check=self.id,
                    severity=Severity.DANGER,
                    score=50,
                    title=f"Token self-holds {ratio:.0%} of supply",
                    detail=(
                        "The token contract holds more than half of its own supply. This is a "
                        "strong signal that the circulating float is thin and the holder can "
                        "dump the unreleased supply."
                    ),
                    evidence={"self_balance": str(self_balance), "total_supply": str(supply)},
                )
            ]
        if ratio >= 0.2:
            return [
                CheckResult(
                    check=self.id,
                    severity=Severity.WARN,
                    score=20,
                    title=f"Token self-holds {ratio:.0%} of supply",
                    detail=(
                        "The token contract holds a significant share of its own supply. "
                        "This may be a reflection/tax mechanism or an unreleased allocation."
                    ),
                    evidence={"self_balance": str(self_balance), "total_supply": str(supply)},
                )
            ]
        return [
            CheckResult(
                check=self.id,
                severity=Severity.OK,
                score=0,
                title="Token self-holding negligible",
                detail=f"The contract holds {ratio:.1%} of its own supply.",
                evidence={"self_balance": str(self_balance), "total_supply": str(supply)},
            )
        ]


class BurnedSupplyCheck:
    """Report what share of supply has been burned (sent to 0x0...dead or 0x0...0)."""

    id = "CONC-BURNED"

    async def run(self, ctx: Context) -> list[CheckResult]:
        if ctx.cache.get("token_code_size") == 0:
            return []

        try:
            supply_raw = await ctx.rpc.eth_call(ctx.request.token, encode_call("totalSupply"))
            supply = decode_uint(supply_raw)
            if supply == 0:
                return []

            dead = "0x000000000000000000000000000000000000dEaD"
            zero_bal = decode_uint(await ctx.rpc.eth_call(ctx.request.token, encode_call("balanceOf", ZERO)))
            dead_bal = decode_uint(await ctx.rpc.eth_call(ctx.request.token, encode_call("balanceOf", dead)))
            burned = zero_bal + dead_bal
        except Exception:
            return []

        ratio = burned / supply if supply else 0
        ctx.cache["burned_ratio"] = ratio

        if ratio >= 0.95:
            return [
                CheckResult(
                    check=self.id,
                    severity=Severity.WARN,
                    score=15,
                    title=f"{ratio:.0%} of supply is burned",
                    detail=(
                        "Nearly all supply has been sent to burn addresses. The remaining "
                        "float is extremely thin — small trades can cause outsized price impact."
                    ),
                    evidence={"burned": str(burned), "total_supply": str(supply)},
                )
            ]
        return [
            CheckResult(
                check=self.id,
                severity=Severity.OK,
                score=0,
                title=f"{ratio:.1%} of supply burned",
                detail=f"{burned} tokens are in burn addresses out of {supply} total supply.",
                evidence={"burned": str(burned), "total_supply": str(supply)},
            )
        ]
