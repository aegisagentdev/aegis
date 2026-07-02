"""Market checks backed by the DexScreener data source.

These consume a pre-fetched ``MarketData`` stashed in ``ctx.cache["market"]`` by
the engine. Like the reputation checks they are additive: with no market data
(untraded token, source disabled) they stay silent and the on-chain battery
stands alone. They translate live trading data into pre-trade risk: is there
enough real liquidity for your size, is the market active, is flow one-sided.
"""

from __future__ import annotations

from ..models import CheckResult, Severity
from ..sources.dexscreener import MarketData
from .base import Context


def _market(ctx: Context) -> MarketData | None:
    data = ctx.cache.get("market")
    return data if isinstance(data, MarketData) else None


class MarketLiquidityCheck:
    """Absolute pooled liquidity — thin books are exit traps regardless of hype."""

    id = "MKT-LIQUIDITY"

    async def run(self, ctx: Context) -> list[CheckResult]:
        m = _market(ctx)
        if m is None:
            return []
        liq = m.liquidity_usd
        if liq is None:
            return []

        where = f"{m.dex or 'DEX'} {m.symbol or ''}".strip()
        total_note = f" (pool total ${m.pooled_total_usd:,.0f})" if m.pooled_total_usd else ""
        evidence = {"source": "dexscreener", "liquidity_usd": f"{liq:.0f}"}
        if m.pooled_total_usd:
            evidence["pooled_total_usd"] = f"{m.pooled_total_usd:.0f}"

        if liq < 5_000:
            return [
                CheckResult(
                    check=self.id,
                    severity=Severity.DANGER,
                    score=70,
                    title=f"Very thin liquidity (${liq:,.0f})",
                    detail=(
                        f"Only ${liq:,.0f} of withdrawable ({m.quote_symbol or 'quote'}) liquidity on "
                        f"{where}{total_note}. A book this thin means even a small sell craters the "
                        "price and you may not be able to exit."
                    ),
                    evidence=evidence,
                )
            ]
        if liq < 25_000:
            return [
                CheckResult(
                    check=self.id,
                    severity=Severity.WARN,
                    score=25,
                    title=f"Low liquidity (${liq:,.0f})",
                    detail=(
                        f"${liq:,.0f} of withdrawable ({m.quote_symbol or 'quote'}) liquidity on "
                        f"{where}{total_note}. Expect meaningful slippage and difficulty exiting a "
                        "larger position."
                    ),
                    evidence=evidence,
                )
            ]
        return [
            CheckResult(
                check=self.id,
                severity=Severity.OK,
                score=0,
                title=f"Liquidity ${liq:,.0f}",
                detail=(
                    f"${liq:,.0f} of withdrawable ({m.quote_symbol or 'quote'}) liquidity"
                    f"{total_note}, across {m.pair_count} pair(s)."
                ),
                evidence=evidence,
            )
        ]


class MarketDepthCheck:
    """Your trade size measured against real pooled liquidity."""

    id = "MKT-DEPTH"

    async def run(self, ctx: Context) -> list[CheckResult]:
        m = _market(ctx)
        if m is None or not m.liquidity_usd:
            return []
        size = ctx.request.amount_usd
        ratio = size / m.liquidity_usd
        pct = ratio * 100
        if ratio >= 0.10:
            sev, score = Severity.DANGER, 60
            note = "This will move the price hard and incur severe slippage."
        elif ratio >= 0.02:
            sev, score = Severity.WARN, 25
            note = "Split the order or route via an aggregator to limit impact."
        else:
            sev, score = Severity.OK, 0
            note = "Trade is small relative to pooled liquidity."
        return [
            CheckResult(
                check=self.id,
                severity=sev,
                score=score,
                title=f"Trade is {pct:.1f}% of pooled liquidity",
                detail=(f"${size:,.0f} against ${m.liquidity_usd:,.0f} of liquidity is {pct:.1f}% of the pool. {note}"),
                evidence={"source": "dexscreener", "size_ratio": f"{ratio:.4f}"},
            )
        ]


class MarketActivityCheck:
    """Volume and buy/sell balance — dead or one-sided markets are red flags."""

    id = "MKT-ACTIVITY"

    async def run(self, ctx: Context) -> list[CheckResult]:
        m = _market(ctx)
        if m is None:
            return []
        out: list[CheckResult] = []

        vol = m.volume_24h
        if vol is not None and vol < 1_000:
            out.append(
                CheckResult(
                    check=self.id,
                    severity=Severity.WARN,
                    score=15,
                    title=f"Near-zero 24h volume (${vol:,.0f})",
                    detail=(
                        f"DexScreener reports ${vol:,.0f} traded in 24h. An inactive market makes "
                        "exit unreliable and price marks unreliable."
                    ),
                    evidence={"source": "dexscreener", "volume_24h": f"{vol:.0f}"},
                )
            )

        buys, sells = m.buys_24h, m.sells_24h
        if buys is not None and sells is not None and (buys + sells) >= 20:
            total = buys + sells
            sell_share = sells / total
            if sell_share >= 0.75:
                out.append(
                    CheckResult(
                        check=self.id,
                        severity=Severity.WARN,
                        score=20,
                        title=f"Sell-heavy flow ({sells}/{total} sells)",
                        detail=(
                            f"{sells} sells vs {buys} buys in 24h. Heavily one-sided selling can "
                            "signal holders exiting."
                        ),
                        evidence={"source": "dexscreener", "buys": str(buys), "sells": str(sells)},
                    )
                )
            elif buys / total >= 0.95 and total >= 50:
                out.append(
                    CheckResult(
                        check=self.id,
                        severity=Severity.INFO,
                        score=5,
                        title=f"Almost no sells ({sells}/{total})",
                        detail=(
                            f"{buys} buys but only {sells} sells in 24h. Near-absent selling can be "
                            "organic — or a honeypot where sells are blocked. Cross-check the "
                            "honeypot findings."
                        ),
                        evidence={"source": "dexscreener", "buys": str(buys), "sells": str(sells)},
                    )
                )

        if not out and m.price_usd is not None:
            out.append(
                CheckResult(
                    check=self.id,
                    severity=Severity.OK,
                    score=0,
                    title="Market active",
                    detail=(
                        f"Price ${m.price_usd:.6g}"
                        + (f", 24h vol ${vol:,.0f}" if vol is not None else "")
                        + (f", {buys}/{(buys or 0) + (sells or 0)} buys" if buys is not None else "")
                    ),
                    evidence={"source": "dexscreener"},
                )
            )
        return out
