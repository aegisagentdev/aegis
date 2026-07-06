"""Tests for DexScreener-backed market checks."""

import pytest

from hoodtrade.checks.market import (
    MarketActivityCheck,
    MarketDepthCheck,
    MarketLiquidityCheck,
)
from hoodtrade.cli import _apply_young_chain
from hoodtrade.config import Settings
from hoodtrade.models import Severity
from hoodtrade.sources.dexscreener import MarketData


def _mkt(**kwargs) -> MarketData:
    base = dict(chain="robinhood", token_address="0xabc", symbol="TKN", dex="uniswap")
    base.update(kwargs)
    return MarketData(**base)


def _lenient() -> Settings:
    s = Settings()
    _apply_young_chain(s)
    return s


@pytest.mark.asyncio
async def test_no_market_data_is_silent(make_context):
    ctx = make_context(rpc=None)
    assert await MarketLiquidityCheck().run(ctx) == []
    assert await MarketDepthCheck().run(ctx) == []
    assert await MarketActivityCheck().run(ctx) == []


@pytest.mark.asyncio
async def test_very_thin_liquidity_is_danger(make_context):
    ctx = make_context(rpc=None, cache={"market": _mkt(liquidity_usd=3000.0)})
    results = await MarketLiquidityCheck().run(ctx)
    assert results[0].severity is Severity.DANGER


@pytest.mark.asyncio
async def test_low_liquidity_is_warn(make_context):
    ctx = make_context(rpc=None, cache={"market": _mkt(liquidity_usd=15000.0)})
    results = await MarketLiquidityCheck().run(ctx)
    assert results[0].severity is Severity.WARN


@pytest.mark.asyncio
async def test_healthy_liquidity_is_ok(make_context):
    ctx = make_context(rpc=None, cache={"market": _mkt(liquidity_usd=500000.0, pair_count=3)})
    results = await MarketLiquidityCheck().run(ctx)
    assert results[0].severity is Severity.OK


@pytest.mark.asyncio
async def test_depth_large_trade_is_danger(make_context, default_request):
    # default_request is $1000; against $5000 liquidity that's 20%
    ctx = make_context(rpc=None, cache={"market": _mkt(liquidity_usd=5000.0)})
    results = await MarketDepthCheck().run(ctx)
    assert results[0].severity is Severity.DANGER


@pytest.mark.asyncio
async def test_thin_liquidity_lenient_is_warn_not_danger(make_context):
    # On a young chain a near-empty book should caution, not hard-block (NO-GO).
    ctx = make_context(rpc=None, settings=_lenient(), cache={"market": _mkt(liquidity_usd=500.0)})
    results = await MarketLiquidityCheck().run(ctx)
    assert results[0].severity is Severity.WARN


@pytest.mark.asyncio
async def test_oversized_trade_lenient_is_warn_not_danger(make_context, default_request):
    # $1000 into a $5000 pool is 20% impact; lenient mode warns instead of blocking.
    ctx = make_context(rpc=None, settings=_lenient(), cache={"market": _mkt(liquidity_usd=5000.0)})
    results = await MarketDepthCheck().run(ctx)
    assert results[0].severity is Severity.WARN


@pytest.mark.asyncio
async def test_depth_small_trade_is_ok(make_context):
    ctx = make_context(rpc=None, cache={"market": _mkt(liquidity_usd=1_000_000.0)})
    results = await MarketDepthCheck().run(ctx)
    assert results[0].severity is Severity.OK


@pytest.mark.asyncio
async def test_dead_volume_is_warn(make_context):
    ctx = make_context(rpc=None, cache={"market": _mkt(liquidity_usd=100000.0, volume_24h=200.0, price_usd=0.01)})
    results = await MarketActivityCheck().run(ctx)
    assert any(r.severity is Severity.WARN for r in results)


@pytest.mark.asyncio
async def test_sell_heavy_flow_is_warn(make_context):
    ctx = make_context(
        rpc=None,
        cache={"market": _mkt(liquidity_usd=100000.0, volume_24h=50000.0, buys_24h=5, sells_24h=45, price_usd=0.01)},
    )
    results = await MarketActivityCheck().run(ctx)
    assert any(r.severity is Severity.WARN and "sell" in r.title.lower() for r in results)


@pytest.mark.asyncio
async def test_active_balanced_market_is_ok(make_context):
    ctx = make_context(
        rpc=None,
        cache={"market": _mkt(liquidity_usd=100000.0, volume_24h=50000.0, buys_24h=100, sells_24h=90, price_usd=0.01)},
    )
    results = await MarketActivityCheck().run(ctx)
    assert results[0].severity is Severity.OK
