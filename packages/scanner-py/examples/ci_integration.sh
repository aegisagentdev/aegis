#!/usr/bin/env bash
# Example: integrate Aegis into a CI pipeline.
# Block a deployment if the pre-trade check fails.

set -euo pipefail

TOKEN="${TOKEN_ADDRESS:?TOKEN_ADDRESS env var required}"
QUOTE="${QUOTE_ADDRESS:?QUOTE_ADDRESS env var required}"
AMOUNT="${TRADE_AMOUNT:-1000}"

echo "Running Aegis pre-trade scan..."
echo "  Token:  $TOKEN"
echo "  Quote:  $QUOTE"
echo "  Amount: \$$AMOUNT"

# Run scan in JSON mode without AI (faster, deterministic)
OUTPUT=$(aegis scan \
  --token "$TOKEN" \
  --quote "$QUOTE" \
  --amount "$AMOUNT" \
  --json \
  --no-ai 2>&1) || true

EXIT_CODE=${PIPESTATUS[0]:-$?}

echo "$OUTPUT"

case $EXIT_CODE in
  0)
    echo "✅ VERDICT: GO — proceeding"
    ;;
  1)
    echo "⚠️  VERDICT: CAUTION — review findings before proceeding"
    # Optionally: exit 1 to block on CAUTION
    ;;
  2)
    echo "🚫 VERDICT: NO-GO — blocking deployment"
    exit 1
    ;;
  *)
    echo "❌ Unexpected exit code: $EXIT_CODE"
    exit 1
    ;;
esac
