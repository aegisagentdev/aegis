"""Tests for the GoPlus source client and response normalization."""

import httpx
import pytest

from hoodtrade.sources.goplus import (
    SUPPORTED_CHAINS,
    GoPlusClient,
    GoPlusError,
    GoPlusReport,
    _as_bool,
    _as_float,
    _as_int,
)

SAMPLE = {
    "token_name": "Tether USD",
    "token_symbol": "USDT",
    "is_honeypot": "0",
    "buy_tax": "0",
    "sell_tax": "0.05",
    "is_open_source": "1",
    "is_proxy": "0",
    "is_mintable": "1",
    "transfer_pausable": "1",
    "can_take_back_ownership": "0",
    "owner_change_balance": "1",
    "hidden_owner": "",
    "is_blacklisted": "1",
    "owner_address": "0xc6cde7c39eb2f0f0095f41570af89efc2c1ea828",
    "holder_count": "15313409",
    "total_supply": "97062996230.909656",
}


def test_coercion_helpers():
    assert _as_bool("1") is True
    assert _as_bool("0") is False
    assert _as_bool("") is None
    assert _as_bool(None) is None
    assert _as_float("0.05") == 0.05
    assert _as_float("") is None
    assert _as_float("nope") is None
    assert _as_int("42") == 42
    assert _as_int("") is None


def test_from_api_normalizes_types():
    rep = GoPlusReport.from_api("0xABC", 1, SAMPLE)
    assert rep.token_symbol == "USDT"
    assert rep.is_honeypot is False
    assert rep.sell_tax == 0.05
    assert rep.buy_tax == 0.0
    assert rep.is_mintable is True
    assert rep.transfer_pausable is True
    assert rep.owner_change_balance is True
    assert rep.can_take_back_ownership is False
    assert rep.hidden_owner is None  # empty string -> unknown
    assert rep.is_blacklisted is True
    assert rep.holder_count == 15313409
    assert rep.total_supply == pytest.approx(97062996230.909656)


def test_chain_name():
    rep = GoPlusReport.from_api("0xABC", 8453, {})
    assert rep.chain_name == "Base"
    rep2 = GoPlusReport.from_api("0xABC", 999999, {})
    assert "999999" in rep2.chain_name


def test_supported_chains_have_ethereum_and_base():
    assert SUPPORTED_CHAINS[1] == "Ethereum"
    assert SUPPORTED_CHAINS[8453] == "Base"


@pytest.mark.asyncio
async def test_token_security_parses_ok():
    addr = "0xdac17f958d2ee523a2206206994597c13d831ec7"

    def handler(request: httpx.Request) -> httpx.Response:
        assert "/1" in str(request.url)
        return httpx.Response(200, json={"code": 1, "message": "OK", "result": {addr: SAMPLE}})

    transport = httpx.MockTransport(handler)
    client = GoPlusClient()
    client._client = httpx.AsyncClient(transport=transport)
    rep = await client.token_security(1, addr)
    await client.aclose()
    assert rep is not None
    assert rep.token_symbol == "USDT"
    assert rep.sell_tax == 0.05


@pytest.mark.asyncio
async def test_token_security_none_when_no_entry():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"code": 1, "message": "OK", "result": {}})

    client = GoPlusClient()
    client._client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    rep = await client.token_security(1, "0xabc")
    await client.aclose()
    assert rep is None


@pytest.mark.asyncio
async def test_token_security_raises_on_api_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"code": 0, "message": "rate limited", "result": {}})

    client = GoPlusClient()
    client._client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    with pytest.raises(GoPlusError):
        await client.token_security(1, "0xabc")
    await client.aclose()
