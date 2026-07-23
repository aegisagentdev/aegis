"""Model Context Protocol (MCP) server for Aegis.

Exposes the pre-trade scanner as tools any MCP-compatible agent can call —
Claude Desktop, Claude Code, Cursor, Cline, Windsurf, or a custom agent built on
the OpenAI/Anthropic agent SDKs. The agent gets the same verdict the CLI would:
GO / CAUTION / NO with the on-chain evidence behind it.

Run it:  ``aegis-mcp``  (stdio transport)

Install:  ``pip install "aegis[mcp]"``  or  ``uvx --from "aegis[mcp]" aegis-mcp``
"""

from __future__ import annotations

from typing import Any

from .models import ScanReport
from .networks import CHAINS, WETH, UnknownChainError, resolve_chain
from .networks import scan_token as _scan_token

try:
    from mcp.server.fastmcp import FastMCP
except ModuleNotFoundError as exc:  # pragma: no cover - import guard
    raise SystemExit(
        "The MCP server needs the 'mcp' package. Install it with:\n"
        '  pip install "aegis[mcp]"\n'
        "or run it without installing via:\n"
        '  uvx --from "aegis[mcp]" aegis-mcp'
    ) from exc

mcp = FastMCP(
    "aegis",
    instructions=(
        "Aegis is a read-only pre-trade safety scanner for Robinhood Chain and other "
        "EVM chains. Call `scan_token` with a token contract address BEFORE the user buys or "
        "signs a swap; relay the verdict (GO / CAUTION / NO), the key risks, and the risk "
        "score. It never signs, holds funds or trades — it only inspects. Use `list_chains` to "
        "see supported networks and `check_rpc` to confirm connectivity."
    ),
)


def _report_to_dict(report: ScanReport) -> dict[str, Any]:
    """Flatten a ScanReport into a compact, LLM-friendly structure. Nothing is
    dropped — every finding and its evidence is included."""
    s = report.summary
    return {
        "verdict": report.verdict.value,
        "risk_score": report.score,
        "token": {
            "address": report.request.token,
            "name": report.token_name,
            "symbol": report.token_symbol,
        },
        "market": {
            "price_usd": report.price_usd,
            "market_cap_usd": report.market_cap,
            "liquidity_usd": report.liquidity_usd,
            "volume_24h_usd": report.volume_24h,
        },
        "summary": None
        if s is None
        else {
            "headline": s.headline,
            "key_risks": list(s.key_risks),
            "verify_yourself": list(s.what_to_check),
        },
        "findings": [
            {
                "check": r.check,
                "severity": r.severity.value,
                "score": r.score,
                "title": r.title,
                "detail": r.detail,
                "evidence": r.evidence,
            }
            for r in report.results
        ],
        "notes": list(report.notes),
    }


@mcp.tool()
async def scan_token(
    token: str,
    chain: str = "robinhood",
    amount_usd: float = 1000.0,
    quote: str = WETH,
    strict: bool = False,
    lenient: bool = False,
) -> dict[str, Any]:
    """Scan a token contract and return a GO / CAUTION / NO safety verdict.

    Args:
        token: Token contract address (42-char 0x…).
        chain: Network name or alias — robinhood (default), ethereum, base,
            arbitrum, bsc, polygon, optimism, avalanche (aliases: eth, arb, op…).
        amount_usd: Intended trade size in USD; affects the price-impact check.
        quote: Quote-asset address (defaults to WETH).
        strict: Force full strictness — thin liquidity / oversized trades block
            even on a young chain.
        lenient: Relax market-maturity gates on any chain (auto-on for Robinhood
            Chain). Security signals (honeypot, hidden fee, mint) always block.

    Returns a structured verdict: risk score, token identity, market snapshot,
    a plain-English summary with key risks, and every individual finding with
    its on-chain evidence. Read-only — this never signs, holds funds or trades.
    """
    try:
        report = await _scan_token(
            token,
            chain=chain,
            amount_usd=amount_usd,
            quote=quote,
            strict=strict,
            lenient=lenient,
        )
    except (ValueError, UnknownChainError) as exc:
        return {"error": str(exc)}
    return _report_to_dict(report)


@mcp.tool()
async def check_rpc(chain: str = "robinhood") -> dict[str, Any]:
    """Check that a chain's RPC endpoint is reachable and reports the expected
    chain id. Use before scanning if a scan returns connectivity notes."""
    from .rpc import RpcClient

    try:
        _key, cfg = resolve_chain(chain)
    except UnknownChainError as exc:
        return {"error": str(exc)}
    try:
        async with RpcClient(cfg["rpc"], timeout=15.0) as rpc:
            cid = await rpc.chain_id()
        return {"chain": _key, "rpc": cfg["rpc"], "chain_id": cid, "expected": cfg["id"], "reachable": True}
    except Exception as exc:  # noqa: BLE001 - report unreachable, don't crash the tool
        return {"chain": _key, "rpc": cfg["rpc"], "reachable": False, "error": str(exc)}


@mcp.tool()
def list_chains() -> dict[str, Any]:
    """List the supported networks and which ones use new-chain leniency."""
    from .networks import YOUNG_CHAINS

    return {
        "chains": [
            {"name": name, "chain_id": cfg["id"], "young_chain_default": name in YOUNG_CHAINS}
            for name, cfg in CHAINS.items()
        ]
    }


def main() -> None:
    """Console-script entry point: run the MCP server over stdio."""
    mcp.run()


if __name__ == "__main__":
    main()
