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

# Conservative signal: tokenized-equity symbols on RH Chain are commonly the ticker
# with a wrapper suffix. We treat a short all-caps alpha symbol as a candidate and
# surface the disclosure; false positives here are cheap (an extra info card).
_EQUITY_HINTS = ("X", "STOCK", "RWA", "HOOD")


def _looks_like_stock_token(symbol: str) -> bool:
    s = symbol.strip().upper()
    if not s or not s.isalnum():
        return False
    if any(s.endswith(h) or s.startswith(h) for h in _EQUITY_HINTS):
        return True
    # bare 1-5 letter ticker, no digits -> plausible equity ticker
    return s.isalpha() and 1 <= len(s) <= 5


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
