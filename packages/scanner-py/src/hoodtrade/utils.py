"""Shared utility functions.

Small helpers used across modules — address validation, formatting, and
conversion. Kept in one place to avoid duplication.
"""

from __future__ import annotations

import re

_ADDR_RE = re.compile(r"^0x[0-9a-fA-F]{40}$")


def is_valid_address(address: str) -> bool:
    return bool(_ADDR_RE.match(address))


def normalize_address(address: str) -> str:
    if not is_valid_address(address):
        raise ValueError(f"Invalid Ethereum address: {address}")
    return address.lower()


def shorten_address(address: str, chars: int = 4) -> str:
    if len(address) < 10:
        return address
    return f"{address[: chars + 2]}...{address[-chars:]}"


def format_usd(amount: float) -> str:
    if amount >= 1_000_000:
        return f"${amount / 1_000_000:.1f}M"
    if amount >= 1_000:
        return f"${amount / 1_000:.1f}k"
    return f"${amount:.2f}"


def format_bps(bps: float) -> str:
    if bps >= 10_000:
        return f"{bps / 10_000:.1f}x"
    if bps >= 100:
        return f"{bps / 100:.1f}%"
    return f"{bps:.0f}bps"


def wei_to_ether(wei: int) -> float:
    return wei / 10**18


def ether_to_wei(ether: float) -> int:
    return int(ether * 10**18)
