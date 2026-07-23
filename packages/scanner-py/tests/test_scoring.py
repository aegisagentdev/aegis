from aegis.models import CheckResult, Severity
from aegis.scoring import (
    danger_count,
    normalize_score,
    passing_count,
    risk_level,
    score_breakdown,
    warn_count,
    weighted_score,
)


def _r(sev, score, check="X"):
    return CheckResult(check=check, severity=sev, score=score, title="t", detail="d")


def test_weighted_score():
    results = [_r(Severity.WARN, 10), _r(Severity.OK, 0)]
    assert weighted_score(results) == (10 * 3 + 0) / 2


def test_weighted_score_empty():
    assert weighted_score([]) == 0.0


def test_normalize_score():
    assert normalize_score(100, 200) == 0.5
    assert normalize_score(300, 200) == 1.0
    assert normalize_score(0, 200) == 0.0


def test_risk_level():
    assert risk_level(10) == "low"
    assert risk_level(30) == "medium"
    assert risk_level(80) == "high"


def test_danger_count():
    results = [_r(Severity.DANGER, 50), _r(Severity.WARN, 10), _r(Severity.DANGER, 60)]
    assert danger_count(results) == 2


def test_warn_count():
    results = [_r(Severity.WARN, 10), _r(Severity.WARN, 15), _r(Severity.OK, 0)]
    assert warn_count(results) == 2


def test_passing_count():
    results = [_r(Severity.OK, 0), _r(Severity.WARN, 10), _r(Severity.OK, 0)]
    assert passing_count(results) == 2


def test_score_breakdown():
    results = [
        _r(Severity.WARN, 10, "CONTRACT-OWNER"),
        _r(Severity.WARN, 15, "CONTRACT-SUPPLY"),
        _r(Severity.DANGER, 50, "POOL-LIQUIDITY"),
    ]
    bd = score_breakdown(results)
    assert bd["CONTRACT"] == 25
    assert bd["POOL"] == 50
