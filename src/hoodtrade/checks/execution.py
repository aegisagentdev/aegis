"""Execution-quality checks.

Robinhood Chain uses first-come-first-served sequencing, so the classic gas-auction
sandwich is structurally suppressed. It is NOT gone: MEV shifts to a latency race at
the sequencer, and cross-domain / oracle-timing games remain. These checks are about
how *your* order is likely to execute, given size and chain properties.
"""

from __future__ import annotations

from ..models import CheckResult, Severity
from .base import Context


class ChainIdentityCheck:
    id = "EXEC-CHAINID"

    async def run(self, ctx: Context) -> list[CheckResult]:
        expected = ctx.settings.chain_id
        if expected is None:
            return [
                CheckResult(
                    check=self.id,
                    severity=Severity.INFO,
                    score=0,
                    title="Chain id not pinned",
                    detail="HOODTRADE_CHAIN_ID is unset, so the RPC's chain id was not verified.",
                )
            ]
        actual = await ctx.rpc.chain_id()
        if actual != expected:
            return [
                CheckResult(
                    check=self.id,
                    severity=Severity.DANGER,
                    score=90,
                    title="RPC chain id mismatch",
                    detail=(
                        f"Configured RPC reports chain id {actual}, expected {expected}. "
                        "You may be pointed at the wrong network or a spoofed RPC."
                    ),
                    evidence={"expected": str(expected), "actual": str(actual)},
                )
            ]
        return [
            CheckResult(
                check=self.id,
                severity=Severity.OK,
                score=0,
                title="Chain id verified",
                detail=f"RPC chain id {actual} matches the configured value.",
            )
        ]


class SizeVsDepthCheck:
    """Flags trades that are large relative to the pool's active liquidity. Big orders
    into thin books eat slippage and are the juiciest targets for latency-MEV even on
    an FCFS chain."""

    id = "EXEC-SIZE"

    async def run(self, ctx: Context) -> list[CheckResult]:
        active = ctx.cache.get("active_liquidity")
        # We don't have a USD oracle wired in this build, so we reason qualitatively on
        # size bands. This is intentionally conservative and clearly labeled.
        amt = ctx.request.amount_usd
        if amt >= 100_000:
            sev, score, band = Severity.WARN, 20, "large (>= $100k)"
        elif amt >= 10_000:
            sev, score, band = Severity.INFO, 8, "medium ($10k-$100k)"
        else:
            sev, score, band = Severity.OK, 0, "small (< $10k)"
        detail = (
            f"Trade notional is {band}. On a new chain with shallow books, size this or "
            "larger should be split or routed through an aggregator (0x/1inch) to limit "
            "price impact and latency-MEV exposure."
        )
        ev = {"amount_usd": f"{amt:.2f}", "band": band}
        if active is not None:
            ev["active_liquidity"] = str(active)
        return [
            CheckResult(
                check=self.id,
                severity=sev,
                score=score,
                title=f"Trade size: {band}",
                detail=detail,
                evidence=ev,
            )
        ]


class SequencingContextCheck:
    id = "EXEC-MEV"

    async def run(self, ctx: Context) -> list[CheckResult]:
        return [
            CheckResult(
                check=self.id,
                severity=Severity.INFO,
                score=0,
                title="FCFS sequencing — reduced but not zero MEV",
                detail=(
                    "Robinhood Chain orders transactions first-come-first-served, so gas-priority "
                    "sandwiching does not apply. Residual risks: sequencer-latency ordering, oracle "
                    "update timing, and cross-domain arbitrage. Prefer tight slippage limits."
                ),
            )
        ]
