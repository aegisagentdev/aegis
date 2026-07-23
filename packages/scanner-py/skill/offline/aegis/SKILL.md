---
name: aegis
description: Pre-trade safety scanner for Robinhood Chain and other EVM chains. Use whenever the user wants to know if a token is safe to buy or swap before signing — they paste a token contract address, ask "is this a rug / honeypot?", "scan 0x…", "should I buy this token", or want to check liquidity, ownership, transfer fees, or holder concentration before a trade. Returns a GO / CAUTION / NO verdict backed by on-chain evidence.
---

# Aegis — pre-trade safety scanner (offline build)

Aegis inspects a token contract and its market, then returns a **GO / CAUTION / NO**
verdict before the user signs a swap. It is **read-only**: it never signs, holds funds, or trades.
It inspects — the user decides.

This is the **offline** build: the package and its dependencies are bundled in `wheels/`, so it
installs without reaching PyPI. It is pinned to a specific version (see `wheels/`).

## When to use this skill

Trigger when the user:
- pastes a token contract address and asks whether it's safe to buy
- says "scan this token", "is this a honeypot / rug", "should I ape into 0x…"
- wants to check liquidity, ownership, transfer fees, or holder concentration before a trade

## Setup (once)

Check whether the scanner is already installed:

    aegis version

If that command is not found, install it from the bundled wheels — no internet needed.
Run this from **this skill's own directory** (the folder that contains `wheels/`):

    pip install --no-index --find-links wheels aegis

## How to run a scan

    aegis scan <TOKEN_ADDRESS> --chain <CHAIN> --json

- `<TOKEN_ADDRESS>` — 42-character `0x…` contract address.
- `--chain` — `robinhood` (default), `ethereum`, `base`, `arbitrum`, `bsc`, `polygon`, `optimism`, `avalanche` (aliases: `eth`, `arb`, `op`, `avax`…).
- `--amount <USD>` — intended trade size (default `1000`); affects the price-impact check.
- `--json` — machine-readable output. Always use this and parse the JSON.

Example:

    aegis scan 0x87E1Ed2aDe9Db5DEA0E805f296B796219A05636B --chain robinhood --json

The process **exit code is the verdict**: `0` = GO, `1` = CAUTION, `2` = NO.

## How to report back

From the JSON, read `verdict`, `risk_score`, `summary.headline` and `summary.key_risks`.
Then:
1. State the verdict plainly (GO / CAUTION / NO) and the risk score.
2. List the top 1–3 key risks in plain language.
3. Remind the user it is read-only and the decision is theirs.

Do **not** declare a token "safe" outright — report the verdict and the evidence behind it,
and let the user decide.

## Good to know

- On Robinhood Chain (a freshly-launched chain) thin liquidity and low volume are treated as
  **CAUTION**, not an automatic NO. Real security issues — honeypot, hidden transfer fee,
  mint capability, owner permissions — still force **NO** on any chain.
- Add `--strict` to block on thin liquidity even on new chains, or `--lenient` to relax those
  gates on any chain.
- Full docs: https://aegismcp.io · source: https://github.com/aegisagentdev/aegis
