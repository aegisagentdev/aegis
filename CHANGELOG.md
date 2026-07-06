# Changelog

All notable changes to Hood Trade are documented here.

## [0.4.0] - 2026-07-06

### Added
- **MCP server** (`hoodtrade-mcp`): exposes the scanner to any MCP-compatible agent (Claude Desktop, Claude Code, Cursor, Cline, Windsurf, custom agents) via the `scan_token`, `check_rpc` and `list_chains` tools. Install with `pip install "hoodtrade[mcp]"`. Read-only; the agent gets the same verdict the CLI produces.

### Changed
- Extracted the chain registry, settings resolution and new-chain leniency into `hoodtrade.networks` so every front-end (CLI, MCP server, future bots/API) produces an identical verdict. Added a high-level `hoodtrade.networks.scan_token()` async entry point.

## [0.3.0] - 2026-07-06

### Added
- **New-chain leniency**: on a freshly-launched chain (Robinhood Chain by default) the market-maturity signals — thin liquidity, low volume, trade-size impact — now produce CAUTION instead of an automatic NO-GO. Security signals (honeypot, hidden fee, mint, owner permissions) still block on any chain. New `--strict` / `--lenient` CLI flags and `HOODTRADE_LIQ_DANGER_BELOW`, `HOODTRADE_LIQ_WARN_BELOW`, `HOODTRADE_BLOCK_ON_THIN_LIQUIDITY`, `HOODTRADE_BLOCK_ON_HIGH_IMPACT` settings.
- PyPI packaging metadata (trove classifiers); first release published to PyPI (`pip install hoodtrade`).

### Fixed
- Demo report (`hoodtrade scan --demo`) showed a NO-GO badge under a CAUTION headline; the sample transfer-fee finding is now a warning, so the verdict and summary agree.

## [0.2.0] - 2026-07-02

### Added
- **Honeypot detection** (`CONTRACT-HONEYPOT`, `CONTRACT-APPROVE`): simulates `transfer()` and `approve()` via `eth_call` to detect tokens that block selling.
- **Holder concentration** (`CONC-SELF`, `CONC-BURNED`): flags tokens where the contract self-holds a large share of supply or where most supply is burned (thin float risk).
- **GitHub Actions CI**: lint (ruff) and test (pytest) on push/PR across Python 3.10-3.12.
- Extended test suite: pool checks, execution checks, CLI, honeypot, concentration (40+ tests).
- `CONTRIBUTING.md`, `SECURITY.md`, architecture documentation.
- `examples/` directory with sample scan output.

### Changed
- Default check battery expanded from 11 to 15 checks.
- README rewritten with architecture diagram, full check reference table, and badges.

## [0.1.0] - 2026-07-02

### Added
- Initial release: 11-check battery covering contract, pool, execution, and stock-token safety.
- Deterministic verdict engine (GO / CAUTION / NO-GO).
- Claude-powered risk summary with offline template fallback.
- CLI with `scan`, `doctor`, and `version` commands.
- Rich terminal output with colored verdict panel.
