# FAQ

## General

**Q: Does Aegis execute trades?**
No. Aegis is strictly read-only. It inspects on-chain state via `eth_call` and `eth_getCode` — both are read operations. It never signs transactions, holds private keys, or moves funds.

**Q: Is a GO verdict a guarantee the token is safe?**
No. GO means "no automated red flags were found by the checks that ran." The scanner cannot predict future actions (an owner minting supply, a liquidity provider removing funds), and it does not yet cover every possible attack vector. Always verify addresses against official sources before signing.

**Q: Does it work without an Anthropic API key?**
Yes. Without a key, the AI summary falls back to a built-in template. The verdict and all checks work identically — the AI layer only explains findings, it never decides the verdict.

## Technical

**Q: Why not use web3.py?**
Aegis uses a minimal `httpx`-based JSON-RPC client with precomputed function selectors. This keeps the install to ~5 dependencies, makes the surface auditable, and avoids the complexity of a full web3 stack for what amounts to a handful of `eth_call` and `eth_getCode` calls.

**Q: How does the honeypot check work?**
It simulates a `transfer(deadAddress, 1)` via `eth_call` — a read-only simulation that does not actually execute a transaction. If the call reverts (typically with "transfer blocked" or similar), it's a strong signal that the token blocks transfers for non-whitelisted addresses.

**Q: What's the difference between CAUTION and NO-GO?**
CAUTION means the aggregate risk score crossed the caution threshold (default 25) but no single finding is blocking. NO-GO means either a DANGER-severity finding was found (e.g., honeypot, no contract code) or the aggregate score crossed the no-go threshold (default 60).

**Q: Can I add my own checks?**
Yes. See [CONTRIBUTING.md](../CONTRIBUTING.md). Create a class with an `id` attribute and an `async def run(self, ctx) -> list[CheckResult]` method, register it in `default_checks()`, and add tests.

## Robinhood Chain

**Q: Is Robinhood Chain the same as Robinhood (the brokerage)?**
Robinhood Chain is an Arbitrum Orbit L2 launched by Robinhood. It's a separate blockchain network, not the Robinhood mobile app. Stock tokens on the chain are tokenized debt instruments, not the equities traded on the brokerage platform.

**Q: What is FCFS sequencing?**
First-come-first-served. Transactions are ordered by arrival time at the sequencer, not by gas price. This prevents the classic gas-priority sandwich attack but shifts MEV to latency-based competition.

**Q: Can liquidity be removed on Robinhood Chain?**
Yes. Uniswap V3 on Robinhood Chain uses standard remove-liquidity calls. LP providers can withdraw their liquidity at any time. This is why Aegis checks pool depth and flags thin liquidity.
