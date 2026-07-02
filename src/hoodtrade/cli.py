"""hoodtrade command-line interface."""

from __future__ import annotations

import asyncio

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from . import __version__
from .ai import summarize
from .config import load_settings
from .engine import run_scan
from .models import Direction, ScanReport, Severity, TradeRequest, Verdict
from .rpc import RpcClient

app = typer.Typer(add_completion=False, help="Pre-trade safety scanner for Robinhood Chain.")
console = Console()

_SEV_STYLE = {
    Severity.OK: "green",
    Severity.INFO: "cyan",
    Severity.WARN: "yellow",
    Severity.DANGER: "bold red",
}
_VERDICT_STYLE = {
    Verdict.GO: "bold green",
    Verdict.CAUTION: "bold yellow",
    Verdict.NO_GO: "bold red",
    Verdict.UNKNOWN: "bold white",
}


def _render(report: ScanReport) -> None:
    style = _VERDICT_STYLE[report.verdict]
    head = Text(f" {report.verdict.value} ", style=f"reverse {style}")
    head.append(f"  risk score {report.score}", style=style)
    console.print(Panel(head, title="Hood Trade verdict", border_style=style))

    if report.summary:
        s = report.summary
        console.print(f"[bold]{s.headline}[/bold]\n")
        if s.key_risks:
            console.print("[bold]Key risks[/bold]")
            for r in s.key_risks:
                console.print(f"  • {r}")
        if s.what_to_check:
            console.print("\n[bold]Verify yourself[/bold]")
            for r in s.what_to_check:
                console.print(f"  → {r}")
        console.print()

    table = Table(title="Findings", show_lines=False, expand=True)
    table.add_column("check", style="dim", no_wrap=True)
    table.add_column("sev", no_wrap=True)
    table.add_column("finding")
    for r in report.results:
        table.add_row(r.check, Text(r.severity.value, style=_SEV_STYLE[r.severity]), f"{r.title}")
    console.print(table)

    for note in report.notes:
        console.print(f"[dim]note: {note}[/dim]")


@app.command()
def scan(
    token: str = typer.Option(..., help="Address of the token being traded."),
    quote: str = typer.Option(..., help="Address of the counter asset (e.g. USDG)."),
    amount: float = typer.Option(..., min=0.0, help="Trade notional in USD."),
    pool: str = typer.Option(None, help="Pool/pair address (enables depth + pairing checks)."),
    direction: Direction = typer.Option(Direction.BUY, help="buy | sell"),
    venue: str = typer.Option("uniswap", help="uniswap | pleiades | arcus | 0x | other"),
    no_ai: bool = typer.Option(False, "--no-ai", help="Skip the Claude summary; use the built-in template."),
    as_json: bool = typer.Option(False, "--json", help="Emit the full report as JSON."),
) -> None:
    """Scan a proposed swap and print a GO / CAUTION / NO-GO verdict."""
    settings = load_settings()
    if no_ai:
        settings.ai_enabled = False
    request = TradeRequest(
        token=token, quote=quote, amount_usd=amount, direction=direction, pool=pool, venue=venue
    )
    report = asyncio.run(run_scan(request, settings))
    if report.verdict is not Verdict.UNKNOWN:
        report.summary = summarize(report, settings)

    if as_json:
        console.print_json(report.model_dump_json(indent=2))
    else:
        _render(report)

    # Exit code encodes the verdict for scripting: 0 GO, 1 CAUTION, 2 NO-GO/UNKNOWN.
    raise typer.Exit(code={Verdict.GO: 0, Verdict.CAUTION: 1, Verdict.NO_GO: 2, Verdict.UNKNOWN: 2}[report.verdict])


@app.command()
def doctor() -> None:
    """Check that the configured RPC is reachable and report its chain id."""
    settings = load_settings()
    console.print(f"RPC: [cyan]{settings.rpc_url}[/cyan]")

    async def _probe() -> None:
        async with RpcClient(settings.rpc_url, timeout=settings.request_timeout) as rpc:
            cid = await rpc.chain_id()
            console.print(f"chain id: [bold]{cid}[/bold]")
            if settings.chain_id is not None and settings.chain_id != cid:
                console.print(f"[bold red]mismatch:[/bold red] expected {settings.chain_id}")

    try:
        asyncio.run(_probe())
        console.print("[green]RPC reachable.[/green]")
    except Exception as exc:  # noqa: BLE001
        console.print(f"[bold red]RPC unreachable:[/bold red] {exc}")
        console.print("Set HOODTRADE_RPC_URL to a working Robinhood Chain endpoint.")
        raise typer.Exit(code=1) from exc


@app.command()
def version() -> None:
    """Print the hoodtrade version."""
    console.print(__version__)


if __name__ == "__main__":
    app()
