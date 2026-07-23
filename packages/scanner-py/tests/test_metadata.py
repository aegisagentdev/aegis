from hoodtrade.checks.base import Context
from hoodtrade.checks.metadata import CodeSizeCheck, VenueContextCheck
from hoodtrade.config import Settings
from hoodtrade.models import Direction, Severity, TradeRequest

TOKEN = "0x2222222222222222222222222222222222222222"
QUOTE = "0x3333333333333333333333333333333333333333"


class DummyRpc:
    async def get_code(self, addr):
        return b""

    async def eth_call(self, to, data):
        return b"\x00" * 32

    async def chain_id(self):
        return 1


def _ctx(cache=None, venue="uniswap"):
    ctx = Context(
        request=TradeRequest(token=TOKEN, quote=QUOTE, amount_usd=1000, direction=Direction.BUY, venue=venue),
        settings=Settings(),
        rpc=DummyRpc(),
    )
    if cache:
        ctx.cache.update(cache)
    return ctx


async def test_code_size_normal():
    results = await CodeSizeCheck().run(_ctx(cache={"token_code_size": 5000}))
    assert results[0].severity is Severity.OK


async def test_code_size_small():
    results = await CodeSizeCheck().run(_ctx(cache={"token_code_size": 50}))
    assert results[0].severity is Severity.WARN


async def test_code_size_large():
    results = await CodeSizeCheck().run(_ctx(cache={"token_code_size": 150_000}))
    assert results[0].severity is Severity.INFO


async def test_code_size_no_code():
    assert await CodeSizeCheck().run(_ctx(cache={"token_code_size": 0})) == []


async def test_venue_uniswap():
    results = await VenueContextCheck().run(_ctx(venue="uniswap"))
    assert results[0].severity is Severity.OK
    assert "Uniswap" in results[0].title


async def test_venue_unknown():
    results = await VenueContextCheck().run(_ctx(venue="some_dex"))
    assert results[0].severity is Severity.INFO
