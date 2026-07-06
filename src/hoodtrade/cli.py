"""hoodtrade command-line interface."""

from __future__ import annotations

import asyncio

import typer
from rich import box
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


def _fmt_usd(value: float | None) -> str | None:
    if value is None:
        return None
    if value == 0:
        return "$0"
    if abs(value) < 0.01:
        return f"${value:.8f}".rstrip("0").rstrip(".")
    if abs(value) < 1000:
        return f"${value:,.2f}"
    return f"${value:,.0f}"


def _render_market(report: ScanReport) -> None:
    """A clearly-labeled market snapshot so liquidity is never confused with mcap."""
    parts: list[str] = []
    if (p := _fmt_usd(report.price_usd)) is not None:
        parts.append(f"[dim]price[/dim] {p}")
    if (mc := _fmt_usd(report.market_cap)) is not None:
        parts.append(f"[dim]mcap[/dim] {mc}")
    if (liq := _fmt_usd(report.liquidity_usd)) is not None:
        parts.append(f"[dim]liquidity[/dim] {liq}")
    if (vol := _fmt_usd(report.volume_24h)) is not None:
        parts.append(f"[dim]24h vol[/dim] {vol}")
    if parts:
        console.print("  " + "   ".join(parts) + "\n")


def _render(report: ScanReport) -> None:
    style = _VERDICT_STYLE[report.verdict]
    head = Text(f" {report.verdict.value} ", style=f"reverse {style}")
    head.append(f"  risk score {report.score}", style=style)
    if report.token_name or report.token_symbol:
        label = report.token_name or ""
        if report.token_symbol and report.token_symbol != report.token_name:
            label = f"{label} ({report.token_symbol})" if label else report.token_symbol
        title = f"Hood Trade — {label.strip()}"
    else:
        title = "Hood Trade verdict"
    console.print(Panel(head, title=title, border_style=style, box=box.SIMPLE, expand=False, padding=(0, 1)))

    _render_market(report)

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

    table = Table(title="Findings", show_lines=False, expand=True, box=box.SIMPLE)
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
    OK, WARN, INFO = Severity.OK, Severity.WARN, Severity.INFO
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
        _cr("transfer_fee", WARN, 30, "Transfer fee detected", "5% fee on transfers."),
    ]
    score = sum(r.score for r in results)
    settings = load_settings()
    settings.ai_enabled = False
    _apply_young_chain(settings)  # demo token is on the new chain — show lenient thresholds
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
    return ScanReport(
        request=request,
        verdict=verdict,
        score=score,
        token_name="Demo Token",
        token_symbol="DEMO",
        results=results,
        summary=summary,
        notes=[],
    )


WETH = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"

# One table per chain: numeric id, default public RPC, DexScreener slug, and the
# GoPlus chain id (None where GoPlus has no coverage — e.g. Robinhood Chain).
CHAINS = {
    "robinhood": {"id": 4663, "rpc": "https://rpc.mainnet.chain.robinhood.com", "dex": "robinhood", "goplus": None},
    "ethereum": {"id": 1, "rpc": "https://ethereum-rpc.publicnode.com", "dex": "ethereum", "goplus": 1},
    "base": {"id": 8453, "rpc": "https://base-rpc.publicnode.com", "dex": "base", "goplus": 8453},
    "arbitrum": {"id": 42161, "rpc": "https://arbitrum-one-rpc.publicnode.com", "dex": "arbitrum", "goplus": 42161},
    "bsc": {"id": 56, "rpc": "https://bsc-rpc.publicnode.com", "dex": "bsc", "goplus": 56},
    "polygon": {"id": 137, "rpc": "https://polygon-bor-rpc.publicnode.com", "dex": "polygon", "goplus": 137},
    "optimism": {"id": 10, "rpc": "https://optimism-rpc.publicnode.com", "dex": "optimism", "goplus": 10},
    "avalanche": {
        "id": 43114,
        "rpc": "https://avalanche-c-chain-rpc.publicnode.com",
        "dex": "avalanche",
        "goplus": 43114,
    },
}
CHAIN_ALIASES = {
    "rh": "robinhood",
    "hood": "robinhood",
    "eth": "ethereum",
    "mainnet": "ethereum",
    "arb": "arbitrum",
    "bnb": "bsc",
    "matic": "polygon",
    "op": "optimism",
    "avax": "avalanche",
}

