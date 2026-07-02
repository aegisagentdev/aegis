"""Verify type aliases resolve correctly."""

from hoodtrade.types import Address, BasisPoints, ChainId, HexData, RiskScore, Wei


def test_type_aliases_exist():
    addr: Address = "0x1234"
    data: HexData = "0xabcd"
    wei: Wei = 10**18
    cid: ChainId = 42161
    bps: BasisPoints = 150
    score: RiskScore = 42
    assert isinstance(addr, str)
    assert isinstance(data, str)
    assert isinstance(wei, int)
    assert isinstance(cid, int)
    assert isinstance(bps, int)
    assert isinstance(score, int)
