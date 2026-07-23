# Robinhood Chain Reference

Technical reference for Robinhood Chain as it relates to Aegis's check battery.

## Overview

| Property | Value |
|----------|-------|
| Type | Arbitrum Orbit L2 |
| Settlement | Ethereum mainnet |
| Gas token | ETH |
| Native token | None |
| Sequencing | First-come-first-served (FCFS) |
| Mainnet launch | July 1, 2026 |
| Stock token trading | 24/7, 120+ countries (not US) |

## Key Protocols

### AMMs / DEXes

- **Uniswap V3** — primary public AMM. Standard `IUniswapV3Pool` interface:
  `slot0()`, `liquidity()`, `token0()`, `token1()`, `fee()`. Full remove-liquidity
  support.

- **Pleiades** — proprietary AMM with custom bonding curves. Non-standard pool
  interface; Aegis's pool checks may return INFO rather than precise readings.

- **dYdX Arcus** — perpetuals and spot DEX. Different trading model than AMM;
  Aegis's pool checks are not applicable here.

- **0x Protocol** — RFQ (request-for-quote) liquidity and aggregation. Off-chain
  order matching; Aegis cannot inspect 0x orders on-chain.

### Lending

- **Morpho** — lending protocol. Earn ~7% on USDG. Not directly relevant to
  pre-trade scanning but important context for the chain's DeFi ecosystem.

### Infrastructure

- **Chainlink** — oracle feeds for price data
- **LayerZero** — cross-chain bridging
- **Blockscout** — block explorer (API used for verified-source lookups)

## FCFS Sequencing

Robinhood Chain uses first-come-first-served transaction ordering at the sequencer
level. This has important implications for MEV:

**What it prevents:**
- Gas-priority sandwiching (the classic MEV attack on Ethereum mainnet)
- Priority fee auctions between competing bots

**What it does NOT prevent:**
- Latency-based ordering — whoever reaches the sequencer first gets executed first,
  creating a latency race
- Oracle-timing attacks — trades can be frontrun if oracle update timing is predictable
- Cross-domain MEV — arbitrage between Robinhood Chain and other chains

## Stock Tokens

Robinhood Chain's headline product is tokenized equities. Critical distinctions:

1. **Not shares** — they are debt instruments issued by Robinhood Assets (Jersey)
   Limited that track an equity price
2. **No ownership rights** — holding a tokenized AAPL does not make you an Apple
   shareholder
3. **Counterparty risk** — you hold an issuer obligation, not equity
4. **Jurisdictional restrictions** — not available in the US and several other
   jurisdictions
5. **24/7 trading** — the token trades around the clock, but the underlying equity
   market has fixed hours. During closure, the token price can diverge from fair value.

## RPC Interface

Aegis uses a standard Ethereum JSON-RPC interface. Required methods:

| Method | Purpose |
|--------|---------|
| `eth_chainId` | Verify correct network |
| `eth_getCode` | Check contract deployment |
| `eth_call` | Read contract state (ERC-20, Uniswap V3) |

No write operations. No signing. No transaction submission.
