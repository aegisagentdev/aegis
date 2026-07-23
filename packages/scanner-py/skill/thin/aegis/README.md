# Aegis skill — thin (latest)

A downloadable [Agent Skill](https://aegismcp.io) that lets a Claude-style agent scan a token
for safety before you buy. This is the **thin** build: tiny, and it always installs the newest
Aegis from PyPI.

## Install

1. Unzip this archive.
2. Move the `aegis/` folder into your agent's skills directory:
   - Claude Code: `~/.claude/skills/`
3. Restart / reload the agent. It will read `SKILL.md` and use Aegis when you ask about
   token safety.

The first scan runs `pip install aegis` if the CLI isn't present. Requires internet + Python.

## Use

Just ask your agent, e.g.:

> Scan `0x87E1Ed2aDe9Db5DEA0E805f296B796219A05636B` on Robinhood Chain before I buy.

You'll get a **GO / CAUTION / NO-GO** verdict with the on-chain evidence behind it.

## Thin vs offline build

- **Thin (this one):** smallest download, always the latest version, needs internet on first run.
- **Offline:** ships the package and its dependencies inside the archive, installs without PyPI —
  bigger download, pinned to one version. Get it at https://aegismcp.io

Read-only. Aegis never signs, holds funds, or trades.
