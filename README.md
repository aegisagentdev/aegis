# Hood Trade

[![CI](https://github.com/YarikRuuuu/hoodtrade/actions/workflows/ci.yml/badge.svg)](https://github.com/YarikRuuuu/hoodtrade/actions)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**A pre-trade safety scanner for [Robinhood Chain](https://docs.robinhood.com/chain/).**

Point it at a swap you're about to sign — it returns a **GO / CAUTION / NO-GO** verdict
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
- **Honeypot tokens** can let you buy but block sells — a `transfer()` that reverts for
  non-whitelisted addresses is the classic pattern.
- The headline product, **stock tokens, are tokenized debt instruments** (issued by
  Robinhood Assets (Jersey) Limited), not equity — with counterparty risk and 24/7 vs.
  market-hours divergence.
- FCFS sequencing blunts gas-auction sandwiching, but MEV shifts to a latency race and
  oracle-timing games; it isn't gone.

Hood Trade turns those into a checklist that runs in seconds before you sign.

## Architecture

```
CLI (typer+rich)  →  Engine (run_scan)  →  Check Battery (15 checks)
                                                 │
                                          ┌──────┴──────┐
                                          │   decide()  │  deterministic
                                          └──────┬──────┘
                                                 │
                                          ┌──────┴──────┐
                                          │ AI summary  │  Claude (optional)
                                          └─────────────┘
```

The **verdict is decided deterministically** by the engine — any `DANGER` finding forces NO-GO,
and summed risk scores trigger CAUTION / NO-GO thresholds. A Claude-powered summary then explains
the result in plain language — but **the AI never overrides the gate**. With no API key, the
summary falls back to a built-in template and the scanner works fully offline.

See [docs/architecture.md](docs/architecture.md) for the full design rationale.

## Check Reference

| ID | Area | What it checks | Severity range |
|---|---|---|---|
| `EXEC-CHAINID` | Execution | RPC chain-id matches configured value | OK / DANGER |
| `CONTRACT-EXISTS` | Contract | Token address has deployed code | OK / DANGER |
| `CONTRACT-OWNER` | Contract | Owner / admin key status | OK / WARN |
| `CONTRACT-SUPPLY` | Contract | Standard ERC-20 reads (name, symbol, totalSupply) | OK / WARN |
| `CONTRACT-HONEYPOT` | Honeypot | Simulated transfer() to dead address | OK / DANGER |
| `CONTRACT-APPROVE` | Honeypot | Simulated approve() call | OK / WARN |
| `CONC-SELF` | Concentration | Token contract self-holds supply | OK / WARN / DANGER |
| `CONC-BURNED` | Concentration | Burned supply ratio (thin float risk) | OK / WARN |
| `POOL-EXISTS` | Pool | Pool address has deployed code | OK / INFO / DANGER |
| `POOL-PAIR` | Pool | Pool pairs the expected token0/token1 | OK / DANGER |
| `POOL-LIQUIDITY` | Pool | Active in-range liquidity (Uniswap V3) | OK / DANGER |
| `EXEC-SIZE` | Execution | Trade size band vs. depth | OK / INFO / WARN |
| `STOCK-DISCLOSURE` | Stock token | Debt-instrument disclosure for equity tickers | WARN |
| `STOCK-DIVERGENCE` | Stock token | Off-hours / underlying price divergence | OK / INFO / WARN / DANGER |
| `EXEC-MEV` | Execution | FCFS sequencing context and residual MEV | INFO |

## Install

```bash
git clone https://github.com/YarikRuuuu/hoodtrade
cd hoodtrade
python -m venv .venv && source .venv/bin/activate
pip install -e '.[ai,dev]'      # drop [ai] if you don't want the Claude summary
cp .env.example .env            # set HOODTRADE_RPC_URL (and ANTHROPIC_API_KEY for AI)
```

**Requirements**: Python 3.10+. Core dependencies: httpx, pydantic, typer, rich. Optional: anthropic (for AI summaries).

## Usage

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

# Sell scan (checks the same battery, direction affects context)
hoodtrade scan \
  --token 0xTokenAddress \
  --quote 0xUSDGAddress \
  --amount 1000 \
  --direction sell

# JSON output for scripting / CI integration
hoodtrade scan --token 0x.. --quote 0x.. --amount 500 --json --no-ai

# Exit codes: 0 = GO, 1 = CAUTION, 2 = NO-GO/UNKNOWN
```

### Example output

```
╭─ Hood Trade verdict ─────────────────────────────╮
│  CAUTION   risk score 43                         │
╰──────────────────────────────────────────────────╯
Proceed carefully — the scanner found notable risks.

Key risks
  • Token has an active owner: An owner address can pause transfers…
  • Trade size: large (>= $100k): split or route via an aggregator…
  • AAPL may be a tokenized equity (debt instrument)

Verify yourself
  → Confirm the token and pool addresses against the official source.
  → Check the pool's real depth for your size on the DEX UI.
  → Set a tight slippage limit; split large orders.
```

See [examples/sample_output.md](examples/sample_output.md) for more scenarios including honeypot detection and JSON output.

## Configuration

All settings are environment variables (prefix `HOODTRADE_`) or `.env` entries — see
[`.env.example`](.env.example).

| Variable | Default | Description |
|---|---|---|
| `HOODTRADE_RPC_URL` | (placeholder) | JSON-RPC endpoint for Robinhood Chain |
| `HOODTRADE_CHAIN_ID` | (unset) | Pin expected chain id for RPC verification |
| `HOODTRADE_CAUTION_SCORE` | 25 | Risk score threshold for CAUTION verdict |
| `HOODTRADE_NOGO_SCORE` | 60 | Risk score threshold for NO-GO verdict |
| `HOODTRADE_AI_ENABLED` | true | Use Claude for risk summaries |
| `HOODTRADE_AI_MODEL` | claude-opus-4-8 | Claude model for AI summaries |
| `ANTHROPIC_API_KEY` | (unset) | Anthropic API key (needed only if AI enabled) |

## Development

```bash
ruff check src tests          # lint
ruff format --check src tests # format check
pytest -q                     # run tests (40+)
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to add new checks.

## Roadmap

- [ ] Tick-by-tick depth simulation (Uniswap V3 tick math for precise price impact)
- [ ] Live USD/equity price oracles for stock-token divergence measurement
- [ ] Holder-concentration via indexer (Blockscout / Dune API)
- [ ] Bytecode pattern analysis (proxy detection, known exploit signatures)
- [ ] Multi-venue routing comparison (Uniswap vs Pleiades vs 0x)
- [ ] Telegram / Discord bot interface
- [ ] Watch mode (continuous monitoring of a token)

## Scope & honesty

This is v0.2. What it does **not** do yet: a full tick-by-tick depth simulation, live
USD/equity price oracles (divergence thresholds apply only when a reference is supplied),
full holder-concentration via indexer, or bytecode pattern analysis. Those are on the
roadmap and are called out as `INFO` findings when skipped, never silently. A green verdict
means "no automated red flags," not "safe" — always verify addresses against official
sources before signing.

## License

MIT — see [LICENSE](LICENSE).
