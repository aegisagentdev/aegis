"""Report export formats.

Converts a ScanReport into various output formats for integration with
external tools, dashboards, and CI pipelines.
"""

from __future__ import annotations

import csv
import io

from .models import ScanReport, Severity


def to_json(report: ScanReport, indent: int = 2) -> str:
    return report.model_dump_json(indent=indent)


def to_dict(report: ScanReport) -> dict:
    return report.model_dump(mode="json")


def to_csv(report: ScanReport) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["check", "severity", "score", "title", "detail"])
    for r in report.results:
        writer.writerow([r.check, r.severity.value, r.score, r.title, r.detail])
    return output.getvalue()


def to_markdown(report: ScanReport) -> str:
    lines = [
        "# Aegis Scan Report",
        "",
        f"**Verdict**: {report.verdict.value}  ",
        f"**Risk Score**: {report.score}  ",
        f"**Token**: `{report.request.token}`  ",
        f"**Quote**: `{report.request.quote}`  ",
        f"**Amount**: ${report.request.amount_usd:,.2f}  ",
        f"**Direction**: {report.request.direction.value}  ",
        "",
    ]

    if report.summary:
        lines.extend(
            [
                "## Summary",
                "",
                report.summary.headline,
                "",
            ]
        )
        if report.summary.key_risks:
            lines.append("### Key Risks")
            lines.append("")
            for risk in report.summary.key_risks:
                lines.append(f"- {risk}")
            lines.append("")
        if report.summary.what_to_check:
            lines.append("### Verify")
            lines.append("")
            for item in report.summary.what_to_check:
                lines.append(f"- {item}")
            lines.append("")

    lines.extend(
        [
            "## Findings",
            "",
            "| Check | Severity | Score | Finding |",
            "|-------|----------|-------|---------|",
        ]
    )
    for r in report.results:
        sev_icon = {"ok": "✅", "info": "ℹ️", "warn": "⚠️", "danger": "🚫"}.get(r.severity.value, "")
        lines.append(f"| `{r.check}` | {sev_icon} {r.severity.value} | {r.score} | {r.title} |")

    if report.notes:
        lines.extend(["", "## Notes", ""])
        for note in report.notes:
            lines.append(f"- {note}")

    lines.append("")
    return "\n".join(lines)


def severity_counts(report: ScanReport) -> dict[str, int]:
    counts = {s.value: 0 for s in Severity}
    for r in report.results:
        counts[r.severity.value] += 1
    return counts
