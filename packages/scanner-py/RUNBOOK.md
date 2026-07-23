# Runbook

Operational guide for running Aegis in production or CI environments.

## Prerequisites

- Python 3.10+
- A working Robinhood Chain JSON-RPC endpoint
- (Optional) Anthropic API key for Claude-powered summaries

## Installation

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e '.[ai]'
cp .env.example .env
```

## Health Check

```bash
aegis doctor
```

Expected output:
```
RPC: https://your-rpc-endpoint.example
chain id: <chain_id>
RPC reachable.
```

If this fails:
1. Verify `AEGIS_RPC_URL` is set correctly in `.env`
2. Check network connectivity to the RPC endpoint
3. Verify the endpoint supports `eth_chainId`, `eth_getCode`, `eth_call`

## Running a Scan

```bash
aegis scan \
  --token 0x<token_address> \
  --quote 0x<quote_address> \
  --amount <usd_amount> \
  --pool 0x<pool_address> \
  --direction buy
```

### Exit Codes

| Code | Verdict | Action |
|------|---------|--------|
| 0 | GO | No blocking issues found |
| 1 | CAUTION | Notable risks — review findings before signing |
| 2 | NO-GO / UNKNOWN | Blocking issues or insufficient data — do not proceed |

### CI Integration

```bash
aegis scan --token $TOKEN --quote $QUOTE --amount $AMOUNT --json --no-ai
exit_code=$?
if [ $exit_code -eq 2 ]; then
  echo "BLOCKED: pre-trade check failed"
  exit 1
fi
```

## Troubleshooting

### "RPC unreachable"

- Check if the RPC URL has a trailing slash issue
- Try a different RPC provider
- Verify HTTPS certificate validity

### "Chain id mismatch"

- You're connected to the wrong network
- Update `AEGIS_CHAIN_ID` or check your RPC configuration

### "No checks produced output"

- The RPC is reachable but not responding to `eth_call`
- The endpoint may not support the Arbitrum Orbit JSON-RPC extensions

### AI summary shows template instead of Claude

- Verify `ANTHROPIC_API_KEY` is set
- Verify `AEGIS_AI_ENABLED=true`
- Check that the `anthropic` package is installed (`pip install aegis[ai]`)
- Check API key validity at https://console.anthropic.com

## Performance

- A full 15-check scan with AI summary typically completes in 2-5 seconds
- Without AI (`--no-ai`), scans complete in <1 second
- RPC latency is the primary bottleneck; use a low-latency endpoint

## Monitoring

For continuous monitoring, run scans on a cron schedule:

```bash
# Check a critical token every 5 minutes
*/5 * * * * cd /path/to/aegis && .venv/bin/aegis scan \
  --token 0x... --quote 0x... --amount 1000 --json --no-ai \
  >> /var/log/aegis/scans.jsonl 2>&1
```
