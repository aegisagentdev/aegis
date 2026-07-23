# Understanding Verdicts

## How Verdicts Work

The verdict is computed by `engine.decide()` — a pure, deterministic function:

```
1. If ANY finding has severity DANGER → NO
2. If total score >= nogo_score (default 60) → NO
3. If total score >= caution_score (default 25) → CAUTION
4. Otherwise → GO
```

The AI summary explains the verdict but never changes it.

## Verdict Meanings

### GO (exit code 0)

No blocking issues found. The automated checks did not flag anything at DANGER
severity, and the total risk score is below the caution threshold.

**This does NOT mean the token is safe.** It means the checks that ran didn't
find problems. Always verify addresses against official sources.

### CAUTION (exit code 1)

Notable risks found. The aggregate risk score crossed the caution threshold,
but no single finding is blocking. Review the findings before proceeding.

Common CAUTION triggers:
- Active owner on the token contract
- Large trade size relative to pool depth
- Stock token disclosure (debt instrument)

### NO (exit code 2)

Blocking issues found. Either a DANGER-severity finding was detected or the
aggregate score crossed the no-go threshold.

Common NO triggers:
- No contract code at the token address
- Honeypot detected (transfer() reverts)
- Pool has zero liquidity
- Pool doesn't pair the expected tokens
- Chain id mismatch (wrong network)
- Token self-holds >50% of supply

### UNKNOWN (exit code 2)

Not enough data to make a determination. Usually means the RPC was unreachable
or all checks failed. Same exit code as NO — treat as "do not proceed."

## Tuning Thresholds

```bash
# Lower caution threshold — more sensitive
AEGIS_CAUTION_SCORE=15

# Higher no-go threshold — more tolerant
AEGIS_NOGO_SCORE=80
```
