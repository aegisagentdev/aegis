"""Chain and protocol constants for Robinhood Chain.

Centralized reference for well-known addresses, protocol parameters, and
chain-specific values. These are sourced from public documentation and
verified against on-chain state.
"""

from __future__ import annotations

# Well-known addresses on Robinhood Chain
ZERO_ADDRESS = "0x" + "0" * 40
DEAD_ADDRESS = "0x000000000000000000000000000000000000dEaD"

# Common token addresses (placeholders — updated as official addresses are published)
WETH = "0x" + "0" * 40  # Wrapped ETH on Robinhood Chain
USDG = "0x" + "0" * 40  # USDG stablecoin

# Uniswap V3 factory and router (deployed on Robinhood Chain)
UNISWAP_V3_FACTORY = "0x" + "0" * 40  # to be updated
UNISWAP_V3_ROUTER = "0x" + "0" * 40  # to be updated

# Known AMM venues on Robinhood Chain
VENUES = {
    "uniswap": "Uniswap V3 — primary public AMM",
    "pleiades": "Pleiades — proprietary AMM with custom curves",
    "arcus": "dYdX Arcus — perpetuals and spot DEX",
    "0x": "0x Protocol — RFQ liquidity and aggregation",
    "morpho": "Morpho — lending protocol (Earn ~7% USDG)",
}

# Risk score thresholds (defaults, overridable via config)
DEFAULT_CAUTION_SCORE = 25
DEFAULT_NOGO_SCORE = 60

# Trade size bands for execution quality assessment
SIZE_BANDS = {
    "small": (0, 10_000),
    "medium": (10_000, 100_000),
    "large": (100_000, float("inf")),
}

# ERC-20 function selectors (duplicated from rpc.py for reference)
ERC20_SELECTORS = {
    "name": "0x06fdde03",
    "symbol": "0x95d89b41",
    "decimals": "0x313ce567",
    "totalSupply": "0x18160ddd",
    "balanceOf": "0x70a08231",
    "transfer": "0xa9059cbb",
    "approve": "0x095ea7b3",
    "allowance": "0xdd62ed3e",
    "transferFrom": "0x23b872dd",
}

# Severity display configuration
SEVERITY_COLORS = {
    "ok": "green",
    "info": "cyan",
    "warn": "yellow",
    "danger": "red",
}

VERDICT_COLORS = {
    "GO": "green",
    "CAUTION": "yellow",
    "NO": "red",
    "UNKNOWN": "white",
}
