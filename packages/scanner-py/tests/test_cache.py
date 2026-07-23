from hoodtrade.cache import CachedRpcClient


class MockInnerRpc:
    def __init__(self):
        self.call_count = 0

    async def chain_id(self):
        self.call_count += 1
        return 42

    async def get_code(self, address):
        self.call_count += 1
        return b"\x60" * 10

    async def eth_call(self, to, data):
        self.call_count += 1
        return b"\x00" * 32

    async def _call(self, method, params):
        self.call_count += 1
        return "0x" + "0" * 64

    async def aclose(self):
        pass


async def test_chain_id_cached():
    inner = MockInnerRpc()
    cached = CachedRpcClient(inner)
    assert await cached.chain_id() == 42
    assert await cached.chain_id() == 42
    assert inner.call_count == 1
    assert cached.stats["hits"] == 1
    assert cached.stats["misses"] == 1


async def test_get_code_cached():
    inner = MockInnerRpc()
    cached = CachedRpcClient(inner)
    addr = "0x1111111111111111111111111111111111111111"
    r1 = await cached.get_code(addr)
    r2 = await cached.get_code(addr)
    assert r1 == r2
    assert inner.call_count == 1


async def test_eth_call_cached():
    inner = MockInnerRpc()
    cached = CachedRpcClient(inner)
    r1 = await cached.eth_call("0xABC", "0x12345678")
    r2 = await cached.eth_call("0xABC", "0x12345678")
    assert r1 == r2
    assert inner.call_count == 1


async def test_different_calls_not_cached():
    inner = MockInnerRpc()
    cached = CachedRpcClient(inner)
    await cached.eth_call("0xABC", "0x11111111")
    await cached.eth_call("0xABC", "0x22222222")
    assert inner.call_count == 2


async def test_clear():
    inner = MockInnerRpc()
    cached = CachedRpcClient(inner)
    await cached.chain_id()
    cached.clear()
    await cached.chain_id()
    assert inner.call_count == 2
