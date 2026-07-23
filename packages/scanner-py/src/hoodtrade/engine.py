"""Scan engine: run the check battery, aggregate, decide a verdict.

The verdict is decided here, deterministically, from the summed risk score and any
DANGER-severity finding. The AI layer (hoodtrade.ai) only *explains* the result — it
never overrides the gate. This separation is deliberate: the go/no-go signal a trader
relies on must be reproducible and auditable, not a model's judgement call.
"""

from __future__ import annotations

from .checks import Context, default_checks
from .config import Settings
from .models import CheckResult, ScanReport, Severity, TradeRequest, Verdict
from .rpc import RpcClient


def decide(score: int, results: list[CheckResult], settings: Settings) -> Verdict:
    if any(r.severity is Severity.DANGER for r in results):
        return Verdict.NO_GO
    if score >= settings.nogo_score:
        return Verdict.NO_GO
    if score >= settings.caution_score:
        return Verdict.CAUTION
    return Verdict.GO


async def run_scan(request: TradeRequest, settings: Settings, checks=None) -> ScanReport:
    checks = checks if checks is not None else default_checks()
    async with RpcClient(settings.rpc_url, timeout=settings.request_timeout) as rpc:
        ctx = Context(request=request, settings=settings, rpc=rpc)
        results: list[CheckResult] = []
        notes: list[str] = []

        # Enrich from external sources before the battery runs so reputation and
        # market checks can read them from the shared cache. A source failure is a
        # note, never a scan abort.
        if settings.goplus_enabled and settings.goplus_chain_id is not None:
            from .sources import fetch_goplus

            try:
                ctx.cache["goplus"] = await fetch_goplus(
                    settings.goplus_chain_id, request.token, settings.request_timeout
                )
            except Exception as exc:  # noqa: BLE001 — external source down: degrade gracefully
                notes.append(f"GoPlus lookup failed: {exc}")

        if settings.dexscreener_enabled and settings.dexscreener_chain is not None:
            from .sources import fetch_market

            try:
                ctx.cache["market"] = await fetch_market(
                    settings.dexscreener_chain, request.token, settings.request_timeout
                )
            except Exception as exc:  # noqa: BLE001 — external source down: degrade gracefully
                notes.append(f"DexScreener lookup failed: {exc}")

        for check in checks:
            try:
                results.extend(await check.run(ctx))
            except Exception as exc:  # noqa: BLE001 — infra failure: record, keep scanning
                notes.append(f"{getattr(check, 'id', type(check).__name__)} failed: {exc}")

    if not results:
        return ScanReport(
            request=request,
            verdict=Verdict.UNKNOWN,
            score=0,
            results=[],
            notes=notes or ["No checks produced output — RPC may be unreachable."],
        )

    score = sum(r.score for r in results)
    verdict = decide(score, results, settings)
    name, symbol = _resolve_identity(ctx)
    market = ctx.cache.get("market")
    return ScanReport(
        request=request,
        verdict=verdict,
        score=score,
        token_name=name,
        token_symbol=symbol,
        price_usd=getattr(market, "price_usd", None),
        market_cap=getattr(market, "market_cap", None),
        liquidity_usd=getattr(market, "liquidity_usd", None),
        volume_24h=getattr(market, "volume_24h", None),
        results=results,
        notes=notes,
    )


def _resolve_identity(ctx: Context) -> tuple[str | None, str | None]:
    """Best-effort token name/symbol from whichever source has it, cheapest first."""
    name = ctx.cache.get("token_name")
    symbol = ctx.cache.get("token_symbol")
    goplus = ctx.cache.get("goplus")
    if goplus is not None:
        name = name or getattr(goplus, "token_name", None)
        symbol = symbol or getattr(goplus, "token_symbol", None)
    market = ctx.cache.get("market")
    if market is not None:
        name = name or getattr(market, "name", None)
        symbol = symbol or getattr(market, "symbol", None)
    return (name if isinstance(name, str) else None, symbol if isinstance(symbol, str) else None)
