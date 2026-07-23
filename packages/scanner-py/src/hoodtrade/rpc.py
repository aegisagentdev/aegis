"""Minimal async JSON-RPC client + just-enough ABI encoding.

We deliberately avoid a heavy web3 dependency. The scanner only needs a handful of
constant, well-known function selectors and simple word-aligned encode/decode, so we
inline them. This keeps install light and the surface auditable.
"""

from __future__ import annotations

import httpx

# Precomputed 4-byte function selectors (keccak256(signature)[:4]). Constants so we
# don't pull in a keccak implementation just to hash fixed strings.
SELECTORS = {
    "name": "0x06fdde03",
    "symbol": "0x95d89b41",
    "decimals": "0x313ce567",
    "totalSupply": "0x18160ddd",
    "balanceOf": "0x70a08231",  # balanceOf(address)
    "owner": "0x8da5cb5b",  # owner()
    "getOwner": "0x893d20e8",  # getOwner()
    # Uniswap V3 pool
    "slot0": "0x3850c7bd",
    "liquidity": "0x1a686502",
    "token0": "0x0dfe1681",
    "token1": "0xd21220a7",
    "fee": "0xddca3f43",
}


class RpcError(RuntimeError):
    pass


def _addr_arg(address: str) -> str:
    """Left-pad a 20-byte address to a 32-byte ABI word (no 0x)."""
    a = address.lower().removeprefix("0x")
    if len(a) != 40:
        raise ValueError(f"not a 20-byte address: {address}")
    return a.rjust(64, "0")


def encode_call(fn: str, *args: str) -> str:
    """Encode a call to a zero- or single-address-arg function. That covers every
    read this scanner makes."""
    data = SELECTORS[fn]
    for a in args:
        data += _addr_arg(a)
    return data


class RpcClient:
    def __init__(self, url: str, timeout: float = 15.0):
        self._url = url
        self._client = httpx.AsyncClient(timeout=timeout)
        self._id = 0

    async def __aenter__(self) -> RpcClient:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self._client.aclose()

    async def _call(self, method: str, params: list) -> object:
        self._id += 1
        payload = {"jsonrpc": "2.0", "id": self._id, "method": method, "params": params}
        resp = await self._client.post(self._url, json=payload)
        resp.raise_for_status()
        body = resp.json()
        if "error" in body:
            raise RpcError(f"{method}: {body['error']}")
        return body["result"]

    async def chain_id(self) -> int:
        return int(await self._call("eth_chainId", []), 16)  # type: ignore[arg-type]

    async def get_code(self, address: str) -> bytes:
        result = await self._call("eth_getCode", [address, "latest"])
        return bytes.fromhex(str(result).removeprefix("0x"))

    async def eth_call(self, to: str, data: str) -> bytes:
        call_obj = {
            "to": to,
            "data": data,
            "from": "0x0000000000000000000000000000000000000000",
        }
        result = await self._call("eth_call", [call_obj, "latest"])
        return bytes.fromhex(str(result).removeprefix("0x"))


# --- decode helpers ---------------------------------------------------------


def decode_uint(raw: bytes) -> int:
    return int.from_bytes(raw[:32], "big") if raw else 0


def decode_address(raw: bytes) -> str:
    if not raw:
        return "0x" + "0" * 40
    return "0x" + raw[12:32].hex()


def decode_string(raw: bytes) -> str:
    """Decode an ABI dynamic string; tolerate bytes32-packed strings some tokens use."""
    if not raw:
        return ""
    if len(raw) >= 64:
        length = int.from_bytes(raw[32:64], "big")
        if 0 < length <= len(raw) - 64:
            return raw[64 : 64 + length].decode("utf-8", "replace")
    return raw.rstrip(b"\x00").decode("utf-8", "replace")
