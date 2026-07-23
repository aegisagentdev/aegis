# scanner-py — Aegis pre-trade scanner (Python engine)

This is the **production data + engine layer** for the pre-trade scanner,
vendored from [Hood Trade](https://github.com/qumiann/hoodtrade) (MIT) into the
Aegis monorepo. It is the real thing: live RPC reads, GoPlus and DexScreener
enrichment, the deterministic check battery, and an **MCP server** so any
agent (Claude Desktop/Code, Cursor, Cline, custom SDK agents) can call the
scanner as a tool.

The TypeScript [`@aegis/scanner`](../scanner) is a faithful port of this engine's
decision logic used by the web demo; this package is what you run in production.

## Install & run

```bash
cd packages/scanner-py
pip install -e ".[mcp,ai]"

# CLI
hoodtrade scan 0xTokenAddress --chain robinhood --amount-usd 1000

# MCP server (stdio) — expose scan_token / check_rpc / list_chains to an agent
hoodtrade-mcp
```

## How it fits Aegis

Aegis is a two-way shield: `@aegis/firewall` guards the way **in** (prompt
injection in MCP tool responses), this scanner guards the way **out** (the
token/trade an agent is about to sign). Both emit the same GO / block style
verdict with on-chain evidence.

## Attribution

MIT. Copyright (c) 2026 Hood Trade contributors. See `NOTICE.md` at the repo
root. The module is kept as-is (`hoodtrade` package name intact) so upstream
imports and the MCP entry point continue to work unchanged.
