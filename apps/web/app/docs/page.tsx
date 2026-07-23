import type { Metadata } from "next";
import { GithubIcon, XIcon } from "@/components/Icons";
import { Logo } from "@/components/Logo";

export const metadata: Metadata = {
  title: "Aegis Docs — the two-way shield for agentic trading",
  description: "Documentation for Aegis: the prompt-injection firewall and Aegis Scan token-scanning skill for MCP agents on Robinhood Chain.",
};

const GITHUB = "https://github.com/aegisagentdev/aegis";
const X = "https://x.com/aegismcp";

const NAV = [
  { h: "Getting started", items: [["introduction", "Introduction"], ["quickstart", "Quickstart"], ["concepts", "Core concepts"]] },
  { h: "Aegis Scan", items: [["cli", "CLI usage"], ["mcp", "MCP server"], ["checks", "The check battery"], ["chains", "Supported networks"]] },
  { h: "Firewall", items: [["firewall", "Prompt-injection firewall"], ["action-guard", "Action guard"]] },
  { h: "More", items: [["receipts", "On-chain receipts"], ["faq", "FAQ"]] },
];

export default function Docs() {
  return (
    <div className="docs">
      <aside className="docs-side">
        <a className="docs-brand" href="/">
          <span className="mark"><Logo size={40} /></span> AEGIS <span className="docs-brand-sub">docs</span>
        </a>
        <nav>
          {NAV.map((g) => (
            <div className="docs-group" key={g.h}>
              <div className="docs-group-h">{g.h}</div>
              {g.items.map(([id, label]) => (
                <a key={id} href={`#${id}`}>{label}</a>
              ))}
            </div>
          ))}
        </nav>
        <div className="docs-side-foot">
          <a className="ic" href={GITHUB} target="_blank" rel="noreferrer" aria-label="GitHub"><GithubIcon /></a>
          <a className="ic" href={X} target="_blank" rel="noreferrer" aria-label="X"><XIcon /></a>
          <a href="/">← back to site</a>
        </div>
      </aside>

      <main className="docs-main">
        <div className="docs-body">
          <p className="docs-eyebrow">Documentation</p>
          <h1>Aegis</h1>
          <p className="docs-lead">
            A two-way security shield for agentic trading on Robinhood Chain. A prompt-injection
            firewall guards what your agent reads; <b>Aegis Scan</b> guards what your agent signs.
            Every verdict is deterministic code — no LLM in the decision path.
          </p>

          <h2 id="introduction">Introduction</h2>
          <p>
            An AI agent that both reads untrusted data and signs transactions has two attack
            surfaces. Aegis closes both with auditable gates:
          </p>
          <ul>
            <li><b>Way in</b> — the <a href="#firewall">firewall</a> scans every MCP tool response for prompt injection before your agent reads it.</li>
            <li><b>Way out</b> — <a href="#cli">Aegis Scan</a> checks a token contract and the proposed trade before your agent signs.</li>
          </ul>
          <p>Both return a verdict with the evidence behind it: <code>GO / CAUTION / NO</code> for trades, <code>allow / flag / block</code> for tool responses.</p>

          <h2 id="quickstart">Quickstart</h2>
          <p>Install the token-scanning skill from PyPI — one line:</p>
          <pre><code>{`pip install aegis-scan`}</code></pre>
          <p>Scan a contract straight from your terminal:</p>
          <pre><code>{`aegis scan 0x6b175474e89094c44da98b954eedeac495271d0f --chain ethereum
# → verdict: GO   risk score: 3`}</code></pre>
          <p>Add the firewall to a Node/MCP project:</p>
          <pre><code>{`npm i @aegis/firewall`}</code></pre>

          <h2 id="concepts">Core concepts</h2>
          <p>
            The verdict is a <b>weighted sum of independent signals</b>. Each check contributes risk
            points by severity (OK 0 · INFO 1 · WARN 3 · DANGER 10-weighted). Any single{" "}
            <code>DANGER</code> finding forces <code>NO</code>. Thresholds decide the rest — the same
            input always yields the same verdict, so it is reproducible and auditable.
          </p>

          <h2 id="cli">CLI usage</h2>
          <pre><code>{`# scan a token before you buy
aegis scan <TOKEN_ADDRESS> --chain ethereum --amount 1000

# JSON output for scripting (exit code: 0=GO, 1=CAUTION, 2=NO)
aegis scan <TOKEN_ADDRESS> --chain base --json

# check RPC connectivity
aegis doctor --chain robinhood`}</code></pre>

          <h2 id="mcp">MCP server</h2>
          <p>Expose Aegis Scan as a tool any MCP-compatible agent can call (Claude Desktop/Code, Cursor, Cline, or a custom SDK agent):</p>
          <pre><code>{`pip install "aegis-scan[mcp]"
aegis-mcp        # stdio transport`}</code></pre>
          <p>The agent gets the same verdict the CLI would — <code>scan_token</code>, <code>check_rpc</code>, and <code>list_chains</code> tools, read-only. It never signs, holds funds, or trades.</p>

          <h2 id="checks">The check battery</h2>
          <p>21 deterministic checks across six families:</p>
          <ul>
            <li><b>Contract</b> — code exists, ownership renounced, supply sanity.</li>
            <li><b>Honeypot</b> — simulated <code>transfer()</code> / <code>approve()</code> via read-only <code>eth_call</code>.</li>
            <li><b>Concentration</b> — self-held supply, burned float.</li>
            <li><b>Pool</b> — pool exists, pair integrity, in-range liquidity.</li>
            <li><b>Reputation</b> — GoPlus: honeypot, tax, mint, pausable, blacklist, owner-can-rewrite-balance.</li>
            <li><b>Market / execution</b> — liquidity, 24h volume, trade-size-vs-depth, tokenized-stock (RIF) divergence.</li>
          </ul>

          <h2 id="chains">Supported networks</h2>
          <p>
            The web scanner reads live GoPlus reputation and DexScreener market data for Ethereum,
            Base, BNB Chain, Arbitrum, Polygon, Optimism and Avalanche. For Robinhood Chain, run the
            CLI with an RPC endpoint for the full on-chain simulation.
          </p>

          <h2 id="firewall">Prompt-injection firewall</h2>
          <p>Scan a single tool response before your agent reads it:</p>
          <pre><code>{`import { scanText } from "@aegis/firewall";

const r = scanText(toolResponse, { source: { server: "dexscreener", tool: "get_token_info" } });
if (r.decision === "block") throw new Error(r.signals[0].title);`}</code></pre>
          <p>
            It decodes base64 / hex / unicode-escape layers, strips zero-width cloaking, then runs
            heuristics for instruction-override, role hijack, exfiltration, tool-call injection and
            embedded-transaction directives — returning <code>allow / flag / block</code> plus a
            sanitized copy of the text.
          </p>

          <h2 id="action-guard">Action guard</h2>
          <p>Inspect the transaction the agent is about to sign:</p>
          <pre><code>{`import { guardAction } from "@aegis/firewall";

const signals = guardAction(
  { kind: "approve", to: spender, amount },
  { allowlist: [knownRouter] },
);
if (signals.length) blockAndConfirm(signals);`}</code></pre>
          <p>Flags unlimited approvals, recipients off the operator allow-list, and single-call drains.</p>

          <h2 id="receipts">On-chain receipts</h2>
          <p>
            Any verdict can be anchored to <code>AegisRegistry</code> on Robinhood Chain — a hash of
            the verdict, score and full report. A third party can then verify the agent acted on a
            real, unmodified decision, and repos/agents can point a safety badge at their latest
            receipt.
          </p>

          <h2 id="faq">FAQ</h2>
          <p className="docs-q">What does “0 LLM” mean?</p>
          <p>
            No large language model participates in the verdict. The decision is pure deterministic
            code, so it cannot be jailbroken by a prompt injection, cannot hallucinate, and returns
            the identical result for the identical input. A model may optionally <i>explain</i> the
            findings, but it never overrides the gate.
          </p>
          <p className="docs-q">Does Aegis ever move funds?</p>
          <p>No. It is strictly read-only — it inspects and reports. You (or your agent) decide.</p>
          <p className="docs-q">Is it open source?</p>
          <p>Yes, MIT. Source: <a href={GITHUB} target="_blank" rel="noreferrer">github.com/aegisagentdev/aegis</a>.</p>

          <div className="docs-end">MIT · Aegis · <a href="/">aegismcp.io</a></div>
        </div>
      </main>
    </div>
  );
}
