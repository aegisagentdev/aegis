#!/usr/bin/env bash
# Thin wrapper: scan a token and print the JSON verdict.
# Usage: scan.sh <TOKEN_ADDRESS> [CHAIN] [AMOUNT_USD]
set -euo pipefail

ADDR="${1:?usage: scan.sh <TOKEN_ADDRESS> [chain] [amount_usd]}"
CHAIN="${2:-robinhood}"
AMOUNT="${3:-1000}"

if ! command -v aegis >/dev/null 2>&1; then
  echo "aegis not found — install with: pip install aegis-scan" >&2
  exit 127
fi

# Exit code is the verdict: 0=GO 1=CAUTION 2=NO
aegis scan "$ADDR" --chain "$CHAIN" --amount "$AMOUNT" --json
