"""Tests for the DexScreener source client and pair selection."""

import httpx
import pytest

from aegis.sources.dexscreener import (
    CHAIN_SLUGS,
    DexScreenerClient,
    DexScreenerError,
    MarketData,
    _f,
    _i,
    _quote_side_liquidity,
)

PAIR_SHALLOW = {
    "baseToken": {"symbol": "TKN", "name": "Token", "address": "0xabc"},
    "quoteToken": {"symbol": "WETH"},
    "dexId": "uniswap",
    "pairAddress": "0xpair1",
    "priceUsd": "0.01",
    "liquidity": {"usd": 5000.0},
    "volume": {"h24": 1000.0},
    "fdv": 50000.0,
    "txns": {"h24": {"buys": 10, "sells": 5}},
}
PAIR_DEEP = {
    "baseToken": {"symbol": "TKN", "name": "Token", "address": "0xabc"},
    "quoteToken": {"symbol": "USDC"},
    "dexId": "uniswap",
    "pairAddress": "0xpair2",
    "priceUsd": "0.011",
    "liquidity": {"usd": 40000.0},
    "volume": {"h24": 9000.0},
    "fdv": 60000.0,
    "marketCap": 55000.0,
    "txns": {"h24": {"buys": 200, "sells": 150}},
}


def test_quote_side_liquidity_matches_trading_ui():
    # CASHCAT-like pool: total $256,849 = base side ($138,592) + quote/WETH side.
    # base_reserve 26,672,759 tokens @ $0.005196 -> quote side ~= $118,257.
    quote = _quote_side_liquidity(256849.0, 26672759.0, 0.005196)
    assert quote is not None
    assert 117000 < quote < 120000  # matches the WETH side shown by trading UIs


def test_quote_side_liquidity_falls_back_to_total():
    # Missing reserve -> can't split, return the full total.
    assert _quote_side_liquidity(40000.0, None, 0.01) == 40000.0
    # Dirty data (base side exceeds total) -> fall back to total, never negative.
    assert _quote_side_liquidity(1000.0, 10_000_000.0, 1.0) == 1000.0
    assert _quote_side_liquidity(None, 1.0, 1.0) is None


def test_coercion_helpers():
    assert _f("0.5") == 0.5
    assert _f(3) == 3.0
    assert _f("") is None
    assert _f("bad") is None
    assert _i("7") == 7
    assert _i("") is None


def test_from_pairs_picks_deepest():
    m = MarketData.from_pairs("robinhood", "0xabc", [PAIR_SHALLOW, PAIR_DEEP])
    assert m is not None
    assert m.pair_address == "0xpair2"  # deeper liquidity wins
    assert m.liquidity_usd == 40000.0
    assert m.market_cap == 55000.0  # distinct from liquidity
    assert m.market_cap != m.liquidity_usd
    assert m.quote_symbol == "USDC"
    assert m.buys_24h == 200
    assert m.sells_24h == 150
    assert m.pair_count == 2


def test_market_cap_falls_back_to_fdv():
    pair = {"liquidity": {"usd": 100.0}, "fdv": 12345.0, "baseToken": {}, "quoteToken": {}}
    m = MarketData.from_pairs("robinhood", "0xabc", [pair])
    assert m is not None
    assert m.market_cap == 12345.0


def test_from_pairs_empty_is_none():
    assert MarketData.from_pairs("robinhood", "0xabc", []) is None


def test_robinhood_slug_present():
    assert CHAIN_SLUGS["robinhood"] == "robinhood"


@pytest.mark.asyncio
async def test_market_parses_list_response():
    def handler(request: httpx.Request) -> httpx.Response:
        assert "/robinhood/" in str(request.url)
        return httpx.Response(200, json=[PAIR_SHALLOW, PAIR_DEEP])

    client = DexScreenerClient()
    client._client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    m = await client.market("robinhood", "0xabc")
    await client.aclose()
    assert m is not None
    assert m.liquidity_usd == 40000.0


@pytest.mark.asyncio
async def test_market_none_when_no_pairs():
    client = DexScreenerClient()
    client._client = httpx.AsyncClient(transport=httpx.MockTransport(lambda r: httpx.Response(200, json=[])))
    m = await client.market("robinhood", "0xabc")
    await client.aclose()
    assert m is None


@pytest.mark.asyncio
async def test_market_raises_on_http_error():
    client = DexScreenerClient()
    client._client = httpx.AsyncClient(transport=httpx.MockTransport(lambda r: httpx.Response(500)))
    with pytest.raises(DexScreenerError):
        await client.market("robinhood", "0xabc")
    await client.aclose()
