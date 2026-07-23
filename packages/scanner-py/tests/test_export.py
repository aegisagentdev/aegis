import json

from hoodtrade.export import severity_counts, to_csv, to_dict, to_json, to_markdown
from hoodtrade.models import CheckResult, RiskSummary, ScanReport, Severity, TradeRequest, Verdict

TOKEN = "0x" + "2" * 40
QUOTE = "0x" + "3" * 40


def _report() -> ScanReport:
    return ScanReport(
        request=TradeRequest(token=TOKEN, quote=QUOTE, amount_usd=5000),
        verdict=Verdict.CAUTION,
        score=30,
        results=[
            CheckResult(check="A", severity=Severity.WARN, score=15, title="warn one", detail="d1"),
            CheckResult(check="B", severity=Severity.OK, score=0, title="ok one", detail="d2"),
            CheckResult(check="C", severity=Severity.INFO, score=5, title="info one", detail="d3"),
            CheckResult(check="D", severity=Severity.WARN, score=10, title="warn two", detail="d4"),
        ],
        summary=RiskSummary(
            headline="Test headline",
            key_risks=["risk one", "risk two"],
            what_to_check=["check this"],
        ),
    )


def test_to_json():
    data = json.loads(to_json(_report()))
    assert data["verdict"] == "CAUTION"
    assert data["score"] == 30
    assert len(data["results"]) == 4


def test_to_dict():
    d = to_dict(_report())
    assert isinstance(d, dict)
    assert d["verdict"] == "CAUTION"


def test_to_csv():
    csv_str = to_csv(_report())
    lines = csv_str.strip().split("\n")
    assert len(lines) == 5  # header + 4 results
    assert "check,severity,score,title,detail" in lines[0]


def test_to_markdown():
    md = to_markdown(_report())
    assert "# Hood Trade Scan Report" in md
    assert "CAUTION" in md
    assert "| `A` |" in md
    assert "risk one" in md
    assert "check this" in md


def test_to_markdown_no_summary():
    report = _report()
    report.summary = None
    md = to_markdown(report)
    assert "Findings" in md


def test_severity_counts():
    counts = severity_counts(_report())
    assert counts["warn"] == 2
    assert counts["ok"] == 1
    assert counts["info"] == 1
    assert counts["danger"] == 0
