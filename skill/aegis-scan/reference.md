# Aegis Scan — reference

## Verdict semantics

The verdict is a weighted sum of independent findings.

| Severity | Weight |
|----------|--------|
| OK       | 0      |
| INFO     | 1      |
| WARN     | 3      |
| DANGER   | 10 (weighted) |

Decision:
- **Any DANGER finding → NO** (a model can never override this).
- else score ≥ `nogoScore` → **NO**
- else score ≥ `cautionScore` → **CAUTION**
- else → **GO**

Same input → same verdict. No LLM in the decision path.

## The check battery (21 checks, six families)

| Family | Checks |
|--------|--------|
| Contract | code exists · ownership renounced · supply sanity |
| Honeypot | simulated `transfer()` / `approve()` via read-only `eth_call` |
| Concentration | token self-holding · burned float |
| Pool | pool exists · pair integrity · in-range liquidity |
| Reputation (GoPlus) | honeypot · buy/sell tax · mintable · pausable · blacklist · owner-can-rewrite-balance · verified source · proxy |
| Market / execution | liquidity · 24h volume · trade-size-vs-depth · tokenized-stock (RIF) disclosure + price divergence |

## JSON shape (`--json`)

```json
{
  "verdict": "NO",
  "risk_score": 486,
  "token": { "address": "0x…", "name": "…", "symbol": "…" },
  "market": { "price_usd": 0.0004, "liquidity_usd": 8000, "volume_24h_usd": 500 },
  "summary": { "headline": "…", "key_risks": ["…"], "verify_yourself": ["…"] },
  "findings": [
    { "check": "CONTRACT-HONEYPOT", "severity": "danger", "score": 90, "title": "…", "detail": "…", "evidence": {} }
  ],
  "notes": ["…"]
}
```

## Firewall detectors (way in)

Decoders: base64 · hex · percent · unicode-escape · zero-width strip · homoglyph fold.
Heuristics: instruction-override · role/system-prompt hijack · exfiltration ·
tool-call injection · embedded-transaction directive · false-authority framing.
Action guard: unlimited approval · off-allow-list recipient · single-call drain.

Decision: `allow` / `flag` / `block`, with a sanitized copy of the text.
