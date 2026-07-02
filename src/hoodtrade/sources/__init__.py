"""External data sources that enrich the on-chain check battery.

Each source is optional: if it is unreachable or has no data for a token, the
scanner degrades gracefully and relies on the deterministic on-chain checks. No
source can override the verdict — they only contribute findings and evidence.
"""

from __future__ import annotations

from .dexscreener import DexScreenerClient, MarketData, fetch_market
from .goplus import GoPlusClient, GoPlusReport, fetch_goplus

__all__ = [
    "GoPlusClient",
    "GoPlusReport",
    "fetch_goplus",
    "DexScreenerClient",
    "MarketData",
    "fetch_market",
]
