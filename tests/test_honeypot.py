from hoodtrade.checks.base import Context
from hoodtrade.checks.honeypot import HoneypotApproveCheck, HoneypotTransferCheck
from hoodtrade.config import Settings
from hoodtrade.models import Direction, Severity, TradeRequest
from hoodtrade.rpc import RpcError

TOKEN = "0x2222222222222222222222222222222222222222"
QUOTE = "0x3333333333333333333333333333333333333333"


class RevertingRpc:
    """Reverts with a restriction reason — a real honeypot signal."""

    async def get_code(self, address):
        return b"\x60" * 100

    async def eth_call(self, to, data):
        raise RpcError("execution reverted: transfer blocked")

    async def chain_id(self):
        return 1


class BalanceRevertRpc:
    """Reverts on insufficient balance — expected for a zero-balance sender."""

    async def get_code(self, address):
        return b"\x60" * 100

    async def eth_call(self, to, data):
        raise RpcError("execution reverted: ERC20: transfer amount exceeds balance")

    async def chain_id(self):
        return 1


class GenericRevertRpc:
    """Reverts with no decodable reason — inconclusive."""

    async def get_code(self, address):
        return b"\x60" * 100

    async def eth_call(self, to, data):
        raise RpcError("execution reverted")

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


async def test_honeypot_transfer_restriction_is_danger():
    ctx = _ctx(RevertingRpc(), cache={"token_code_size": 100})
    results = await HoneypotTransferCheck().run(ctx)
    assert results[0].severity is Severity.DANGER
    assert "honeypot" in results[0].title.lower()


async def test_honeypot_balance_revert_is_ok():
    # A zero-balance sender hitting an insufficient-balance revert is healthy,
    # not a honeypot — this must NOT flag danger.
    ctx = _ctx(BalanceRevertRpc(), cache={"token_code_size": 100})
    results = await HoneypotTransferCheck().run(ctx)
    assert results[0].severity is Severity.OK


async def test_honeypot_generic_revert_is_inconclusive():
    ctx = _ctx(GenericRevertRpc(), cache={"token_code_size": 100})
    results = await HoneypotTransferCheck().run(ctx)
    assert results[0].severity is Severity.INFO
    assert results[0].score == 0


async def test_honeypot_transfer_passes():
    ctx = _ctx(PassingRpc(), cache={"token_code_size": 100})
    results = await HoneypotTransferCheck().run(ctx)
    assert results[0].severity is Severity.OK


async def test_honeypot_skipped_when_no_code():
    ctx = _ctx(PassingRpc(), cache={"token_code_size": 0})
    assert await HoneypotTransferCheck().run(ctx) == []


async def test_approve_restriction_is_warn():
    ctx = _ctx(RevertingRpc(), cache={"token_code_size": 100})
    results = await HoneypotApproveCheck().run(ctx)
    assert results[0].severity is Severity.WARN


async def test_approve_balance_revert_is_quiet():
    # approve() reverting on a non-restriction reason is inconclusive, not a flag.
    ctx = _ctx(BalanceRevertRpc(), cache={"token_code_size": 100})
    assert await HoneypotApproveCheck().run(ctx) == []


async def test_approve_passes():
    ctx = _ctx(PassingRpc(), cache={"token_code_size": 100})
    results = await HoneypotApproveCheck().run(ctx)
    assert results[0].severity is Severity.OK
