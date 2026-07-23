# Notice & Attribution

Aegis merges and builds on two prior MIT-licensed projects. Aegis keeps their
copyright notices as required by the MIT license.

## Pre-trade scanner lineage — Hood Trade

The pre-trade safety scanner (`packages/scanner`, `packages/scanner-py`) is
derived from **Hood Trade** — a read-only pre-trade safety scanner for Robinhood
Chain and other EVM networks.

- Source: https://github.com/qumiann/hoodtrade
- License: MIT — Copyright (c) 2026 Hood Trade contributors

The deterministic check battery, severity weighting, and GO / CAUTION / NO-GO
verdict logic originate there. `packages/scanner-py` is the upstream Python
engine, vendored unchanged so the production backend and MCP server stay intact;
`packages/scanner` is a faithful TypeScript port used by the web demo.

## Firewall lineage — Vault (concept & interface)

The prompt-injection firewall (`packages/firewall`) is an independent
TypeScript implementation inspired by the design of **Vault**, an MCP
prompt-injection proxy.

- Reference: https://github.com/vaultmcp/vault
- License: MIT — Copyright (c) 2026 Vault contributors

Aegis re-implements the "scan every tool response, then guard the action"
approach in its own code. Where Vault code or datasets are used directly, they
remain under Vault's MIT license and are marked in-file.
