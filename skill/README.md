# Aegis Agent Skill

`aegis-scan/` is a drop-in **Agent Skill** — give it to any agent that follows the
`SKILL.md` convention (Claude and others) and it will scan a token before signing a
trade and screen untrusted tool output for prompt injection.

## Install

```bash
pip install aegis-scan          # the scanner CLI + MCP server
npm i @aegis/firewall           # the firewall (Node/MCP)
```

Then point your agent at this folder, or expose the scanner over MCP:

```bash
aegis-mcp                       # stdio MCP server: scan_token / check_rpc / list_chains
```

## Contents

- `aegis-scan/SKILL.md` — the skill: when to use it, how to scan, how to report back.
- `aegis-scan/reference.md` — verdict semantics, the 21-check battery, JSON shape.
- `aegis-scan/scripts/scan.sh` — thin wrapper: `scan.sh <ADDR> [chain] [amount]`.

Read-only. It inspects — the user decides. MIT.
