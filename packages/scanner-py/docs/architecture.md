# Architecture

## Overview

Hood Trade is a read-only pre-trade safety scanner for Robinhood Chain. It evaluates a proposed swap against a battery of on-chain checks and returns a structured verdict.

```
User (CLI / JSON)
       │
       ▼
  ┌─────────┐
  │  CLI    │  typer + rich
  │ cli.py  │  parses args, renders output
  └────┬────┘
       │ TradeRequest
       ▼
  ┌──────────┐
  │  Engine  │  engine.py
  │ run_scan │  orchestrates checks, sums scores
  └────┬────┘
       │ Context (request + settings + rpc + cache)
       ▼
  ┌──────────────────────────────────────────────┐
  │              Check Battery                    │
  │                                               │
  │  contract.py   ─ code exists, owner, supply  │
  │  honeypot.py   ─ transfer/approve simulation │
  │  concentration.py ─ self-holding, burned      │
  │  pool.py       ─ exists, liquidity, pairing  │
  │  execution.py  ─ chain id, size, MEV context │
  │  stock_token.py ─ disclosure, divergence     │
  └──────────────────┬───────────────────────────┘
                     │ list[CheckResult]
                     ▼
  ┌──────────┐
  │  Engine  │  decide() → Verdict (GO/CAUTION/NO-GO)
  │  decide  │  deterministic: any DANGER → NO-GO,
  └────┬────┘  score thresholds for CAUTION/NO-GO
       │ ScanReport
       ▼
  ┌──────────┐
  │  AI      │  ai.py
  │ summarize│  Claude explains findings (never overrides verdict)
  └────┬────┘  falls back to template if no API key
       │ RiskSummary
       ▼
  ┌─────────┐
  │  CLI    │  renders verdict panel + findings table
  │ _render │  exit code: 0=GO, 1=CAUTION, 2=NO-GO
  └─────────┘
```

## Key design decisions

### Deterministic verdict, AI explanation

The verdict (GO / CAUTION / NO-GO) is decided by `engine.decide()` using simple rules: any DANGER finding forces NO-GO; otherwise the summed risk score is compared against configurable thresholds. The AI layer (Claude) only explains the findings in plain language — it never overrides the gate.

**Why**: A trader relying on a safety scanner needs reproducible, auditable signals. If the same on-chain state always produces the same verdict, the tool is trustworthy. AI adds value by making findings readable, not by making judgment calls.

### Shared cache between checks

Checks run sequentially and share a `ctx.cache` dictionary. Earlier checks (contract → honeypot → concentration → pool → execution → stock) populate metadata that later checks consume. For example, `ContractExistsCheck` sets `token_code_size`; honeypot and concentration checks skip if it's 0.

### No web3 dependency

The scanner uses a minimal `httpx`-based JSON-RPC client with precomputed function selectors. This keeps the install lightweight (~5 deps) and the surface auditable. Every selector is a constant; the encode/decode logic is <50 lines.

### Graceful degradation

- No `anthropic` package → template summary
- No API key → template summary
- API error → template summary
- No pool address → pool checks skipped with INFO note
- RPC call fails → check failure recorded as a note, scan continues

## Adding checks

See [CONTRIBUTING.md](../CONTRIBUTING.md) for the check protocol and conventions.
