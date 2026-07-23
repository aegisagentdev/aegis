# @aegis/firewall

A prompt-injection firewall for MCP tool responses, plus an action guard for
agentic trades. Deterministic, dependency-free, and auditable — no LLM decides
the gate.

## Two gates

**Way in — `scanText(untrusted)`** scans a single tool response before your
agent reads it:

1. **Decode** — peel back base64 / hex / percent / unicode-escape layers, strip
   zero-width splitters, fold homoglyphs. The payload is judged by what it
   decodes to.
2. **Detect** — heuristics for instruction-override, role hijack, exfiltration,
   tool-call injection, embedded-transaction directives, and false-authority
   framing.
3. **Decide** — sum signal weights → `allow` / `flag` / `block`, with a
   sanitized copy of the text and the evidence behind the decision.

```ts
import { scanText } from "@aegis/firewall";

const r = scanText(toolResponse, { source: { server: "dexscreener", tool: "get_token_info" } });
if (r.decision === "block") throw new Error(`aegis blocked: ${r.signals[0].title}`);
```

**Way out — `guardAction(proposedTx)`** inspects the transaction the agent is
about to sign: unlimited approvals, recipients off the operator allow-list, and
single-call drains.

```ts
import { guardAction } from "@aegis/firewall";

const signals = guardAction(
  { kind: "approve", to: spender, amount },
  { allowlist: [knownRouter] },
);
if (signals.length) blockAndAsk(signals);
```

## Test

```bash
npm test -w @aegis/firewall
```

## Attribution

Independent implementation inspired by the design of
[Vault](https://github.com/vaultmcp/vault) (MIT). See `NOTICE.md` at the repo
root.
