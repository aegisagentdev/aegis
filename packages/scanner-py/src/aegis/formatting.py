"""Terminal formatting helpers for Rich output.

Shared formatting logic used by the CLI and potentially by other
consumer interfaces (Telegram bot, Discord bot).
"""

from __future__ import annotations

from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .models import ScanReport, Severity, Verdict

SEV_STYLE = {
    Severity.OK: "green",
    Severity.INFO: "cyan",
    Severity.WARN: "yellow",
    Severity.DANGER: "bold red",
}

VERDICT_STYLE = {
    Verdict.GO: "bold green",
    Verdict.CAUTION: "bold yellow",
    Verdict.NO_GO: "bold red",
    Verdict.UNKNOWN: "bold white",
}

VERDICT_EMOJI = {
    Verdict.GO: "[green]✓[/green]",
    Verdict.CAUTION: "[yellow]⚠[/yellow]",
    Verdict.NO_GO: "[red]✗[/red]",
    Verdict.UNKNOWN: "[white]?[/white]",
}


def verdict_panel(report: ScanReport) -> Panel:
    style = VERDICT_STYLE[report.verdict]
    head = Text(f" {report.verdict.value} ", style=f"reverse {style}")
    head.append(f"  risk score {report.score}", style=style)
    return Panel(head, title="Aegis verdict", border_style=style)


def findings_table(report: ScanReport) -> Table:
    table = Table(title="Findings", show_lines=False, expand=True)
    table.add_column("check", style="dim", no_wrap=True)
    table.add_column("sev", no_wrap=True)
    table.add_column("score", justify="right")
    table.add_column("finding")
    for r in report.results:
        table.add_row(
            r.check,
            Text(r.severity.value, style=SEV_STYLE[r.severity]),
            str(r.score),
            r.title,
        )
    return table


def summary_text(report: ScanReport) -> list[str]:
    lines = []
    if report.summary:
        s = report.summary
        lines.append(f"[bold]{s.headline}[/bold]\n")
        if s.key_risks:
            lines.append("[bold]Key risks[/bold]")
            for r in s.key_risks:
                lines.append(f"  • {r}")
        if s.what_to_check:
            lines.append("\n[bold]Verify yourself[/bold]")
            for r in s.what_to_check:
                lines.append(f"  → {r}")
    return lines
