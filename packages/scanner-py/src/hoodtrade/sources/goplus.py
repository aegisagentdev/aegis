"""GoPlus Security token-security API client.

GoPlus (https://gopluslabs.io) exposes a free, keyless token-security endpoint
that returns honeypot / tax / permission flags for a contract on a given EVM
chain. We use it as a *second opinion* alongside our own on-chain simulations:
where our honeypot check runs a live eth_call, GoPlus aggregates crowd- and
scan-sourced signals. Disagreement between the two is itself useful signal.

The endpoint is chain-scoped by numeric chain id in the URL path and returns a
map keyed by the lowercased contract address. Numeric fields arrive as strings
("0", "0.05"); booleans arrive as "0"/"1" strings — we normalize both here so
the rest of the codebase sees real ints/floats/bools.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import httpx

BASE_URL = "https://api.gopluslabs.io/api/v1/token_security"

# GoPlus keys its chains by EVM chain id. This is the subset we surface; any
# integer chain id is still accepted and passed through.
SUPPORTED_CHAINS = {
    1: "Ethereum",
    10: "Optimism",
    56: "BNB Chain",
    137: "Polygon",
    8453: "Base",
    42161: "Arbitrum",
    43114: "Avalanche",
}


def _as_bool(value: object) -> bool | None:
    """GoPlus booleans are "0"/"1" strings; missing keys mean "unknown"."""
    if value in (None, ""):
        return None
    return str(value) == "1"


def _as_float(value: object) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(str(value))
    except (TypeError, ValueError):
        return None


def _as_int(value: object) -> int | None:
    f = _as_float(value)
    return int(f) if f is not None else None


@dataclass
class GoPlusReport:
    """Normalized subset of the GoPlus token_security response."""

    address: str
    chain_id: int
    token_name: str | None = None
    token_symbol: str | None = None
    is_honeypot: bool | None = None
    buy_tax: float | None = None
    sell_tax: float | None = None
    is_open_source: bool | None = None
    is_proxy: bool | None = None
    is_mintable: bool | None = None
    transfer_pausable: bool | None = None
    can_take_back_ownership: bool | None = None
    owner_change_balance: bool | None = None
    hidden_owner: bool | None = None
    is_blacklisted: bool | None = None
    owner_address: str | None = None
    holder_count: int | None = None
    total_supply: float | None = None
    raw: dict = field(default_factory=dict, repr=False)

    @property
    def chain_name(self) -> str:
        return SUPPORTED_CHAINS.get(self.chain_id, f"chain {self.chain_id}")

    @classmethod
    def from_api(cls, address: str, chain_id: int, data: dict) -> GoPlusReport:
        return cls(
            address=address,
            chain_id=chain_id,
            token_name=data.get("token_name") or None,
            token_symbol=data.get("token_symbol") or None,
            is_honeypot=_as_bool(data.get("is_honeypot")),
            buy_tax=_as_float(data.get("buy_tax")),
            sell_tax=_as_float(data.get("sell_tax")),
            is_open_source=_as_bool(data.get("is_open_source")),
            is_proxy=_as_bool(data.get("is_proxy")),
            is_mintable=_as_bool(data.get("is_mintable")),
            transfer_pausable=_as_bool(data.get("transfer_pausable")),
            can_take_back_ownership=_as_bool(data.get("can_take_back_ownership")),
            owner_change_balance=_as_bool(data.get("owner_change_balance")),
            hidden_owner=_as_bool(data.get("hidden_owner")),
            is_blacklisted=_as_bool(data.get("is_blacklisted")),
            owner_address=data.get("owner_address") or None,
            holder_count=_as_int(data.get("holder_count")),
            total_supply=_as_float(data.get("total_supply")),
            raw=data,
        )


class GoPlusError(RuntimeError):
    pass


class GoPlusClient:
    def __init__(self, timeout: float = 15.0, base_url: str = BASE_URL):
        self._base = base_url
        self._client = httpx.AsyncClient(timeout=timeout)

    async def __aenter__(self) -> GoPlusClient:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self._client.aclose()

    async def token_security(self, chain_id: int, address: str) -> GoPlusReport | None:
        """Return the security report for ``address`` on ``chain_id``.

        Returns ``None`` when GoPlus has no record for the token (a valid answer
        for a brand-new contract). Raises GoPlusError on transport/API failure so
        the engine can record it as a note without aborting the scan.
        """
        url = f"{self._base}/{chain_id}"
        try:
            resp = await self._client.get(url, params={"contract_addresses": address})
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise GoPlusError(f"GoPlus request failed: {exc}") from exc

        body = resp.json()
        if body.get("code") != 1:
            raise GoPlusError(f"GoPlus API error: {body.get('message', 'unknown')}")

        result = body.get("result") or {}
        entry = result.get(address.lower())
        if not entry:
            return None
        return GoPlusReport.from_api(address, chain_id, entry)


async def fetch_goplus(chain_id: int, address: str, timeout: float = 15.0) -> GoPlusReport | None:
    """Convenience one-shot fetch used by the engine."""
    async with GoPlusClient(timeout=timeout) as client:
        return await client.token_security(chain_id, address)
