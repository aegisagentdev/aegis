from aegis.checks.base import Context
from aegis.checks.pool import PoolExistsCheck, PoolLiquidityCheck, PoolPairIntegrityCheck
from aegis.config import Settings
from aegis.models import Direction, Severity, TradeRequest

TOKEN = "0x2222222222222222222222222222222222222222"
QUOTE = "0x3333333333333333333333333333333333333333"
POOL = "0x4444444444444444444444444444444444444444"


class PoolRpc:
    def __init__(self, pool_code=b"\x60" * 50, liquidity=1000, token0=TOKEN, token1=QUOTE):
        self._pool_code = pool_code
        self._liquidity = liquidity
        self._token0 = token0
        self._token1 = token1

    async def get_code(self, address):
        if address.lower() == POOL.lower():
            return self._pool_code
        return b"\x60" * 10

    async def eth_call(self, to, data):
        sel = data[:10]
        if sel == "0x1a686502":  # liquidity
            return self._liquidity.to_bytes(32, "big")
        if sel == "0x0dfe1681":  # token0
            return bytes(12) + bytes.fromhex(self._token0.removeprefix("0x"))
        if sel == "0xd21220a7":  # token1
            return bytes(12) + bytes.fromhex(self._token1.removeprefix("0x"))
        return b"\x00" * 32

    async def chain_id(self):
        return 1


def _ctx(rpc, pool=POOL):
    return Context(
        request=TradeRequest(token=TOKEN, quote=QUOTE, amount_usd=1000, direction=Direction.BUY, pool=pool),
        settings=Settings(),
        rpc=rpc,
    )


async def test_pool_exists_no_code():
    rpc = PoolRpc(pool_code=b"")
    results = await PoolExistsCheck().run(_ctx(rpc))
    assert results[0].severity is Severity.DANGER


async def test_pool_exists_ok():
    results = await PoolExistsCheck().run(_ctx(PoolRpc()))
    assert results[0].severity is Severity.OK


async def test_pool_no_pool_provided():
    results = await PoolExistsCheck().run(_ctx(PoolRpc(), pool=None))
    assert results[0].severity is Severity.INFO


async def test_pool_liquidity_zero():
    rpc = PoolRpc(liquidity=0)
    ctx = _ctx(rpc)
    results = await PoolLiquidityCheck().run(ctx)
    assert results[0].severity is Severity.DANGER
    assert ctx.cache["active_liquidity"] == 0


async def test_pool_liquidity_ok():
    rpc = PoolRpc(liquidity=5000)
    ctx = _ctx(rpc)
    results = await PoolLiquidityCheck().run(ctx)
    assert results[0].severity is Severity.OK
    assert ctx.cache["active_liquidity"] == 5000


async def test_pair_integrity_mismatch():
    wrong_token = "0x9999999999999999999999999999999999999999"
    rpc = PoolRpc(token0=wrong_token, token1=QUOTE)
    results = await PoolPairIntegrityCheck().run(_ctx(rpc))
    assert results[0].severity is Severity.DANGER


async def test_pair_integrity_ok():
    rpc = PoolRpc(token0=TOKEN, token1=QUOTE)
    results = await PoolPairIntegrityCheck().run(_ctx(rpc))
    assert results[0].severity is Severity.OK
