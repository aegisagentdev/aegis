# Notice & Attribution

Aegis is MIT-licensed (see `LICENSE`). Copyright (c) 2026 Aegis contributors.

## Firewall lineage — Vault (design inspiration)

The prompt-injection firewall (`packages/firewall`) is an independent
TypeScript implementation inspired by the published design of **Vault**, an MCP
prompt-injection proxy.

- Reference: https://github.com/vaultmcp/vault
- License: MIT — Copyright (c) 2026 Vault contributors

Aegis re-implements the "scan every tool response, then guard the action"
approach in its own code. Where any Vault code or dataset is used directly it
remains under Vault's MIT license and is marked in-file. As of this release the
firewall is a clean-room implementation; this notice is kept for provenance.
