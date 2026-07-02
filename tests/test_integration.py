"""Integration tests — end-to-end scan with StubRpc."""

import pytest

from hoodtrade.checks import default_checks
from hoodtrade.engine import decide, run_scan
from hoodtrade.models import Direction, TradeRequest, Verdict


@pytest.fixture
def trade_request():
    return TradeRequest(
        token="0x" + "ab" * 20,
        quote="0x" + "cd" * 20,
        amount_usd=100.0,
        direction=Direction.BUY,
    )


def test_full_scan_returns_report(trade_request, default_settings, make_context):
    ctx = make_context(trade_request)
    checks = default_checks()
    results = run_scan(checks, ctx)
    assert len(results) == len(checks)


def test_decide_returns_verdict(trade_request, default_settings, make_context):
    ctx = make_context(trade_request)
    checks = default_checks()
    results = run_scan(checks, ctx)
    verdict = decide(results, default_settings)
    assert verdict in (Verdict.GO, Verdict.CAUTION, Verdict.NOGO)


def test_no_contract_gives_nogo(trade_request, default_settings, make_context):
    ctx = make_context(trade_request, code="0x")
    checks = default_checks()
    results = run_scan(checks, ctx)
    verdict = decide(results, default_settings)
    assert verdict == Verdict.NOGO


def test_healthy_token_gives_go(trade_request, default_settings, make_context):
    ctx = make_context(
        trade_request,
        code="0x6080",
        total_supply=10**24,
        balance=10**20,
    )
    checks = default_checks()
    results = run_scan(checks, ctx)
    verdict = decide(results, default_settings)
    assert verdict == Verdict.GO
