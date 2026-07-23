# Roadmap

## v0.2.0 (current)

- [x] Honeypot detection — `transfer()` and `approve()` simulation via `eth_call`
- [x] Holder concentration — self-holding and burned supply checks
- [x] GitHub Actions CI — ruff lint + pytest across Python 3.10-3.12
- [x] Extended test suite — 50 tests covering all check modules + CLI
- [x] Community docs — CONTRIBUTING, SECURITY, CHANGELOG, architecture
- [x] 15-check battery (up from 11 in v0.1)

## v0.3.0 (planned)

- [ ] **Tick-by-tick depth simulation** — full Uniswap V3 tick math for precise price impact
  estimation instead of the current first-order approximation
- [ ] **Bytecode pattern analysis** — detect proxies (EIP-1967), known exploit signatures,
  self-destruct patterns, and delegatecall misuse
- [ ] **Multi-pool routing** — scan all pools for a token pair, not just the one specified,
  and compare depth across venues
- [ ] **Watch mode** — `aegis watch --token 0x..` continuously monitors a token and
  alerts on state changes (owner change, liquidity removal, new pool)

## v0.4.0 (planned)

- [ ] **Live price oracles** — integrate Chainlink feeds on Robinhood Chain for real-time
  stock-token divergence measurement against underlying equity prices
- [ ] **Holder enumeration via indexer** — query Blockscout or Dune for full holder
  distribution, Gini coefficient, whale concentration
- [ ] **Historical analysis** — compare current check results against the token's state
  N blocks ago to detect sudden changes (liquidity drain, ownership transfer)

## v0.5.0 (planned)

- [ ] **Telegram bot** — `/scan 0xToken 0xQuote 500` in a chat, get a verdict card back
- [ ] **Discord bot** — same interface for Discord servers
- [ ] **REST API** — hosted endpoint for integrating Aegis into other tools
- [ ] **Dashboard** — web UI for scanning with a richer visual presentation

## Future / Research

- [ ] **Simulation sandbox** — fork the chain state and simulate the actual swap to measure
  realized price impact, not estimated
- [ ] **Cross-chain support** — extend to other Arbitrum Orbit chains, Base, and mainnet
- [ ] **ML-based pattern detection** — train on labeled honeypot/rug datasets for bytecode
  classification beyond heuristic patterns
- [ ] **Portfolio mode** — scan all tokens in a wallet and generate a risk report
