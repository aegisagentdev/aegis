"""Chain registry and scan orchestration shared by the CLI and the MCP server.

Keeping the chain table, settings resolution and the young-chain leniency in one
place means every front-end (CLI, MCP server, a future bot or REST API) produces
the *same* verdict for the same token. Nothing here prints or formats — callers
own presentation.
"""

from __future__ import annotations

from .ai import summarize
from .config import Settings, load_settings
from .engine import run_scan
from .models import Direction, ScanReport, TradeRequest

# Default quote asset (WETH). Every supported chain quotes against its wrapped
# native today; overridable per scan.
WETH = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"

# One entry per chain: numeric id, default public RPC, DexScreener slug, and the
# GoPlus chain id (None where GoPlus has no coverage — e.g. Robinhood Chain).
CHAINS: dict[str, dict] = {
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

CHAIN_ALIASES: dict[str, str] = {
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
YOUNG_CHAINS: set[str] = {"robinhood"}


class UnknownChainError(ValueError):
    """Raised when a chain name/alias is not in the registry."""


def apply_young_chain(settings: Settings) -> None:
    """Relax only the market-maturity gates so a brand-new chain's normal thin
    liquidity and low activity produce CAUTION, not an automatic NO-GO. Security
    signals still block on any chain."""
    settings.block_on_thin_liquidity = False
    settings.block_on_high_impact = False
    settings.liq_danger_below = 1_000
    settings.liq_warn_below = 8_000
    settings.caution_score = 30  # a lone thin-liquidity / high-impact WARN (35) still cautions
    settings.nogo_score = 90


def resolve_chain(chain: str) -> tuple[str, dict]:
    """Map a chain name or alias to its canonical key and config, or raise."""
    key = CHAIN_ALIASES.get(chain.lower(), chain.lower())
    cfg = CHAINS.get(key)
    if cfg is None:
        raise UnknownChainError(f"unknown chain '{chain}'; supported: {', '.join(CHAINS)}")
    return key, cfg


def build_settings(
    chain: str = "robinhood",
    *,
    rpc: str | None = None,
    no_goplus: bool = False,
    no_market: bool = False,
    strict: bool = False,
    lenient: bool = False,
    ai_enabled: bool = False,
) -> tuple[Settings, str, bool]:
    """Resolve a chain to a ready-to-run Settings object.

    Returns (settings, canonical_chain_key, young_mode). ``young_mode`` is True
    when new-chain leniency was applied. Raises UnknownChainError on a bad chain.
    """
    key, cfg = resolve_chain(chain)
    settings = load_settings()
    settings.rpc_url = rpc or cfg["rpc"]
    settings.chain_id = cfg["id"]
    settings.goplus_enabled = not no_goplus and cfg["goplus"] is not None
    settings.goplus_chain_id = cfg["goplus"] if settings.goplus_enabled else None
    settings.dexscreener_enabled = not no_market
    settings.dexscreener_chain = None if no_market else cfg["dex"]
    settings.ai_enabled = ai_enabled
    young = (key in YOUNG_CHAINS or lenient) and not strict
    if young:
        apply_young_chain(settings)
    return settings, key, young


def validate_address(token: str) -> None:
    """Raise ValueError if ``token`` is not a 42-char 0x address."""
    if not token.startswith("0x") or len(token) != 42:
        raise ValueError(f"invalid address: {token!r} (expected a 42-char 0x… address)")


async def scan_token(
    token: str,
    *,
    chain: str = "robinhood",
    amount_usd: float = 1000.0,
    quote: str = WETH,
    rpc: str | None = None,
    no_goplus: bool = False,
    no_market: bool = False,
    strict: bool = False,
    lenient: bool = False,
    ai_summary: bool = False,
) -> ScanReport:
    """High-level scan: validate, resolve the chain, run the battery, summarize.

    This is the single entry point every non-CLI front-end should call so the
    verdict is identical to the CLI's.
    """
    validate_address(token)
    settings, _key, _young = build_settings(
        chain,
        rpc=rpc,
        no_goplus=no_goplus,
        no_market=no_market,
        strict=strict,
        lenient=lenient,
        ai_enabled=ai_summary,
    )
    request = TradeRequest(token=token, quote=quote, amount_usd=amount_usd, direction=Direction.BUY)
    report = await run_scan(request, settings)
    report.summary = summarize(report, settings)
    return report
