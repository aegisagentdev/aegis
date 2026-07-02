from hoodtrade.checks.base import Context
from hoodtrade.checks.honeypot import HoneypotApproveCheck, HoneypotTransferCheck
from hoodtrade.config import Settings
from hoodtrade.models import Direction, Severity, TradeRequest
from hoodtrade.rpc import RpcError

TOKEN = "0x2222222222222222222222222222222222222222"
QUOTE = "0x3333333333333333333333333333333333333333"


class RevertingRpc:
    async def get_code(self, address):
        return b"\x60" * 100

    async def eth_call(self, to, data):
        raise RpcError("execution reverted: transfer blocked")

    async def chain_id(self):
        return 1


class PassingRpc:
    async def get_code(self, address):
        return b"\x60" * 100

    async def eth_call(self, to, data):
        return (1).to_bytes(32, "big")

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


async def test_honeypot_transfer_reverts():
    ctx = _ctx(RevertingRpc(), cache={"token_code_size": 100})
    results = await HoneypotTransferCheck().run(ctx)
    assert results[0].severity is Severity.DANGER
    assert "honeypot" in results[0].title.lower()


async def test_honeypot_transfer_passes():
    ctx = _ctx(PassingRpc(), cache={"token_code_size": 100})
    results = await HoneypotTransferCheck().run(ctx)
    assert results[0].severity is Severity.OK


async def test_honeypot_skipped_when_no_code():
    ctx = _ctx(PassingRpc(), cache={"token_code_size": 0})
    assert await HoneypotTransferCheck().run(ctx) == []


async def test_approve_reverts():
    ctx = _ctx(RevertingRpc(), cache={"token_code_size": 100})
    results = await HoneypotApproveCheck().run(ctx)
    assert results[0].severity is Severity.WARN


async def test_approve_passes():
    ctx = _ctx(PassingRpc(), cache={"token_code_size": 100})
    results = await HoneypotApproveCheck().run(ctx)
    assert results[0].severity is Severity.OK
