# Python API Reference

Aegis can be used as a library in addition to the CLI.

## Quick Start

```python
import asyncio
from aegis.config import Settings
from aegis.engine import run_scan
from aegis.models import TradeRequest, Direction

async def check_trade():
    settings = Settings()
    request = TradeRequest(
        token="0xTokenAddress",
        quote="0xQuoteAddress",
        amount_usd=5000,
        direction=Direction.BUY,
        pool="0xPoolAddress",
    )
    report = await run_scan(request, settings)
    print(f"Verdict: {report.verdict.value}, Score: {report.score}")

asyncio.run(check_trade())
```

## Core Types

### TradeRequest

```python
class TradeRequest(BaseModel):
    token: str          # Address of the token being traded
    quote: str          # Address of the counter asset (e.g. USDG)
    amount_usd: float   # Notional size in USD (must be > 0)
    direction: Direction # BUY or SELL
    pool: str | None     # Pool address (enables depth checks)
    venue: str           # "uniswap" | "pleiades" | "arcus" | "0x" | "other"
```

### ScanReport

```python
class ScanReport(BaseModel):
    request: TradeRequest
    verdict: Verdict          # GO | CAUTION | NO_GO | UNKNOWN
    score: int                # Aggregate risk score
    results: list[CheckResult]
    summary: RiskSummary | None
    notes: list[str]          # Operational notes

    @property
    def worst(self) -> Severity:  # Worst severity across all results
```

### CheckResult

```python
class CheckResult(BaseModel):
    check: str           # Stable check id (e.g. "CONTRACT-HONEYPOT")
    severity: Severity   # OK | INFO | WARN | DANGER
    score: int           # Risk points (>= 0)
    title: str
    detail: str
    evidence: dict[str, str]
```

### Verdict

| Value | Meaning |
|-------|---------|
| `GO` | No blocking issues |
| `CAUTION` | Notable risks, review findings |
| `NO_GO` | Blocking issues found |
| `UNKNOWN` | Insufficient data (RPC failure) |

### Severity

| Value | Meaning | Typical score |
|-------|---------|---------------|
| `OK` | Check passed | 0 |
| `INFO` | Informational | 0-5 |
| `WARN` | Notable risk | 10-25 |
| `DANGER` | Blocking issue | 40-100 |

## Engine

### `run_scan(request, settings, checks=None) -> ScanReport`

Runs the full check battery against a trade request.

- `checks`: override the default battery (useful for testing)
- Returns a `ScanReport` with all findings and the computed verdict

### `decide(score, results, settings) -> Verdict`

Pure function: computes the verdict from score and results.

- Any DANGER finding → NO_GO
- Score >= `nogo_score` → NO_GO
- Score >= `caution_score` → CAUTION
- Otherwise → GO

## Export

```python
from aegis.export import to_json, to_csv, to_markdown, to_dict, severity_counts

json_str = to_json(report, indent=2)
csv_str = to_csv(report)
md_str = to_markdown(report)
data = to_dict(report)
counts = severity_counts(report)  # {"ok": 5, "info": 2, "warn": 1, "danger": 0}
```

## AI Summary

```python
from aegis.ai import summarize

summary = summarize(report, settings)
# Returns RiskSummary with headline, key_risks, what_to_check
# Falls back to template if AI is disabled or unavailable
```

## Custom Checks

```python
from aegis.checks.base import Check, Context
from aegis.models import CheckResult, Severity

class MyCheck:
    id = "CUSTOM-CHECK"

    async def run(self, ctx: Context) -> list[CheckResult]:
        # Your check logic here
        return [
            CheckResult(
                check=self.id,
                severity=Severity.OK,
                score=0,
                title="Custom check passed",
                detail="Everything looks good.",
            )
        ]
```
