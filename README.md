<div align="center">

# ◇ AEGIS

**A two-way security shield for agentic trading on Robinhood Chain.**

Stop bad input. Stop bad trades.

[Live demo](https://aegismcp.io) · [Firewall](packages/firewall) · [Scanner](packages/scanner) · [Contracts](contracts)

</div>

---

An agent that reads untrusted data **and** signs transactions has two attack
surfaces. Aegis covers both with deterministic, auditable gates — the same
GO/block philosophy on each side, decided by rules and never by an LLM.

```
   untrusted MCP tool output                          proposed swap
            │                                                │
            ▼                                                ▼
  ┌───────────────────┐                          ┌────────────────────┐
  │  @aegis/firewall  │   allow / flag / block    │   @aegis/scanner   │  GO / CAUTION / NO
  │  (way IN)         │ ────────────────────────▶ │   (way OUT)        │ ────────────────────▶ sign
  └───────────────────┘                          └────────────────────┘
     decode → detect → decide                       snapshot → battery → verdict
```

## The two gates

### Gate 1 — Prompt-injection firewall (`packages/firewall`)

Scans every MCP tool response before the agent reads it.

1. **Decode** — peels back base64 / hex / percent / unicode-escape layers,
   strips zero-width splitters, folds homoglyphs. The payload is judged by what
   it decodes to, so `aWdub3Jl…` is caught as the "ignore all previous" it hides.
2. **Detect** — heuristics for instruction-override, role hijack, exfiltration,
   tool-call injection, embedded-transaction directives, false-authority framing.
3. **Decide** — sum weights → allow / flag / block, with a sanitized copy and the
   evidence behind every decision. Plus an **action guard** for the way out:
   unlimited approvals, off-allow-list recipients, single-call drains.

### Gate 2 — Pre-trade safety scanner (`packages/scanner`, `packages/scanner-py`)

Checks the token before the agent signs.

- Simulates transfer/approve (honeypot), reads holder concentration, burned
  supply, pool integrity.
- Corroborates with GoPlus: tax, mint, pausable, blacklist, owner-can-rewrite.
- Sizes the trade against pool depth; flags tokenized-stock (RIF) price divergence.
- **Any DANGER finding forces NO** — the gate a model can never override.

The TypeScript `@aegis/scanner` powers the web demo; `packages/scanner-py` is the
production Python engine with live RPC + an MCP server (`aegis-mcp`).

### On-chain receipts (`contracts/AegisRegistry.sol`)

Anchor a hash of any verdict (kind, score, report hash) on Robinhood Chain so a
third party can verify the agent acted on a real, unmodified decision. Repos and
agents point a safety badge at their latest receipt.

## Monorepo layout

```
aegis/
├── apps/web           Next.js landing + two live, real demos
├── packages/firewall  TS prompt-injection firewall + action guard
├── packages/scanner   TS pre-trade scanner
├── packages/scanner-py Python engine + MCP server (CLI + agent skill)
└── contracts          AegisRegistry.sol — on-chain receipts + badges
```

## Develop

```bash
npm install
npm run dev          # web app on :3037
npm test             # firewall + scanner test suites
npm run build        # production build (what Vercel runs)
```

## License & attribution

MIT. The prompt-injection firewall is inspired by the design of [Vault](https://github.com/vaultmcp/vault) (MIT); see [`NOTICE.md`](NOTICE.md).
