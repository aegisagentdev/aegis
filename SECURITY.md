# Security Policy

## Scope

Hood Trade is a **read-only** pre-trade scanner. It never signs transactions, never holds private keys, and never moves funds. Its security surface is limited to:

- **RPC communication**: the scanner sends JSON-RPC read calls (`eth_call`, `eth_getCode`, `eth_chainId`) to the configured endpoint.
- **AI summary**: when enabled, findings are sent to the Anthropic API for summarization. The AI layer is strictly explanatory and cannot override the deterministic verdict.

## Reporting a vulnerability

If you find a security issue (e.g. a way to make the scanner produce a misleading verdict, or a data leak through the AI layer), please report it privately:

1. **Email**: Open an issue marked `[SECURITY]` in the title, or contact the maintainer directly.
2. **Do not** open a public issue with exploit details.

We aim to acknowledge reports within 48 hours and provide a fix or mitigation within 7 days.

## What is NOT a vulnerability

- The scanner producing a `GO` verdict for a token that later rugs — the scanner checks on-chain state at scan time and cannot predict future actions by contract owners.
- The AI summary disagreeing with your risk assessment — the AI explains findings but does not decide the verdict.
- RPC endpoint security — securing your RPC connection (HTTPS, authentication) is the operator's responsibility.
