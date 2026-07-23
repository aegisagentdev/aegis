import pytest

from aegis.validators import ValidationError, validate_address, validate_amount, validate_trade_request

VALID = "0x2222222222222222222222222222222222222222"
QUOTE = "0x3333333333333333333333333333333333333333"


def test_validate_address_ok():
    assert validate_address(VALID) == VALID.lower()


def test_validate_address_empty():
    with pytest.raises(ValidationError, match="required"):
        validate_address("")


def test_validate_address_invalid():
    with pytest.raises(ValidationError, match="Invalid"):
        validate_address("0xBAD")


def test_validate_amount_ok():
    assert validate_amount(100.0) == 100.0


def test_validate_amount_zero():
    with pytest.raises(ValidationError, match="positive"):
        validate_amount(0)


def test_validate_amount_negative():
    with pytest.raises(ValidationError, match="positive"):
        validate_amount(-50)


def test_validate_amount_too_large():
    with pytest.raises(ValidationError, match="sanity"):
        validate_amount(2_000_000_000)


def test_validate_trade_ok():
    validate_trade_request(VALID, QUOTE, 1000)


def test_validate_trade_same_token_quote():
    with pytest.raises(ValidationError, match="same"):
        validate_trade_request(VALID, VALID, 1000)


def test_validate_trade_with_pool():
    pool = "0x4444444444444444444444444444444444444444"
    validate_trade_request(VALID, QUOTE, 1000, pool=pool)


def test_validate_trade_bad_pool():
    with pytest.raises(ValidationError):
        validate_trade_request(VALID, QUOTE, 1000, pool="bad")
