# Hood Trade skill — offline (bundled)

A downloadable [Agent Skill](https://hoodtrade.pro) that lets a Claude-style agent scan a token
for safety before you buy. This is the **offline** build: Hood Trade `0.4.1` and all of its
dependencies are bundled in `wheels/`, so it installs **without reaching PyPI**.

## Install

1. Unzip this archive.
2. Move the `hoodtrade/` folder into your agent's skills directory:
   - Claude Code: `~/.claude/skills/`
3. Install the scanner from the bundled wheels (run from the `hoodtrade/` folder):

       pip install --no-index --find-links wheels hoodtrade

4. Restart / reload the agent. It reads `SKILL.md` and uses Hood Trade when you ask about token safety.

## Use

> Scan `0x87E1Ed2aDe9Db5DEA0E805f296B796219A05636B` on Robinhood Chain before I buy.

You'll get a **GO / CAUTION / NO-GO** verdict with the on-chain evidence behind it.

## What's bundled / compatibility

- Hood Trade `0.4.1` + every dependency, as wheels.
- Compiled dependency `pydantic-core` is included for **Linux (x86_64, aarch64), macOS
  (Apple Silicon + Intel), and Windows (x86_64)** on **Python 3.10 – 3.13**. Other platforms
  aren't covered — use the thin build instead.
- Version is **pinned** to `0.4.1`; it will not silently upgrade.

## Offline vs thin build

- **Offline (this one):** installs with no internet, pinned version, ~42 MB. Good for airgapped
  or reproducible setups.
- **Thin:** a few KB, always installs the latest from PyPI, needs internet. Get it at https://hoodtrade.pro

A scan itself still needs network access to reach the chain RPC and market data — "offline" refers
to installation, not to running a live scan.

Read-only. Hood Trade never signs, holds funds, or trades.
