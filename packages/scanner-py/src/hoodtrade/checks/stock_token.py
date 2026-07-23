"""Stock-token integrity checks.

Robinhood Chain's headline product is tokenized equities. Critically, these are NOT
shares: they are debt instruments issued by Robinhood Assets (Jersey) Limited that
track a price. That has two consequences a trader must understand before signing:

  1. Counterparty risk — you hold an issuer obligation, not equity ownership.
  2. Off-hours divergence — the token trades 24/7, but the underlying equity does not.
     During market closure the token price can drift from any fair reference, and thin
     weekend liquidity amplifies it.

This check is heuristic and label-driven: it flags when the traded symbol looks like a
tokenized equity so the user gets the disclosure and a divergence caution. It does not
fetch live equity prices (no market-data vendor is wired in this build); the divergence
thresholds in settings are applied when a reference price is supplied via evidence.
"""

from __future__ import annotations

from ..models import CheckResult, Severity
from .base import Context

# Known equity tickers Robinhood offers as tokenized stocks. Matching the exact
# symbol (optionally with a common wrapper suffix like AAPLx) keeps this precise:
# a memecoin or stablecoin will not accidentally trip the equity disclosure.
_EQUITY_TICKERS = frozenset(
    {
        "AAPL",
        "MSFT",
        "NVDA",
        "AMZN",
        "GOOGL",
        "GOOG",
        "META",
        "TSLA",
        "AMD",
        "NFLX",
        "INTC",
        "DIS",
        "BA",
        "JPM",
        "V",
        "MA",
        "PYPL",
        "SQ",
        "COIN",
        "HOOD",
        "UBER",
        "ABNB",
        "SHOP",
        "SPY",
        "QQQ",
        "KO",
        "PEP",
        "WMT",
        "NKE",
        "MCD",
        "SBUX",
        "GME",
        "AMC",
        "PLTR",
        "SNAP",
        "F",
        "GM",
        "T",
        "BABA",
    }
)
# Wrapper suffixes Robinhood-style tokenized equities append to the raw ticker.
_WRAPPER_SUFFIXES = ("X", ".RH", "-RH")


def _underlying_ticker(symbol: str) -> str | None:
    """Return the equity ticker this symbol represents, or None if it isn't one."""
    s = symbol.strip().upper()
    if not s:
        return None
    if s in _EQUITY_TICKERS:
        return s
    for suffix in _WRAPPER_SUFFIXES:
        if s.endswith(suffix):
            base = s[: -len(suffix)]
            if base in _EQUITY_TICKERS:
                return base
    return None


def _looks_like_stock_token(symbol: str) -> bool:
    return _underlying_ticker(symbol) is not None


class StockTokenDisclosureCheck:
    id = "STOCK-DISCLOSURE"

    async def run(self, ctx: Context) -> list[CheckResult]:
        symbol = str(ctx.cache.get("token_symbol") or "")
        if not _looks_like_stock_token(symbol):
            return []
        return [
            CheckResult(
                check=self.id,
                severity=Severity.WARN,
                score=15,
                title=f"{symbol} may be a tokenized equity (debt instrument)",
                detail=(
                    "Robinhood stock tokens are tokenized debt securities issued by Robinhood "
                    "Assets (Jersey) Limited. They track an equity price but grant no ownership "
                    "or shareholder rights, and carry issuer counterparty risk. They are also "
                    "restricted in several jurisdictions (incl. the US)."
                ),
                evidence={"symbol": symbol},
            )
        ]


class StockTokenDivergenceCheck:
    """Applies configured divergence thresholds when a reference price is supplied.

    The trade request can carry an off-chain reference via evidence in the cache
    (``ref_price`` and ``token_price``); when present we compute basis-point drift and
    escalate. Without a reference we emit a single off-hours caution."""

    id = "STOCK-DIVERGENCE"

    async def run(self, ctx: Context) -> list[CheckResult]:
        symbol = str(ctx.cache.get("token_symbol") or "")
        if not _looks_like_stock_token(symbol):
            return []
        ref = ctx.cache.get("ref_price")
        tok = ctx.cache.get("token_price")
        if isinstance(ref, (int, float)) and isinstance(tok, (int, float)) and ref > 0:
            bps = abs(tok - ref) / ref * 10_000
            if bps >= ctx.settings.stock_divergence_danger_bps:
                sev, score = Severity.DANGER, 45
            elif bps >= ctx.settings.stock_divergence_warn_bps:
                sev, score = Severity.WARN, 20
            else:
                sev, score = Severity.OK, 0
            return [
                CheckResult(
                    check=self.id,
                    severity=sev,
                    score=score,
                    title=f"Token/underlying divergence: {bps:.0f} bps",
                    detail=(
                        "The token price differs from the supplied reference by "
                        f"{bps:.0f} basis points. Large divergence during off-hours or thin "
                        "liquidity means you may be buying above fair value."
                    ),
                    evidence={"ref_price": str(ref), "token_price": str(tok), "bps": f"{bps:.0f}"},
                )
            ]
        return [
            CheckResult(
                check=self.id,
                severity=Severity.INFO,
                score=5,
                title="Off-hours pricing risk (no reference supplied)",
                detail=(
                    "Stock tokens trade 24/7 while the underlying market closes. Without a live "
                    "reference price, off-hours divergence cannot be measured. Check the mark "
                    "against the last equity close before trading on weekends or overnight."
                ),
            )
        ]