# Chains young enough that thin books and low volume are the norm, not a red
# flag. For these, market-maturity signals caution instead of blocking; the
# security checks (honeypot, hidden fee, mint, permissions) are untouched.
YOUNG_CHAINS = {"robinhood"}


def _apply_young_chain(settings) -> None:
    """Relax only the market-maturity gates so a brand-new chain's normal thin
    liquidity and low activity produce CAUTION, not an automatic NO-GO. Security
    signals still block on any chain."""
    settings.block_on_thin_liquidity = False
    settings.block_on_high_impact = False
    settings.liq_danger_below = 1_000
    settings.liq_warn_below = 8_000
    settings.caution_score = 30  # a lone thin-liquidity / high-impact WARN (35) still cautions
    settings.nogo_score = 90


@app.command()
def scan(
    token: str = typer.Argument(None, help="Token contract address to scan."),
    chain: str = typer.Option(
        "robinhood", "--chain", help="robinhood, ethereum, base, arbitrum, bsc, polygon, optimism, avalanche."
    ),
    quote: str = typer.Option(WETH, help="Quote asset address (default: WETH)."),
    amount: float = typer.Option(1000.0, help="Trade size in USD."),
    rpc: str = typer.Option(None, "--rpc", help="Override the RPC endpoint."),
    no_goplus: bool = typer.Option(False, "--no-goplus", help="Skip the GoPlus reputation lookup."),
    no_market: bool = typer.Option(False, "--no-market", help="Skip the DexScreener market lookup."),
    as_json: bool = typer.Option(False, "--json", help="Output as JSON."),
    strict: bool = typer.Option(
        False, "--strict", help="Full strictness — thin liquidity / oversized trades block even on new chains."
    ),
    lenient: bool = typer.Option(
        False, "--lenient", help="Relax market-maturity gates on any chain (auto-on for Robinhood Chain)."
    ),
    demo: bool = typer.Option(False, "--demo", help="Run with sample data (no RPC needed)."),
) -> None:
    """Scan a token contract and print a GO / CAUTION / NO-GO verdict.

    \b
    Examples:
      hoodtrade scan 0x87E1Ed2aDe9Db5DEA0E805f296B796219A05636B
      hoodtrade scan 0x4200000000000000000000000000000000000006 --chain base
      hoodtrade scan 0xdAC17F958D2ee523a2206206994597C13D831ec7 --chain ethereum --json
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
            console.print("  hoodtrade scan 0x87E1Ed...636B")
            console.print("  hoodtrade scan --demo")
            raise typer.Exit(code=2)
        if not token.startswith("0x") or len(token) != 42:
            console.print(f"[bold red]Error:[/bold red] invalid address: {token}")
            raise typer.Exit(code=2)

        key = CHAIN_ALIASES.get(chain.lower(), chain.lower())
        cfg = CHAINS.get(key)
        if cfg is None:
            console.print(f"[bold red]Error:[/bold red] unknown chain: {chain}")
            console.print(f"  supported: {', '.join(CHAINS)}")
            raise typer.Exit(code=2)

        settings = load_settings()
        settings.rpc_url = rpc or cfg["rpc"]
        settings.chain_id = cfg["id"]
        settings.goplus_enabled = not no_goplus and cfg["goplus"] is not None
        settings.goplus_chain_id = cfg["goplus"] if settings.goplus_enabled else None
        settings.dexscreener_enabled = not no_market
        settings.dexscreener_chain = None if no_market else cfg["dex"]
        settings.ai_enabled = False
        young = (key in YOUNG_CHAINS or lenient) and not strict
        if young:
            _apply_young_chain(settings)
        request = TradeRequest(
            token=token,
            quote=quote,
            amount_usd=amount,
            direction=Direction.BUY,
        )
        sources = ["on-chain"]
        if settings.goplus_enabled:
            sources.append("GoPlus")
        if settings.dexscreener_enabled:
            sources.append("DexScreener")
        mode = "  [dim]·[/dim] [yellow]lenient (new-chain)[/yellow]" if young else ""
        console.print(
            f"[dim]Scanning [bold]{token[:8]}…{token[-4:]}[/bold] on {key} ({' + '.join(sources)})…[/dim]{mode}\n"
        )
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
