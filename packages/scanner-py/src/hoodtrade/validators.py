"""Input validation for trade requests and configuration.

Validates user inputs before they reach the check battery. Catches
obvious mistakes (invalid addresses, nonsensical amounts) early so
checks don't waste RPC calls on garbage inputs.
"""

from __future__ import annotations

from .utils import is_valid_address


class ValidationError(ValueError):
    pass


def validate_address(address: str, label: str = "address") -> str:
    if not address:
        raise ValidationError(f"{label} is required")
    if not is_valid_address(address):
        raise ValidationError(f"Invalid {label}: {address!r} — expected 0x-prefixed 40-hex-char string")
    return address.lower()


def validate_amount(amount: float) -> float:
    if amount <= 0:
        raise ValidationError(f"Amount must be positive, got {amount}")
    if amount > 1_000_000_000:
        raise ValidationError(f"Amount ${amount:,.0f} exceeds sanity limit ($1B)")
    return amount


def validate_trade_request(token: str, quote: str, amount: float, pool: str | None = None) -> None:
    validate_address(token, "token")
    validate_address(quote, "quote")
    validate_amount(amount)
    if pool is not None:
        validate_address(pool, "pool")
    if token.lower() == quote.lower():
        raise ValidationError("Token and quote addresses are the same")
