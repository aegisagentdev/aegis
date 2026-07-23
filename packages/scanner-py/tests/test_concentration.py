from aegis.checks.base import Context
from aegis.checks.concentration import BurnedSupplyCheck, TokenSelfHoldingCheck
from aegis.config import Settings
from aegis.models import Direction, Severity, TradeRequest

TOKEN = "0x2222222222222222222222222222222222222222"
QUOTE = "0x3333333333333333333333333333333333333333"
ZERO = "0x" + "0" * 40
DEAD = "0x000000000000000000000000000000000000dEaD"


class ConcentrationRpc:
    def __init__(self, supply: int, self_balance: int, zero_balance: int = 0, dead_balance: int = 0):
        self._supply = supply
        self._self_balance = self_balance
        self._zero_balance = zero_balance
        self._dead_balance = dead_balance

    async def get_code(self, address):
        return b"\x60" * 100

    async def eth_call(self, to, data):
        sel = data[:10]
        if sel == "0x18160ddd":  # totalSupply
            return self._supply.to_bytes(32, "big")
        if sel == "0x70a08231":  # balanceOf
            addr_hex = data[10:].lstrip("0")
            if not addr_hex or addr_hex == "0":
                return self._zero_balance.to_bytes(32, "big")
            if addr_hex.lower() == "dead":
                return self._dead_balance.to_bytes(32, "big")
            if addr_hex.lower() == TOKEN.lower().removeprefix("0x").lstrip("0"):
                return self._self_balance.to_bytes(32, "big")
            return (0).to_bytes(32, "big")
        return b"\x00" * 32

    async def chain_id(self):
        return 1


def _ctx(rpc, cache=None):
    ctx = Context(
        request=TradeRequest(token=TOKEN, quote=QUOTE, amount_usd=1000, direction=Direction.BUY),
        settings=Settings(),
        rpc=rpc,
    )
    if cache:
        ctx.cache.update(cache)
    return ctx


async def test_self_holding_high():
    rpc = ConcentrationRpc(supply=1_000_000, self_balance=600_000)
    ctx = _ctx(rpc, cache={"token_code_size": 100})
    results = await TokenSelfHoldingCheck().run(ctx)
    assert results[0].severity is Severity.DANGER


async def test_self_holding_moderate():
    rpc = ConcentrationRpc(supply=1_000_000, self_balance=250_000)
    ctx = _ctx(rpc, cache={"token_code_size": 100})
    results = await TokenSelfHoldingCheck().run(ctx)
    assert results[0].severity is Severity.WARN


async def test_self_holding_low():
    rpc = ConcentrationRpc(supply=1_000_000, self_balance=10_000)
    ctx = _ctx(rpc, cache={"token_code_size": 100})
    results = await TokenSelfHoldingCheck().run(ctx)
    assert results[0].severity is Severity.OK


async def test_self_holding_skipped_no_code():
    rpc = ConcentrationRpc(supply=1_000_000, self_balance=600_000)
    ctx = _ctx(rpc, cache={"token_code_size": 0})
    assert await TokenSelfHoldingCheck().run(ctx) == []


async def test_burned_supply_high():
    rpc = ConcentrationRpc(supply=1_000_000, self_balance=0, zero_balance=500_000, dead_balance=460_000)
    ctx = _ctx(rpc, cache={"token_code_size": 100})
    results = await BurnedSupplyCheck().run(ctx)
    assert results[0].severity is Severity.WARN


async def test_burned_supply_normal():
    rpc = ConcentrationRpc(supply=1_000_000, self_balance=0, zero_balance=100, dead_balance=200)
    ctx = _ctx(rpc, cache={"token_code_size": 100})
    results = await BurnedSupplyCheck().run(ctx)
    assert results[0].severity is Severity.OK
