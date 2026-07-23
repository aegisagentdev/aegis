from aegis.checks.base import Context
from aegis.checks.proxy import ProxyDetectionCheck
from aegis.config import Settings
from aegis.models import Direction, Severity, TradeRequest

TOKEN = "0x2222222222222222222222222222222222222222"
QUOTE = "0x3333333333333333333333333333333333333333"


class ProxyRpc:
    def __init__(self, impl_slot="0x" + "0" * 64):
        self._impl_slot = impl_slot

    async def get_code(self, address):
        return b"\x60" * 100

    async def eth_call(self, to, data):
        return b"\x00" * 32

    async def _call(self, method, params):
        if method == "eth_getStorageAt":
            return self._impl_slot
        return "0x" + "0" * 64

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


async def test_no_proxy():
    rpc = ProxyRpc(impl_slot="0x" + "0" * 64)
    ctx = _ctx(rpc, cache={"token_code_size": 100})
    results = await ProxyDetectionCheck().run(ctx)
    assert results[0].severity is Severity.OK


async def test_proxy_detected():
    impl = "0x" + "0" * 24 + "aa" * 20
    rpc = ProxyRpc(impl_slot=impl)
    ctx = _ctx(rpc, cache={"token_code_size": 100})
    results = await ProxyDetectionCheck().run(ctx)
    assert results[0].severity is Severity.WARN
    assert "proxy" in results[0].title.lower()


async def test_proxy_skipped_no_code():
    ctx = _ctx(ProxyRpc(), cache={"token_code_size": 0})
    assert await ProxyDetectionCheck().run(ctx) == []
