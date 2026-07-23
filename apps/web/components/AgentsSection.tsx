/**
 * The Aegis pipeline framed as a roster of specialized agents. Each entry maps
 * to real code in packages/firewall or packages/scanner — this is a plain-English
 * view of the modules, not marketing invention.
 */

const AGENTS = [
  {
    idx: "AGENT 01",
    name: "Decoder",
    role: "Firewall · way in",
    desc: "Peels back base64, hex, percent and unicode-escape layers, strips zero-width splitters and folds homoglyphs so a hidden payload is judged by what it decodes to.",
    tags: ["base64", "hex", "zero-width", "homoglyph"],
  },
  {
    idx: "AGENT 02",
    name: "Heuristics",
    role: "Firewall · way in",
    desc: "Matches instruction-override, role hijack, exfiltration, tool-call injection and embedded-transaction directives — conservative enough to keep benign docs clean.",
    tags: ["override", "exfil", "role-hijack", "tool-call"],
  },
  {
    idx: "AGENT 03",
    name: "Action Guard",
    role: "Firewall · way out",
    desc: "Inspects the transaction the agent is about to sign: unlimited approvals, recipients off the operator allow-list, single-call drains.",
    tags: ["maxUint", "allow-list", "drain"],
  },
  {
    idx: "AGENT 04",
    name: "On-chain Prober",
    role: "Scanner · way out",
    desc: "Simulates transfer/approve via read-only eth_call to catch honeypots, and reads holder concentration, burned supply and pool integrity.",
    tags: ["honeypot", "concentration", "pool"],
  },
  {
    idx: "AGENT 05",
    name: "Reputation",
    role: "Scanner · way out",
    desc: "Corroborates on-chain signals with the GoPlus dataset: tax, mint authority, pausable transfers, blacklist, owner-can-rewrite-balance.",
    tags: ["GoPlus", "tax", "mint", "pausable"],
  },
  {
    idx: "AGENT 06",
    name: "Verdict",
    role: "Scanner · gate",
    desc: "Sums weighted findings into a deterministic GO / CAUTION / NO. Any DANGER finding forces NO — the gate a model can never override.",
    tags: ["deterministic", "GO/NO", "auditable"],
  },
];

export default function AgentsSection() {
  return (
    <div className="agents">
      {AGENTS.map((a) => (
        <div className="agent" key={a.idx}>
          <div className="idx">{a.idx}</div>
          <div className="an">
            <span className="g">◇</span> {a.name}
          </div>
          <div className="role">{a.role}</div>
          <p>{a.desc}</p>
          <div className="tags">
            {a.tags.map((t) => (
              <span key={t}>{t}</span>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
