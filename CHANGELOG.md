# Changelog

All notable changes to Hood Trade are documented here.

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
