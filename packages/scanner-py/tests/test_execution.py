from aegis.checks.base import Context
from aegis.checks.execution import ChainIdentityCheck, SequencingContextCheck, SizeVsDepthCheck
from aegis.config import Settings
from aegis.models import Direction, Severity, TradeRequest

TOKEN = "0x2222222222222222222222222222222222222222"
QUOTE = "0x3333333333333333333333333333333333333333"


class FakeRpc:
    def __init__(self, chain_id_val=42161):
        self._chain_id = chain_id_val

    async def get_code(self, address):
        return b"\x60" * 10

    async def eth_call(self, to, data):
        return b"\x00" * 32

    async def chain_id(self):
        return self._chain_id


def _ctx(rpc, amount=1000, chain_id=None):
    return Context(
        request=TradeRequest(token=TOKEN, quote=QUOTE, amount_usd=amount, direction=Direction.BUY),
        settings=Settings(chain_id=chain_id),
        rpc=rpc,
    )


async def test_chain_id_match():
    results = await ChainIdentityCheck().run(_ctx(FakeRpc(42161), chain_id=42161))
    assert results[0].severity is Severity.OK


async def test_chain_id_mismatch():
    results = await ChainIdentityCheck().run(_ctx(FakeRpc(1), chain_id=42161))
    assert results[0].severity is Severity.DANGER


async def test_chain_id_not_pinned():
    results = await ChainIdentityCheck().run(_ctx(FakeRpc(), chain_id=None))
    assert results[0].severity is Severity.INFO


async def test_size_small():
    results = await SizeVsDepthCheck().run(_ctx(FakeRpc(), amount=500))
    assert results[0].severity is Severity.OK


async def test_size_medium():
    results = await SizeVsDepthCheck().run(_ctx(FakeRpc(), amount=50_000))
    assert results[0].severity is Severity.INFO


async def test_size_large():
    results = await SizeVsDepthCheck().run(_ctx(FakeRpc(), amount=200_000))
    assert results[0].severity is Severity.WARN


async def test_sequencing_context():
    results = await SequencingContextCheck().run(_ctx(FakeRpc()))
    assert results[0].severity is Severity.INFO
    assert "fcfs" in results[0].title.lower()
