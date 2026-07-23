# @aegis/scanner

A deterministic pre-trade safety scanner. Feed it a `TokenSnapshot` and a
`TradeRequest`; get a reproducible **GO / CAUTION / NO** verdict with every
finding and its evidence.

The deterministic check
battery. The Python engine — including live RPC, GoPlus and
DexScreener data collection and the MCP server — lives in
[`packages/scanner-py`](../scanner-py).

## How the verdict is decided

1. Run the battery over the snapshot: contract existence, ownership, supply
   sanity, honeypot transfer/approve simulation, holder concentration, burned
   supply, GoPlus reputation (honeypot / tax / owner permissions / source), pool
   integrity, liquidity, volume, trade-size-vs-depth, and tokenized-stock
   disclosure/divergence.
2. Sum the risk points.
3. **Any `danger` finding → NO.** Else score ≥ `nogoScore` → NO, ≥
   `cautionScore` → CAUTION, else GO. An explanation layer never overrides this
   gate.

```ts
import { runScan, DEFAULT_SETTINGS } from "@aegis/scanner";
import { fixtureByKey } from "@aegis/scanner/fixtures";

const report = runScan(fixtureByKey("honeypot")!.snapshot,
  { token: "0x…", quote: "USDG", amountUsd: 1000 }, DEFAULT_SETTINGS);

report.verdict; // "NO"
report.results;  // every finding + evidence
```

## Test

```bash
npm test -w @aegis/scanner
```
