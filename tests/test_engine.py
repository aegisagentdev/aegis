from kabuto.config import Settings
from kabuto.engine import decide
from kabuto.models import CheckResult, Severity, Verdict


def _r(sev: Severity, score: int) -> CheckResult:
    return CheckResult(check="X", severity=sev, score=score, title="t", detail="d")


def test_danger_forces_nogo_regardless_of_score():
    settings = Settings()
    results = [_r(Severity.DANGER, 5)]
    assert decide(5, results, settings) is Verdict.NO_GO


def test_score_bands():
    settings = Settings(caution_score=25, nogo_score=60)
    assert decide(0, [_r(Severity.OK, 0)], settings) is Verdict.GO
    assert decide(30, [_r(Severity.WARN, 30)], settings) is Verdict.CAUTION
    assert decide(65, [_r(Severity.WARN, 65)], settings) is Verdict.NO_GO


def test_boundary_is_inclusive():
    settings = Settings(caution_score=25, nogo_score=60)
    assert decide(25, [_r(Severity.WARN, 25)], settings) is Verdict.CAUTION
    assert decide(60, [_r(Severity.WARN, 60)], settings) is Verdict.NO_GO
