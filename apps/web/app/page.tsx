import CopyCA from "@/components/CopyCA";
import FirewallDemo from "@/components/FirewallDemo";
import ScannerDemo from "@/components/ScannerDemo";

const CA = "0x5df08b1a2b3c4d5e6f708192a3b4c5d6e7f80912";
const GITHUB = "https://github.com/hoodtradeprofile/aegis";
const X = "https://x.com/aegismcp";

export default function Home() {
  return (
    <>
      {/* ticker */}
      <div className="ticker">
        <div className="wrap">
          <div className="ca">
            <b>CA:</b>
            <span className="addr">{CA}</span>
            <CopyCA address={CA} />
          </div>
          <div style={{ whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
            <span style={{ color: "var(--green)" }}>● NEW</span> Robinhood Chain shipped agent-executed
            trading. Aegis ships the shield for it.
          </div>
        </div>
      </div>

      {/* nav */}
      <nav>
        <div className="wrap">
          <div className="brand">
            <span className="mark">◇</span> AEGIS
          </div>
          <div className="nav-links">
            <a href="#firewall">Firewall</a>
            <a href="#scanner">Scanner</a>
            <a href="#how">How it works</a>
            <a href="#receipts">Receipts</a>
            <a className="ic" href={GITHUB} target="_blank" rel="noreferrer">
              GitHub
            </a>
            <a className="ic" href={X} target="_blank" rel="noreferrer">
              X
            </a>
          </div>
        </div>
      </nav>

      {/* hero */}
      <header className="hero">
        <div className="wrap">
          <span className="eyebrow">
            <span className="dot" /> Two-way shield for agentic trading · Robinhood Chain
          </span>
          <h1>
            Stop bad input.
            <br />
            <span className="glow">Stop bad trades.</span>
          </h1>
          <p className="sub">
            Aegis is a drop-in security layer for MCP agents. A <b>prompt-injection firewall</b>{" "}
            scans every tool response before your agent reads it. A deterministic{" "}
            <b>pre-trade scanner</b> checks the token before your agent signs. Nothing malicious
            reaches the agent, nothing malicious leaves it — <b>GO / CAUTION / NO-GO</b> in
            milliseconds, with on-chain receipts.
          </p>
          <div className="cta-row">
            <a className="btn btn-primary" href="#firewall">
              ▸ Try the live demo
            </a>
            <a className="btn btn-ghost" href={GITHUB} target="_blank" rel="noreferrer">
              View source
            </a>
          </div>

          <div className="stats">
            <div className="stat">
              <div className="n">2 gates</div>
              <div className="l">Injection firewall in, pre-trade scanner out</div>
            </div>
            <div className="stat">
              <div className="n">21</div>
              <div className="l">Deterministic on-chain + market checks</div>
            </div>
            <div className="stat">
              <div className="n">0 LLM</div>
              <div className="l">Verdicts decided by rules, not a model</div>
            </div>
            <div className="stat">
              <div className="n">&lt;5ms</div>
              <div className="l">Per-response scan, fully offline-capable</div>
            </div>
          </div>
        </div>
      </header>

      {/* two gates */}
      <section>
        <div className="wrap">
          <div className="sec-head">
            <div className="sec-tag">The shield</div>
            <h2>One agent. Two ways to get hurt. Two gates.</h2>
            <p>
              An agent that reads untrusted data and signs transactions has two attack surfaces.
              Aegis covers both with deterministic, auditable gates — the same GO/block philosophy
              on each side.
            </p>
          </div>
          <div className="two-col">
            <div className="gate-card">
              <div className="k">
                Way in <span className="arrow">→</span> what the agent reads
              </div>
              <h3>Prompt-injection firewall</h3>
              <ul>
                <li>Decodes base64 / hex / unicode-escape layers and strips zero-width cloaking before scanning.</li>
                <li>Heuristics for instruction-override, role hijack, exfiltration, tool-call and embedded-transaction directives.</li>
                <li>Deterministic allow / flag / block with a sanitized copy and the evidence behind every decision.</li>
                <li>Drop-in proxy over any MCP server — Anthropic, OpenAI, or fully offline.</li>
              </ul>
            </div>
            <div className="gate-card">
              <div className="k">
                Way out <span className="arrow">→</span> what the agent signs
              </div>
              <h3>Pre-trade safety scanner</h3>
              <ul>
                <li>Simulates transfer/approve to catch honeypots; reads holder concentration, burned supply and pool integrity.</li>
                <li>Corroborates with GoPlus reputation: tax, mint, pausable, blacklist, owner-can-rewrite-balance.</li>
                <li>Sizes the trade against pool depth and flags tokenized-stock (RIF) price divergence.</li>
                <li>Any DANGER finding forces NO-GO — the gate a model can never override.</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* firewall demo */}
      <section>
        <div className="wrap">
          <div className="sec-head">
            <div className="sec-tag">Gate 1 · live</div>
            <h2>Scan a tool response for injection</h2>
            <p>
              Paste anything an MCP tool might return — or try a preset attack. This runs the real{" "}
              <code>@aegis/firewall</code> on the server, no mock.
            </p>
          </div>
          <FirewallDemo />
        </div>
      </section>

      {/* scanner demo */}
      <section>
        <div className="wrap">
          <div className="sec-head">
            <div className="sec-tag">Gate 2 · live</div>
            <h2>Scan a token before the swap</h2>
            <p>
              Pick a Robinhood Chain token and a trade size. This runs the real{" "}
              <code>@aegis/scanner</code> battery and returns the deterministic verdict with every
              finding.
            </p>
          </div>
          <ScannerDemo />
        </div>
      </section>

      {/* how it works */}
      <section id="how">
        <div className="wrap">
          <div className="sec-head">
            <div className="sec-tag">How it works</div>
            <h2>Install once. Both gates on.</h2>
            <p>Wrap your MCP server with the proxy and expose the scanner as a tool. That&apos;s it.</p>
          </div>
          <div className="term">
            <div className="term-bar">
              <i className="r" />
              <i className="y" />
              <i className="g" />
              <span>bash — aegis</span>
            </div>
            <div className="term-body">
              <div>
                <span className="c"># way in: firewall proxy in front of any MCP server</span>
              </div>
              <div>
                <span className="p">$</span> <span className="v">npm i @aegis/firewall</span>
              </div>
              <div>&nbsp;</div>
              <div>
                <span className="c"># way out: pre-trade scanner as an MCP tool for your agent</span>
              </div>
              <div>
                <span className="p">$</span>{" "}
                <span className="v">pipx install &quot;aegis-scanner[mcp]&quot; &amp;&amp; hoodtrade-mcp</span>
              </div>
              <div>&nbsp;</div>
              <div>
                <span className="c"># verdicts are deterministic — same input, same GO / NO-GO, every time</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* receipts */}
      <section id="receipts">
        <div className="wrap">
          <div className="sec-head">
            <div className="sec-tag">On-chain receipts</div>
            <h2>Prove the agent acted on a real verdict</h2>
            <p>
              Every decision can be anchored to <code>AegisRegistry</code> on Robinhood Chain — a
              hash of the verdict, score and full report. Repos and agents point a safety badge at
              their latest receipt, so anyone can verify the guard was on and unmodified.
            </p>
          </div>
          <div className="badge-row">
            <span className="sbadge">
              <span className="l">aegis: firewall</span>
              <span className="r">ON</span>
            </span>
            <span className="sbadge">
              <span className="l">aegis: pre-trade</span>
              <span className="r">GO/NO-GO</span>
            </span>
            <span className="sbadge">
              <span className="l">receipts</span>
              <span className="r">on-chain</span>
            </span>
            <span className="sbadge">
              <span className="l">license</span>
              <span className="r">MIT</span>
            </span>
          </div>
        </div>
      </section>

      {/* footer */}
      <footer>
        <div className="wrap">
          <div>
            <div className="brand" style={{ fontSize: 14 }}>
              <span className="mark">◇</span> AEGIS
            </div>
            <div style={{ marginTop: 8, maxWidth: 420, lineHeight: 1.6 }}>
              Two-way security shield for agentic trading on Robinhood Chain. MIT-licensed. Built on{" "}
              Hood Trade + the Vault firewall design.
            </div>
          </div>
          <div style={{ display: "flex", gap: 22 }}>
            <a href={GITHUB} target="_blank" rel="noreferrer">
              GitHub
            </a>
            <a href={X} target="_blank" rel="noreferrer">
              X
            </a>
            <a href="#firewall">Demo</a>
          </div>
        </div>
      </footer>
    </>
  );
}
