import FirewallDemo from "@/components/FirewallDemo";
import ScannerDemo from "@/components/ScannerDemo";
import AgentsSection from "@/components/AgentsSection";
import StatsBoard from "@/components/StatsBoard";
import { GithubIcon, XIcon } from "@/components/Icons";
import { Logo } from "@/components/Logo";

const GITHUB = "https://github.com/aegisagentdev/aegis";
const X = "https://x.com/aegismcp";
const DOCS = "/docs";

export default function Home() {
  return (
    <>
      {/* ticker */}
      <div className="ticker">
        <div className="wrap">
          <div className="ca">
            <b>CA:</b> <span className="addr">soon</span>
          </div>
          <div className="tick-right">
            <span className="tick-new">
              <span style={{ color: "var(--green)" }}>● NEW</span> Robinhood Chain shipped
              agent-executed trading. Aegis ships the shield for it.
            </span>
          </div>
        </div>
      </div>

      {/* nav */}
      <nav>
        <div className="wrap">
          <div className="brand">
            <span className="mark"><Logo size={34} /></span> AEGIS
          </div>
          <div className="nav-links">
            <a href="#agents">Agents</a>
            <a href="#scanner">Scan a contract</a>
            <a href="#stats">Stats</a>
            <a href="#install">Install</a>
            <a href={DOCS}>Docs</a>
            <a className="ic" href={GITHUB} target="_blank" rel="noreferrer" aria-label="GitHub">
              <GithubIcon />
            </a>
            <a className="ic" href={X} target="_blank" rel="noreferrer" aria-label="X / Twitter">
              <XIcon />
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
            Every injection blocked.
            <br />
            <span className="glow">Every contract cleared.</span>
          </h1>
          <p className="sub">
            Aegis is a drop-in security layer for MCP agents. A <b>prompt-injection firewall</b>{" "}
            scans every tool response before your agent reads it. <b>Aegis Scan</b> checks the
            contract before your agent signs. Nothing malicious reaches the agent, nothing malicious
            leaves it — <b>GO / CAUTION / NO</b> in milliseconds, with on-chain receipts.
          </p>
          <div className="cta-row">
            <a className="btn btn-primary" href="#scanner">▸ Scan a contract</a>
            <a className="btn btn-ghost" href="#install">Download the agent</a>
          </div>

          <div className="stats">
            <div className="stat">
              <div className="n">2 gates</div>
              <div className="l">Injection firewall in, Aegis Scan out</div>
            </div>
            <div className="stat">
              <div className="n">21</div>
              <div className="l">Deterministic on-chain + market checks</div>
            </div>
            <div className="stat">
              <div className="n">0 LLM</div>
              <div className="l">No model decides the verdict — pure code, so it can&apos;t be jailbroken or hallucinate, and it&apos;s identical every run</div>
            </div>
            <div className="stat">
              <div className="n">&lt;5ms</div>
              <div className="l">Per-response scan, fully offline-capable</div>
            </div>
          </div>
        </div>
      </header>

      {/* agents */}
      <section id="agents">
        <div className="wrap">
          <div className="sec-head">
            <div className="sec-tag">The pipeline</div>
            <h2>Six specialized agents. One verdict.</h2>
            <p>
              Aegis is a pipeline of small, single-purpose agents. Each does one job, emits its own
              evidence, and hands off to the next. No agent can be talked out of its job by the text
              it is inspecting — the gate is code, not a prompt.
            </p>
          </div>
          <AgentsSection />
        </div>
      </section>

      {/* scanner demo — paste a contract */}
      <section id="scanner">
        <div className="wrap">
          <div className="sec-head">
            <div className="sec-tag">Live · way out</div>
            <h2>Paste a contract. Get a verdict.</h2>
            <p>
              Drop any ERC-20 address and pick a network. Aegis Scan pulls live GoPlus reputation and
              DexScreener market depth, runs the full deterministic battery, and returns a
              reproducible GO / CAUTION / NO with every finding — no mock, no LLM.
            </p>
          </div>
          <ScannerDemo />
        </div>
      </section>

      {/* firewall demo */}
      <section id="firewall">
        <div className="wrap">
          <div className="sec-head">
            <div className="sec-tag">Live · way in</div>
            <h2>Scan a tool response for injection</h2>
            <p>
              Paste anything an MCP tool might return — or try a preset attack. This runs the real{" "}
              <code>@aegis/firewall</code> on the server and shows the evidence behind the decision.
            </p>
          </div>
          <FirewallDemo />
        </div>
      </section>

      {/* stats */}
      <section id="stats">
        <div className="wrap">
          <div className="sec-head">
            <div className="sec-tag">Under the hood</div>
            <h2>What the scoring actually looks like</h2>
            <p>
              The verdict is a weighted sum of independent signals. Below is the real scoring table
              and a live count of scans run from this page — every figure is a property of the code,
              not a usage claim.
            </p>
          </div>
          <StatsBoard />
        </div>
      </section>

      {/* install / download the agent */}
      <section id="install">
        <div className="wrap">
          <div className="sec-head">
            <div className="sec-tag">Download the agent</div>
            <h2>One line. Then scan from your terminal.</h2>
            <p>
              Aegis Scan ships on PyPI as a self-contained agent skill — a CLI and an MCP server.
              Install it in one command and scan contracts from your own machine, or wire it into any
              MCP-compatible agent.
            </p>
          </div>
          <div className="term">
            <div className="term-bar">
              <i className="r" />
              <i className="y" />
              <i className="g" />
              <span>bash — aegis-scan</span>
            </div>
            <div className="term-body">
              <div><span className="c"># install from PyPI — one line</span></div>
              <div><span className="p">$</span> <span className="v">pip install aegis-scan</span></div>
              <div>&nbsp;</div>
              <div><span className="c"># scan a contract straight from the terminal</span></div>
              <div><span className="p">$</span> <span className="v">aegis scan 0x020bfc650a365f8bb26819deaabf3e21291018b4 --chain robinhood</span></div>
              <div><span className="c">  → Cash Cat (CASHCAT)   verdict: GO   risk score: 5</span></div>
              <div>&nbsp;</div>
              <div><span className="c"># or run the MCP server so any agent can call it</span></div>
              <div><span className="p">$</span> <span className="v">aegis-mcp</span></div>
              <div>&nbsp;</div>
              <div><span className="c"># firewall (Node) — guard every tool response</span></div>
              <div><span className="p">$</span> <span className="v">npm i @aegis/firewall</span></div>
            </div>
          </div>
        </div>
      </section>

      {/* skill coming soon */}
      <section id="soon">
        <div className="wrap">
          <div className="soon">
            <div>
              <span className="pill">Coming soon</span>
              <h3>The Aegis Skill for any AI agent</h3>
              <p>
                A one-install skill for Claude and any MCP agent: drop it in and your agent scans
                every contract and every tool response natively, before it acts — no glue code. The
                CLI and MCP server above are live today; the packaged neural-agent skill lands next.
              </p>
            </div>
            <a className="btn btn-primary" href={GITHUB} target="_blank" rel="noreferrer">
              ▸ Watch on GitHub
            </a>
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
            <span className="sbadge"><span className="l">aegis: firewall</span><span className="r">ON</span></span>
            <span className="sbadge"><span className="l">aegis: pre-trade</span><span className="r">GO/NO</span></span>
            <span className="sbadge"><span className="l">receipts</span><span className="r">on-chain</span></span>
            <span className="sbadge"><span className="l">license</span><span className="r">MIT</span></span>
          </div>
        </div>
      </section>

      {/* footer */}
      <footer>
        <div className="wrap">
          <div>
            <div className="brand" style={{ fontSize: 14 }}>
              <span className="mark"><Logo size={26} /></span> AEGIS
            </div>
            <div style={{ marginTop: 8, maxWidth: 440, lineHeight: 1.6 }}>
              Two-way security shield for agentic trading on Robinhood Chain — a prompt-injection
              firewall and Aegis Scan, a deterministic token-scanning skill. MIT-licensed.
            </div>
          </div>
          <div className="foot-links">
            <a className="ic" href={GITHUB} target="_blank" rel="noreferrer" aria-label="GitHub"><GithubIcon /></a>
            <a className="ic" href={X} target="_blank" rel="noreferrer" aria-label="X / Twitter"><XIcon /></a>
            <a href={DOCS}>Docs</a>
            <a href="#scanner">Scan</a>
          </div>
        </div>
      </footer>
    </>
  );
}
