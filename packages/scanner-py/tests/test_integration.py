"""Integration tests — end-to-end verdict logic with StubRpc."""

import pytest

from aegis.checks import default_checks
from aegis.engine import decide
from aegis.models import CheckResult, Direction, Severity, TradeRequest, Verdict


@pytest.fixture
def trade_request():
    return TradeRequest(
        token="0x" + "ab" * 20,
        quote="0x" + "cd" * 20,
        amount_usd=100.0,
        direction=Direction.BUY,
    )


def test_go_verdict_on_clean_results(default_settings):
    results = [
        CheckResult(check="test", title="ok", severity=Severity.OK, score=0, detail="fine"),
    ]
    verdict = decide(0, results, default_settings)
    assert verdict == Verdict.GO


def test_nogo_on_danger_finding(default_settings):
    results = [
        CheckResult(check="test", title="bad", severity=Severity.DANGER, score=30, detail="fail"),
    ]
    verdict = decide(30, results, default_settings)
    assert verdict == Verdict.NO_GO


def test_caution_on_moderate_score(default_settings):
    results = [
        CheckResult(check="test", title="warn", severity=Severity.WARN, score=30, detail="hmm"),
    ]
    verdict = decide(30, results, default_settings)
    assert verdict == Verdict.CAUTION


def test_nogo_on_high_score(default_settings):
    results = [
        CheckResult(check="test", title="warn", severity=Severity.WARN, score=70, detail="bad"),
    ]
    verdict = decide(70, results, default_settings)
    assert verdict == Verdict.NO_GO


def test_checks_list_is_nonempty():
    checks = default_checks()
    assert len(checks) >= 10
