"""RPC response caching layer.

Wraps RpcClient to cache repeated calls within a single scan. On-chain
state doesn't change between checks in the same scan (they run in <1s),
so caching avoids redundant RPC round-trips.
"""

from __future__ import annotations

from .rpc import RpcClient


class CachedRpcClient:
    """Transparent caching wrapper around RpcClient."""

    def __init__(self, inner: RpcClient):
        self._inner = inner
        self._code_cache: dict[str, bytes] = {}
        self._call_cache: dict[tuple[str, str], bytes] = {}
        self._chain_id: int | None = None
        self.stats = {"hits": 0, "misses": 0}

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        await self._inner.aclose()

    async def aclose(self):
        await self._inner.aclose()

    async def chain_id(self) -> int:
        if self._chain_id is None:
            self._chain_id = await self._inner.chain_id()
            self.stats["misses"] += 1
        else:
            self.stats["hits"] += 1
        return self._chain_id

    async def get_code(self, address: str) -> bytes:
        key = address.lower()
        if key not in self._code_cache:
            self._code_cache[key] = await self._inner.get_code(address)
            self.stats["misses"] += 1
        else:
            self.stats["hits"] += 1
        return self._code_cache[key]

    async def eth_call(self, to: str, data: str) -> bytes:
        key = (to.lower(), data)
        if key not in self._call_cache:
            self._call_cache[key] = await self._inner.eth_call(to, data)
            self.stats["misses"] += 1
        else:
            self.stats["hits"] += 1
        return self._call_cache[key]

    async def _call(self, method: str, params: list) -> object:
        return await self._inner._call(method, params)

    def clear(self) -> None:
        self._code_cache.clear()
        self._call_cache.clear()
        self._chain_id = None
        self.stats = {"hits": 0, "misses": 0}
