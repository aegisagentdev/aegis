# Hood Trade

**A pre-trade safety scanner for [Robinhood Chain](https://docs.robinhood.com/chain/).**
Point it at a swap you're about to sign; it returns a **GO / CAUTION / NO-GO** verdict
with the on-chain evidence behind it.

Hood Trade is **read-only**. It never signs, never holds funds, never trades. It inspects —
you decide.

---

## Why

Robinhood Chain launched July 2026 as a permissionless Arbitrum-Orbit L2 with Uniswap,
Pleiades, 0x, dYdX's Arcus, and Morpho live from day one. A permissionless chain that is
days old is exactly where pre-trade checks matter most:

- Anyone can deploy a token; the one you're buying may be hours old.
- **Liquidity can be removed** — the Uniswap pool you trade into can be drained by whoever
  provided it.
- The headline product, **stock tokens, are tokenized debt instruments** (issued by
  Robinhood Assets (Jersey) Limited), not equity — with counterparty risk and 24/7 vs.
  market-hours divergence.
- FCFS sequencing blunts gas-auction sandwiching, but MEV shifts to a latency race and
  oracle-timing games; it isn't gone.

Hood Trade turns those into a checklist that runs in seconds before you sign.

## What it checks

| Area | Checks |
|---|---|
| **Contract** | code present · owner / renounced · standard ERC-20 reads · supply sanity |
| **Pool** | pool exists · pairs the tokens you think it does · active in-range liquidity |
| **Execution** | RPC chain-id pinning · trade size vs. depth band · FCFS/MEV context |
| **Stock tokens** | debt-instrument disclosure · off-hours / underlying divergence |

Each finding carries a severity and a risk-point contribution. The **verdict is decided
deterministically** by the engine (any `DANGER` finding, or the summed score crossing the
`CAUTION` / `NO-GO` thresholds). A Claude-powered summary then explains the result in plain
language — but **the AI never overrides the gate**; it only explains it. With no API key,
the summary falls back to a built-in template and the scanner works fully offline.

## Install

```bash
git clone https://github.com/OWNER/hoodtrade
cd hoodtrade
python -m venv .venv && source .venv/bin/activate
pip install -e '.[ai,dev]'      # drop [ai] if you don't want the Claude summary
cp .env.example .env            # set HOODTRADE_RPC_URL (and ANTHROPIC_API_KEY for AI)
```

## Use

```bash
# Check the RPC is reachable and see its chain id
hoodtrade doctor

# Scan a proposed buy
hoodtrade scan \
  --token 0xTokenAddress \
  --quote 0xUSDGAddress \
  --amount 2500 \
  --pool  0xPoolAddress \
  --direction buy

# Scripting: exit code encodes the verdict (0 GO, 1 CAUTION, 2 NO-GO/UNKNOWN)
hoodtrade scan --token 0x.. --quote 0x.. --amount 500 --json --no-ai
```

Example output:

```
╭─ Hood Trade verdict ─────────────────────────────╮
│  CAUTION   risk score 35                      │
╰──────────────────────────────────────────────╯
Proceed carefully — the scanner found notable risks.

Key risks
  • Token has an active owner: An owner address can pause transfers…
  • Trade size: large (>= $100k): split or route via an aggregator…

Verify yourself
  → Confirm the token and pool addresses against the official source.
  → Check the pool's real depth for your size on the DEX UI.
```

## Configuration

All settings are environment variables (prefix `HOODTRADE_`) or `.env` entries — see
[`.env.example`](.env.example). Key ones: `HOODTRADE_RPC_URL`, `HOODTRADE_CHAIN_ID` (pin it),
`HOODTRADE_CAUTION_SCORE` / `HOODTRADE_NOGO_SCORE`, `ANTHROPIC_API_KEY`.

## Development

```bash
ruff check src tests
pytest -q
```

## Scope & honesty

This is v0.1. What it does **not** do yet: a full tick-by-tick depth simulation, live
USD/equity price oracles (divergence thresholds apply only when a reference is supplied),
holder-concentration enumeration, or bytecode-level honeypot simulation. Those are on the
roadmap and are called out as `INFO` findings when skipped, never silently. A green verdict
means "no automated red flags," not "safe" — always verify addresses against official
sources before signing.

## License

MIT — see [LICENSE](LICENSE).
