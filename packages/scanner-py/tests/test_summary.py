from hoodtrade.ai import _template_summary, summarize
from hoodtrade.config import Settings
from hoodtrade.models import CheckResult, ScanReport, Severity, TradeRequest, Verdict


def _report(verdict: Verdict, results) -> ScanReport:
    return ScanReport(
        request=TradeRequest(token="0x" + "2" * 40, quote="0x" + "3" * 40, amount_usd=500),
        verdict=verdict,
        score=sum(r.score for r in results),
        results=results,
    )


def test_template_summary_orders_danger_first():
    results = [
        CheckResult(check="A", severity=Severity.WARN, score=10, title="warn thing", detail="d"),
        CheckResult(check="B", severity=Severity.DANGER, score=100, title="danger thing", detail="d"),
    ]
    summary = _template_summary(_report(Verdict.NO_GO, results))
    assert "danger thing" in summary.key_risks[0]
    assert summary.what_to_check


def test_summarize_falls_back_when_ai_disabled():
    results = [CheckResult(check="A", severity=Severity.OK, score=0, title="fine", detail="d")]
    settings = Settings(ai_enabled=False)
    summary = summarize(_report(Verdict.GO, results), settings)
    assert summary.headline
