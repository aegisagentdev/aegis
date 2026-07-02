# Check Reference

Detailed documentation for every check in the Hood Trade battery.

## Contract Checks

### CONTRACT-EXISTS

**Purpose**: Verify the token address has deployed bytecode.

An address with no code is an EOA (externally-owned account) or an undeployed address.
Buying a "token" with no contract is a guaranteed loss — there is nothing to sell back.

| Field | Value |
|-------|-------|
| Severity | OK / DANGER |
| Score range | 0 / 100 |
| RPC calls | `eth_getCode(token)` |

### CONTRACT-OWNER

**Purpose**: Check if the token has an active owner/admin key.

An owner can often pause transfers, mint supply, change fees, or blacklist addresses.
Ownership is not inherently malicious, but it is a live admin key the trader is trusting.

| Field | Value |
|-------|-------|
| Severity | OK / WARN |
| Score range | 0 / 15 |
| RPC calls | `eth_call(owner())`, `eth_call(getOwner())` |

### CONTRACT-SUPPLY

**Purpose**: Verify standard ERC-20 reads (name, symbol, totalSupply).

A token that doesn't implement standard ERC-20 reads can behave unpredictably in AMMs.
Zero total supply is unusual for a live tradable token.

| Field | Value |
|-------|-------|
| Severity | OK / WARN |
| Score range | 0 / 15-20 |
| RPC calls | `eth_call(name())`, `eth_call(symbol())`, `eth_call(totalSupply())` |

## Honeypot Checks

### CONTRACT-HONEYPOT

**Purpose**: Detect tokens that block selling.

Simulates `transfer(deadAddress, 1)` via `eth_call`. If the call reverts, the token
likely blocks transfers for non-whitelisted addresses — you can buy but cannot sell.

| Field | Value |
|-------|-------|
| Severity | OK / INFO / DANGER |
| Score range | 0 / 5 / 90 |
| RPC calls | `eth_call(transfer(0xdead, 1))` |

### CONTRACT-APPROVE

**Purpose**: Detect tokens that block approvals.

Simulates `approve(deadAddress, maxUint)`. Some honeypots block approval to prevent
selling via a DEX router.

| Field | Value |
|-------|-------|
| Severity | OK / WARN |
| Score range | 0 / 25 |
| RPC calls | `eth_call(approve(0xdead, 2^255))` |

## Concentration Checks

### CONC-SELF

**Purpose**: Flag tokens where the contract self-holds a large share of supply.

Common in tax/reflection tokens and sometimes a sign of unreleased supply controlled
by the deployer. >50% self-held is DANGER, >20% is WARN.

| Field | Value |
|-------|-------|
| Severity | OK / WARN / DANGER |
| Score range | 0 / 20 / 50 |
| RPC calls | `eth_call(totalSupply())`, `eth_call(balanceOf(token))` |

### CONC-BURNED

**Purpose**: Report burned supply ratio.

Checks balances at the zero address and the dead address. Nearly all supply burned means
the remaining float is extremely thin — small trades cause outsized price impact.

| Field | Value |
|-------|-------|
| Severity | OK / WARN |
| Score range | 0 / 15 |
| RPC calls | `eth_call(balanceOf(0x0))`, `eth_call(balanceOf(0xdead))` |

## Pool Checks

### POOL-EXISTS

**Purpose**: Verify the pool address has deployed bytecode.

| Field | Value |
|-------|-------|
| Severity | OK / INFO / DANGER |
| Score range | 0 / 5 / 80 |
| RPC calls | `eth_getCode(pool)` |

### POOL-PAIR

**Purpose**: Confirm the pool pairs the expected tokens.

A mismatched pool is a common way to route a victim into a look-alike token.

| Field | Value |
|-------|-------|
| Severity | OK / DANGER |
| Score range | 0 / 60 |
| RPC calls | `eth_call(token0())`, `eth_call(token1())` |

### POOL-LIQUIDITY

**Purpose**: Read active in-range liquidity (Uniswap V3).

Zero active liquidity means the pool is untradeable at spot — a market order will
get an extreme price or revert.

| Field | Value |
|-------|-------|
| Severity | OK / DANGER |
| Score range | 0 / 70 |
| RPC calls | `eth_call(liquidity())` |

## Execution Checks

### EXEC-CHAINID

**Purpose**: Verify the RPC reports the expected chain id.

A mismatch means you may be pointed at the wrong network or a spoofed RPC.

| Field | Value |
|-------|-------|
| Severity | OK / INFO / DANGER |
| Score range | 0 / 90 |
| RPC calls | `eth_chainId` |

### EXEC-SIZE

**Purpose**: Flag trades that are large relative to expected pool depth.

Big orders into thin books eat slippage and are targets for latency-MEV even on
an FCFS chain.

| Field | Value |
|-------|-------|
| Severity | OK / INFO / WARN |
| Score range | 0 / 8 / 20 |
| Bands | <$10k small, $10k-$100k medium, >$100k large |

### EXEC-MEV

**Purpose**: Provide context on FCFS sequencing and residual MEV risks.

Informational only — no blocking severity.

| Field | Value |
|-------|-------|
| Severity | INFO |
| Score range | 0 |

## Stock Token Checks

### STOCK-DISCLOSURE

**Purpose**: Flag potential tokenized equities with a debt-instrument disclosure.

Robinhood stock tokens are tokenized debt securities, not shares. They carry
issuer counterparty risk and are restricted in several jurisdictions.

| Field | Value |
|-------|-------|
| Severity | WARN |
| Score range | 15 |
| Heuristic | Symbol matches common equity ticker patterns |

### STOCK-DIVERGENCE

**Purpose**: Measure off-hours price divergence vs. underlying equity.

Without a live reference price, emits an informational warning about off-hours risk.
With a reference, computes basis-point divergence and escalates.

| Field | Value |
|-------|-------|
| Severity | OK / INFO / WARN / DANGER |
| Score range | 0 / 5 / 20 / 45 |
| Thresholds | 150bps warn, 500bps danger (configurable) |
