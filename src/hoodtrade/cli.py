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
from .engine import decide, run_scan
from .models import CheckResult, Direction, RiskSummary, ScanReport, Severity, TradeRequest, Verdict
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


def _cr(check: str, sev: Severity, score: int, title: str, detail: str) -> CheckResult:
    return CheckResult(check=check, severity=sev, score=score, title=title, detail=detail)


def _demo_report(request: TradeRequest) -> ScanReport:
    """Generate a realistic demo report without any RPC calls."""
    OK, WARN, INFO, DANGER = Severity.OK, Severity.WARN, Severity.INFO, Severity.DANGER
    results = [
        _cr("contract_exists", OK, 0, "Contract verified", "Bytecode found at token address (1.2 kB)."),
        _cr("ownership", WARN, 15, "Active owner detected", "owner() returns a non-zero EOA."),
        _cr("supply_sanity", OK, 0, "Supply within norms", "Total supply 1,000,000 tokens, 18 decimals."),
        _cr("honeypot_transfer", OK, 0, "Transfer simulation passed", "transfer() did not revert."),
        _cr("honeypot_approve", OK, 0, "Approve simulation passed", "approve() succeeded normally."),
        _cr("token_self_holding", OK, 0, "Self-holding normal", "Token contract holds 2.1% of supply."),
        _cr("burned_supply", INFO, 0, "No tokens burned", "Zero balance at burn address."),
        _cr("pool_exists", OK, 0, "Pool found", "Uniswap V3 pool at 0x7a25...c3f1."),
        _cr("pool_liquidity", WARN, 10, "Thin liquidity", "Depth ~$12,400 — trade is 8% of pool."),
        _cr("pool_pair_integrity", OK, 0, "Pair tokens match", "token0/token1 match request."),
        _cr("chain_identity", OK, 0, "Correct chain", "Chain id matches config."),
        _cr("size_vs_depth", INFO, 5, "Moderate price impact", "Estimated slippage 0.8%."),
        _cr("proxy_detection", OK, 0, "Not a proxy", "EIP-1967 slot is empty."),
        _cr("code_size", OK, 0, "Code size normal", "Bytecode is 1,247 bytes."),
        _cr("transfer_fee", DANGER, 30, "Transfer fee detected", "5% fee on transfers."),
    ]
    score = sum(r.score for r in results)
    settings = load_settings()
    settings.ai_enabled = False
    verdict = decide(score, results, settings)
    summary = RiskSummary(
        headline="Caution — transfer fee and thin liquidity increase risk on this trade.",
        key_risks=[
            "Transfer fee detected: 5% fee on every transfer reduces the amount you receive.",
            "Active owner: contract owner can call privileged functions (pause, mint, change fee).",
            "Thin liquidity: pool depth is ~$12,400 — your $1,000 trade moves 8% of reserves.",
        ],
        what_to_check=[
            "Confirm the token address against the project's official channels.",
            "Check if the fee is documented — unlisted fees are a common rug-pull pattern.",
            "Use a tight slippage limit (1-2%) and consider splitting the order.",
        ],
    )
    return ScanReport(request=request, verdict=verdict, score=score, results=results, summary=summary, notes=[])


WETH = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
ETH_RPC = "https://ethereum-rpc.publicnode.com"


@app.command()
def scan(
    token: str = typer.Argument(None, help="Token contract address to scan."),
    quote: str = typer.Option(WETH, help="Quote asset address (default: WETH)."),
    amount: float = typer.Option(1000.0, help="Trade size in USD."),
    rpc: str = typer.Option(None, "--rpc", help="RPC endpoint (default: public Ethereum)."),
    as_json: bool = typer.Option(False, "--json", help="Output as JSON."),
    demo: bool = typer.Option(False, "--demo", help="Run with sample data (no RPC needed)."),
) -> None:
    """Scan a token contract and print a GO / CAUTION / NO-GO verdict.

    \b
    Examples:
      hoodtrade scan 0xdAC17F958D2ee523a2206206994597C13D831ec7
      hoodtrade scan 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48 --json
      hoodtrade scan --demo
    """
    if demo:
        request = TradeRequest(
            token="0x7a250d5630b4cf539739df2c5dacb4c659f2488d",
            quote=WETH,
            amount_usd=amount,
            direction=Direction.BUY,
        )
        report = _demo_report(request)
    else:
        if not token:
            console.print("[bold red]Error:[/bold red] provide a token address or use --demo\n")
            console.print("  hoodtrade scan 0xdAC17F...ec7")
            console.print("  hoodtrade scan --demo")
            raise typer.Exit(code=2)
        if not token.startswith("0x") or len(token) != 42:
            console.print(f"[bold red]Error:[/bold red] invalid address: {token}")
            raise typer.Exit(code=2)

        settings = load_settings()
        settings.rpc_url = rpc or ETH_RPC
        settings.ai_enabled = False
        request = TradeRequest(
            token=token,
            quote=quote,
            amount_usd=amount,
            direction=Direction.BUY,
        )
        console.print(f"[dim]Scanning [bold]{token[:8]}…{token[-4:]}[/bold] via {settings.rpc_url}…[/dim]\n")
        report = asyncio.run(run_scan(request, settings))
        report.summary = summarize(report, settings)

    if as_json:
        console.print_json(report.model_dump_json(indent=2))
    else:
        _render(report)

    raise typer.Exit(
        code={
            Verdict.GO: 0,
            Verdict.CAUTION: 1,
            Verdict.NO_GO: 2,
            Verdict.UNKNOWN: 2,
        }[report.verdict]
    )


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
