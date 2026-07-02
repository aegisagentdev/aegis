# Sample Scan Output

## CAUTION verdict — active owner + large trade

```
$ hoodtrade scan \
    --token 0xTokenAddr \
    --quote 0xUSDGAddr \
    --amount 150000 \
    --pool 0xPoolAddr \
    --direction buy

╭─ Hood Trade verdict ─────────────────────────────╮
│  CAUTION   risk score 43                         │
╰──────────────────────────────────────────────────╯
Proceed carefully — the scanner found notable risks.

Key risks
  • Token has an active owner: An owner address can pause transfers,
    mint supply, or change fees. Not inherently malicious, but it is
    a live admin key you are trusting.
  • Trade size: large (>= $100k): split or route via an aggregator
    to limit price impact and latency-MEV exposure.
  • AAPL may be a tokenized equity (debt instrument): Robinhood stock
    tokens grant no ownership rights and carry issuer counterparty risk.

Verify yourself
  → Confirm the token and pool addresses against the official source.
  → Check the pool's real depth for your size on the DEX UI.
  → Set a tight slippage limit; split large orders.

┌─ Findings ───────────────────────────────────────┐
│ check              │ sev    │ finding             │
│ EXEC-CHAINID       │ ok     │ Chain id verified   │
│ CONTRACT-EXISTS    │ ok     │ Contract code pre…  │
│ CONTRACT-OWNER     │ warn   │ Token has an acti…  │
│ CONTRACT-SUPPLY    │ ok     │ Standard ERC-20: …  │
│ CONTRACT-HONEYPOT  │ ok     │ Transfer simulati…  │
│ CONTRACT-APPROVE   │ ok     │ Approve simulatio…  │
│ CONC-SELF          │ ok     │ Token self-holdin…  │
│ CONC-BURNED        │ ok     │ 0.0% of supply b…  │
│ POOL-EXISTS        │ ok     │ Pool contract pre…  │
│ POOL-PAIR          │ ok     │ Pool pairs the ex…  │
│ POOL-LIQUIDITY     │ ok     │ Pool has active l…  │
│ EXEC-SIZE          │ warn   │ Trade size: large…  │
│ STOCK-DISCLOSURE   │ warn   │ AAPL may be a tok…  │
│ STOCK-DIVERGENCE   │ info   │ Off-hours pricing…  │
│ EXEC-MEV           │ info   │ FCFS sequencing —…  │
└──────────────────────────────────────────────────┘
```

## NO-GO verdict — honeypot detected

```
$ hoodtrade scan \
    --token 0xSuspiciousToken \
    --quote 0xUSDGAddr \
    --amount 500 \
    --direction buy

╭─ Hood Trade verdict ─────────────────────────────╮
│  NO-GO   risk score 190                          │
╰──────────────────────────────────────────────────╯
High-risk trade — the scanner flagged blocking issues.

Key risks
  • Honeypot risk — transfer() reverts: A simulated sell reverted.
    This is a strong signal that the token blocks transfers for
    non-whitelisted addresses.
  • Token self-holds 65% of supply: The contract holds more than
    half of its own supply. Thin float, dump risk.

┌─ Findings ───────────────────────────────────────┐
│ check              │ sev    │ finding             │
│ CONTRACT-EXISTS    │ ok     │ Contract code pre…  │
│ CONTRACT-OWNER     │ warn   │ Token has an acti…  │
│ CONTRACT-HONEYPOT  │ danger │ Honeypot risk — t…  │
│ CONC-SELF          │ danger │ Token self-holds …  │
│ ...                │        │                     │
└──────────────────────────────────────────────────┘
```

## JSON output for scripting

```
$ hoodtrade scan --token 0x... --quote 0x... --amount 100 --json --no-ai
```

Returns a `ScanReport` JSON object with `verdict`, `score`, `results[]`, and `notes[]`. Exit code encodes the verdict: 0 = GO, 1 = CAUTION, 2 = NO-GO/UNKNOWN.
