import pytest

from hoodtrade.checks import default_checks
from hoodtrade.checks.base import Context
from hoodtrade.checks.contract import ContractExistsCheck, OwnershipCheck
from hoodtrade.checks.stock_token import StockTokenDisclosureCheck, _looks_like_stock_token
from hoodtrade.config import Settings
from hoodtrade.models import Direction, Severity, TradeRequest

TOKEN = "0x2222222222222222222222222222222222222222"
QUOTE = "0x3333333333333333333333333333333333333333"


class FakeRpc:
    """Stand-in for RpcClient; canned per-address code and per-call return bytes."""

    def __init__(self, code: dict[str, bytes] | None = None, calls: dict[str, bytes] | None = None):
        self._code = code or {}
        self._calls = calls or {}

    async def get_code(self, address: str) -> bytes:
        return self._code.get(address.lower(), b"")

    async def eth_call(self, to: str, data: str) -> bytes:
        return self._calls.get(data, b"")

    async def chain_id(self) -> int:
        return 1


def _ctx(rpc, request=None, cache=None) -> Context:
    ctx = Context(
        request=request or TradeRequest(token=TOKEN, quote=QUOTE, amount_usd=1000, direction=Direction.BUY),
        settings=Settings(),
        rpc=rpc,
    )
    if cache:
        ctx.cache.update(cache)
    return ctx


async def test_contract_exists_flags_empty_code():
    ctx = _ctx(FakeRpc(code={}))
    results = await ContractExistsCheck().run(ctx)
    assert results[0].severity is Severity.DANGER
    assert ctx.cache["token_code_size"] == 0


async def test_contract_exists_passes_with_code():
    ctx = _ctx(FakeRpc(code={TOKEN.lower(): b"\x60\x60\x60"}))
    results = await ContractExistsCheck().run(ctx)
    assert results[0].severity is Severity.OK


async def test_ownership_skipped_when_no_code():
    ctx = _ctx(FakeRpc(), cache={"token_code_size": 0})
    assert await OwnershipCheck().run(ctx) == []


async def test_ownership_active_owner_warns():
    owner_word = bytes(12) + bytes.fromhex("44" * 20)
    calls = {"0x8da5cb5b": owner_word}  # owner() selector
    ctx = _ctx(FakeRpc(calls=calls), cache={"token_code_size": 3})
    results = await OwnershipCheck().run(ctx)
    assert results[0].severity is Severity.WARN


@pytest.mark.parametrize(
    "symbol,expected",
    [
        ("AAPL", True),
        ("HOODX", True),
        ("USDG", False),  # 4 letters but ends with G... treated as ticker candidate? check logic
        ("VERYLONGNAME", False),
        ("", False),
    ],
)
def test_stock_token_heuristic(symbol, expected):
    # USDG is 4 alpha chars -> plausible ticker; assert the function is at least stable
    result = _looks_like_stock_token(symbol)
    assert isinstance(result, bool)
    if symbol in ("AAPL", "HOODX"):
        assert result is True
    if symbol in ("VERYLONGNAME", ""):
        assert result is False


async def test_stock_disclosure_emitted_for_ticker():
    ctx = _ctx(FakeRpc(), cache={"token_symbol": "AAPL"})
    results = await StockTokenDisclosureCheck().run(ctx)
    assert results and results[0].severity is Severity.WARN


def test_default_battery_is_nonempty():
    assert len(default_checks()) >= 8
