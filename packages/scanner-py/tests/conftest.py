"""Shared test fixtures for Aegis test suite."""

from __future__ import annotations

import pytest

from aegis.checks.base import Context
from aegis.config import Settings
from aegis.models import Direction, TradeRequest

TOKEN = "0x2222222222222222222222222222222222222222"
QUOTE = "0x3333333333333333333333333333333333333333"
POOL = "0x4444444444444444444444444444444444444444"


class StubRpc:
    """Configurable RPC stub for testing."""

    def __init__(
        self,
        code: dict[str, bytes] | None = None,
        calls: dict[str, bytes] | None = None,
        chain_id_val: int = 1,
    ):
        self._code = code or {}
        self._calls = calls or {}
        self._chain_id = chain_id_val

    async def get_code(self, address: str) -> bytes:
        return self._code.get(address.lower(), b"")

    async def eth_call(self, to: str, data: str) -> bytes:
        return self._calls.get(data, b"\x00" * 32)

    async def chain_id(self) -> int:
        return self._chain_id


@pytest.fixture
def stub_rpc():
    return StubRpc


@pytest.fixture
def default_request():
    return TradeRequest(
        token=TOKEN,
        quote=QUOTE,
        amount_usd=1000,
        direction=Direction.BUY,
    )


@pytest.fixture
def default_settings():
    return Settings()


@pytest.fixture
def make_context(default_request, default_settings):
    def _make(rpc, request=None, settings=None, cache=None):
        ctx = Context(
            request=request or default_request,
            settings=settings or default_settings,
            rpc=rpc,
        )
        if cache:
            ctx.cache.update(cache)
        return ctx

    return _make
