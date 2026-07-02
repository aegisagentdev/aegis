"""DexScreener market-data source.

DexScreener (https://dexscreener.com) indexes DEX pairs across many chains —
including Robinhood Chain (chain slug ``robinhood``) — and exposes a free,
keyless JSON API. Where GoPlus tells us about the *contract*, DexScreener tells
us about the *market*: real price, pooled liquidity, 24h volume, and buy/sell
counts. That is exactly the depth/liquidity context the execution checks need,
sourced from live trading rather than a single pool read.

We pick the deepest pair (max USD liquidity) for a token, since that is the one
a trade would realistically route through.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import httpx

BASE_URL = "https://api.dexscreener.com"

# DexScreener chain slugs for the chains hoodtrade targets. Robinhood Chain is
# the headline one; the EVM majors are here so the same source works with the
# GoPlus-backed multichain scan.
CHAIN_SLUGS = {
    "robinhood": "robinhood",
    "ethereum": "ethereum",
    "base": "base",
    "arbitrum": "arbitrum",
    "bsc": "bsc",
    "polygon": "polygon",
    "optimism": "optimism",
    "avalanche": "avalanche",
}


@dataclass
class MarketData:
    """The deepest DEX pair for a token, normalized."""

    chain: str
    token_address: str
    symbol: str | None = None
    name: str | None = None
    dex: str | None = None
    pair_address: str | None = None
    quote_symbol: str | None = None
    price_usd: float | None = None
    liquidity_usd: float | None = None
    volume_24h: float | None = None
    fdv: float | None = None
    buys_24h: int | None = None
    sells_24h: int | None = None
    pair_count: int = 0
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_pairs(cls, chain: str, token_address: str, pairs: list[dict]) -> MarketData | None:
        if not pairs:
            return None
        # Deepest pair = the one a trade would route through.
        best = max(pairs, key=lambda p: (p.get("liquidity") or {}).get("usd") or 0.0)
        base = best.get("baseToken") or {}
        quote = best.get("quoteToken") or {}
        txns = (best.get("txns") or {}).get("h24") or {}
        return cls(
            chain=chain,
            token_address=token_address,
            symbol=base.get("symbol"),
            name=base.get("name"),
            dex=best.get("dexId"),
            pair_address=best.get("pairAddress"),
            quote_symbol=quote.get("symbol"),
            price_usd=_f(best.get("priceUsd")),
            liquidity_usd=_f((best.get("liquidity") or {}).get("usd")),
            volume_24h=_f((best.get("volume") or {}).get("h24")),
            fdv=_f(best.get("fdv")),
            buys_24h=_i(txns.get("buys")),
            sells_24h=_i(txns.get("sells")),
            pair_count=len(pairs),
            raw=best,
        )


def _f(value: object) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


def _i(value: object) -> int | None:
    f = _f(value)
    return int(f) if f is not None else None


class DexScreenerError(RuntimeError):
    pass


class DexScreenerClient:
    def __init__(self, timeout: float = 15.0, base_url: str = BASE_URL):
        self._base = base_url
        self._client = httpx.AsyncClient(timeout=timeout)

    async def __aenter__(self) -> DexScreenerClient:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self._client.aclose()

    async def market(self, chain: str, token_address: str) -> MarketData | None:
        """Return the deepest pair for ``token_address`` on ``chain``.

        Returns ``None`` when the token has no indexed pairs (untraded / brand
        new). Raises DexScreenerError on transport failure so the engine records
        it as a note without aborting.
        """
        slug = CHAIN_SLUGS.get(chain.lower(), chain.lower())
        url = f"{self._base}/tokens/v1/{slug}/{token_address}"
        try:
            resp = await self._client.get(url)
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise DexScreenerError(f"DexScreener request failed: {exc}") from exc

        body = resp.json()
        pairs = body if isinstance(body, list) else body.get("pairs") or []
        return MarketData.from_pairs(chain, token_address, pairs)


async def fetch_market(chain: str, token_address: str, timeout: float = 15.0) -> MarketData | None:
    """Convenience one-shot fetch used by the engine."""
    async with DexScreenerClient(timeout=timeout) as client:
        return await client.market(chain, token_address)
