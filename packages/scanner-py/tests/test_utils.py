import pytest

from hoodtrade.utils import (
    ether_to_wei,
    format_bps,
    format_usd,
    is_valid_address,
    normalize_address,
    shorten_address,
    wei_to_ether,
)

VALID = "0x2222222222222222222222222222222222222222"


def test_valid_address():
    assert is_valid_address(VALID)
    assert is_valid_address("0xaAbBcCdDeEfF00112233445566778899aAbBcCdD")


def test_invalid_addresses():
    assert not is_valid_address("")
    assert not is_valid_address("0x123")
    assert not is_valid_address("not_an_address")
    assert not is_valid_address("2222222222222222222222222222222222222222")


def test_normalize():
    assert normalize_address(VALID) == VALID.lower()


def test_normalize_rejects_invalid():
    with pytest.raises(ValueError):
        normalize_address("bad")


def test_shorten():
    assert shorten_address(VALID) == "0x2222...2222"
    assert shorten_address(VALID, 6) == "0x222222...222222"


def test_format_usd():
    assert format_usd(500) == "$500.00"
    assert format_usd(5_000) == "$5.0k"
    assert format_usd(2_500_000) == "$2.5M"


def test_format_bps():
    assert format_bps(50) == "50bps"
    assert format_bps(250) == "2.5%"
    assert format_bps(15_000) == "1.5x"


def test_wei_ether_conversion():
    assert wei_to_ether(10**18) == 1.0
    assert ether_to_wei(1.0) == 10**18
    assert wei_to_ether(0) == 0.0
