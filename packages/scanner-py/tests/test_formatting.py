from hoodtrade.formatting import findings_table, summary_text, verdict_panel
from hoodtrade.models import CheckResult, RiskSummary, ScanReport, Severity, TradeRequest, Verdict


def _report():
    return ScanReport(
        request=TradeRequest(token="0x" + "2" * 40, quote="0x" + "3" * 40, amount_usd=1000),
        verdict=Verdict.CAUTION,
        score=30,
        results=[
            CheckResult(check="A", severity=Severity.WARN, score=15, title="warn", detail="d"),
            CheckResult(check="B", severity=Severity.OK, score=0, title="ok", detail="d"),
        ],
        summary=RiskSummary(
            headline="Test headline",
            key_risks=["risk one"],
            what_to_check=["check this"],
        ),
    )


def test_verdict_panel():
    panel = verdict_panel(_report())
    assert panel.title == "Hood Trade verdict"


def test_findings_table():
    table = findings_table(_report())
    assert table.title == "Findings"
    assert len(table.rows) == 2


def test_summary_text():
    lines = summary_text(_report())
    assert any("Test headline" in line for line in lines)
    assert any("risk one" in line for line in lines)
    assert any("check this" in line for line in lines)


def test_summary_text_no_summary():
    report = _report()
    report.summary = None
    assert summary_text(report) == []
