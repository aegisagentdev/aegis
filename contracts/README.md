# contracts — AegisRegistry

`AegisRegistry.sol` anchors tamper-evident receipts for Aegis decisions on
Robinhood Chain.

Aegis decides two things off-chain, deterministically:

- **Firewall** — allow / flag / block on an MCP tool response.
- **Scanner** — GO / CAUTION / NO on a token before a swap.

The registry stores a compact commitment of a decision (`verdict`, `score`, and
`keccak256` of the full report) so anyone can later prove an agent acted on a
real, unmodified verdict. Repos and agents can point a **badge** at their latest
receipt — the on-chain equivalent of the safety badge shown on the site.

Only hashes live on-chain; the full report stays off-chain and is proven by
preimage via `verify(receiptId, reportHash)`.

## Layout

- `src/AegisRegistry.sol` — the registry (receipts + badges + verification).

Build with Foundry (`forge build`) or Hardhat; no dependencies beyond the
Solidity ^0.8.24 compiler.

MIT — the on-chain-receipt design follows Vault's `VaultReputation` approach
(MIT). See `NOTICE.md`.
