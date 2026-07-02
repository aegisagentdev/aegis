"""Core data types shared across the scanner.

These are the contract between the deterministic on-chain checks, the aggregation
engine, and the AI summary layer. Keeping them in one place means the AI layer only
ever sees validated, structured signals — never raw RPC blobs.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class Severity(str, Enum):
    OK = "ok"
    INFO = "info"
    WARN = "warn"
    DANGER = "danger"


class Direction(str, Enum):
    BUY = "buy"  # spending the quote asset to acquire `token`
    SELL = "sell"  # disposing of `token` for the quote asset


class TradeRequest(BaseModel):
    """A proposed swap the user is about to sign."""

    token: str = Field(description="Address of the token being acquired or disposed of.")
    quote: str = Field(description="Address of the counter asset (e.g. USDG, WETH).")
    amount_usd: float = Field(gt=0, description="Notional size of the trade in USD.")
    direction: Direction = Direction.BUY
    pool: str | None = Field(default=None, description="Specific pool/pair address, if known.")
    venue: str = Field(default="uniswap", description="uniswap | pleiades | arcus | 0x | other")


class CheckResult(BaseModel):
    """One finding from one check."""

    check: str = Field(description="Stable check id, e.g. CONTRACT-HONEYPOT.")
    severity: Severity
    score: int = Field(ge=0, description="Risk points contributed toward the verdict.")
    title: str
    detail: str
    evidence: dict[str, str] = Field(default_factory=dict)


class Verdict(str, Enum):
    GO = "GO"
    CAUTION = "CAUTION"
    NO_GO = "NO-GO"
    UNKNOWN = "UNKNOWN"  # not enough data (e.g. RPC unreachable)


class RiskSummary(BaseModel):
    """AI-authored, human-facing explanation. The verdict itself is NOT decided here —
    it is decided by the deterministic engine; this only explains and contextualizes."""

    headline: str = Field(description="One sentence a trader can read in two seconds.")
    key_risks: list[str] = Field(default_factory=list, description="Plain-language risks, most severe first.")
    what_to_check: list[str] = Field(default_factory=list, description="Concrete things the user can verify.")


class ScanReport(BaseModel):
    request: TradeRequest
    verdict: Verdict
    score: int
    results: list[CheckResult] = Field(default_factory=list)
    summary: RiskSummary | None = None
    notes: list[str] = Field(default_factory=list, description="Operational notes (skipped checks, RPC errors).")

    @property
    def worst(self) -> Severity:
        order = [Severity.OK, Severity.INFO, Severity.WARN, Severity.DANGER]
        worst = Severity.OK
        for r in self.results:
            if order.index(r.severity) > order.index(worst):
                worst = r.severity
        return worst
