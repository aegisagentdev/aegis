"use client";

import { useEffect, useState } from "react";

interface Finding {
  check: string;
  severity: "ok" | "info" | "warn" | "danger";
  score: number;
  title: string;
  detail: string;
}
interface Report {
  verdict: "GO" | "CAUTION" | "NO" | "UNKNOWN";
  score: number;
  tokenName?: string;
  tokenSymbol?: string;
  priceUsd?: number;
  liquidityUsd?: number;
  volume24h?: number;
  results: Finding[];
  notes: string[];
  live?: boolean;
  sources?: string[];
  error?: string;
}
interface ChainOpt { key: string; label: string; live: boolean }

function money(n?: number) {
  if (n == null) return "—";
  if (n >= 1e6) return `$${(n / 1e6).toFixed(2)}M`;
  if (n >= 1e3) return `$${(n / 1e3).toFixed(1)}k`;
  return `$${n.toLocaleString(undefined, { maximumFractionDigits: 6 })}`;
}

// GO / CAUTION / NO — display label for each internal verdict.
function verdictLabel(v: Report["verdict"]) {
  return v === "NO" ? "NO" : v;
}

const inputStyle: React.CSSProperties = {
  width: "100%", background: "var(--panel)", border: "1px solid var(--line-2)", borderRadius: 4,
  color: "var(--text)", fontFamily: "var(--mono)", fontSize: 13, padding: 12,
};

export default function ScannerDemo() {
  const [chains, setChains] = useState<ChainOpt[]>([]);
  const [address, setAddress] = useState("");
  const [chain, setChain] = useState("robinhood");
  const [amount, setAmount] = useState(1000);
  const [rep, setRep] = useState<Report | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch("/api/scan").then((r) => r.json()).then((d) => setChains(d.chains ?? [])).catch(() => {});
  }, []);

  async function run() {
    if (!address.trim()) {
      setRep({ verdict: "UNKNOWN", score: 0, results: [], notes: ["Paste a contract address first."], error: "Paste a contract address first." });
      return;
    }
    setLoading(true);
    setRep(null);
    try {
      const r = await fetch("/api/scan", {
        method: "POST", headers: { "content-type": "application/json" },
        body: JSON.stringify({ address: address.trim(), chain, amountUsd: amount }),
      });
      setRep(await r.json());
      window.dispatchEvent(new CustomEvent("aegis:scan"));
    } catch {
      setRep({ verdict: "UNKNOWN", score: 0, results: [], notes: ["Network error — try again."] });
    } finally {
      setLoading(false);
    }
  }

  const vClass = rep && !rep.error ? `v-${rep.verdict.toLowerCase().replace("-", "")}` : "";
  const shown = rep?.results?.filter((r) => r.severity !== "ok").slice(0, 8) ?? [];

  return (
    <div className="demo" id="scanner">
      <div className="demo-grid">
        <div className="demo-in">
          <label>contract address</label>
          <input style={inputStyle} spellCheck={false} value={address} autoComplete="off"
            onChange={(e) => setAddress(e.target.value)} placeholder="0x… paste any ERC-20 contract" />
          <label>network</label>
          <select value={chain} onChange={(e) => setChain(e.target.value)}>
            {chains.map((c) => (
              <option key={c.key} value={c.key}>{c.label}{c.live ? "" : " (no reputation data)"}</option>
            ))}
          </select>
          <label>trade size (usd)</label>
          <input type="number" min={1} value={amount} onChange={(e) => setAmount(Number(e.target.value))} style={inputStyle} />
          <button className="btn btn-primary" onClick={run} disabled={loading}>
            {loading ? "scanning…" : "▸ scan contract"}
          </button>
          <p style={{ fontSize: 11.5, color: "var(--muted-2)" }}>
            Real scan over live GoPlus + DexScreener data. Unsupported chains return UNKNOWN.
          </p>
        </div>
        <div className="demo-out">
          <label>pre-trade verdict</label>
          {!rep ? (
            <div className="out-empty">{loading ? "querying on-chain reputation + market…" : "Paste a contract and scan to see the verdict."}</div>
          ) : rep.error ? (
            <div className="out-empty" style={{ color: "var(--amber)" }}>{rep.error}</div>
          ) : (
            <div style={{ marginTop: 12 }}>
              <span className={`verdict ${vClass}`}>{verdictLabel(rep.verdict)}</span>
              <span className="score-pill">risk score {rep.score}</span>
              {rep.sources?.length ? <div style={{ fontSize: 11, color: "var(--muted-2)", marginTop: 8 }}>data: {rep.sources.join(" · ")}{rep.live ? " · live" : ""}</div> : null}
              <div className="token-meta">
                <div><div className="mk">token</div><div className="mv">{rep.tokenSymbol ?? "—"}</div></div>
                <div><div className="mk">price</div><div className="mv">{money(rep.priceUsd)}</div></div>
                <div><div className="mk">liquidity</div><div className="mv">{money(rep.liquidityUsd)}</div></div>
                <div><div className="mk">24h volume</div><div className="mv">{money(rep.volume24h)}</div></div>
              </div>
              {shown.map((f, i) => (
                <div key={i} className={`finding sev-${f.severity}`}>
                  <div className="ft"><span className="fid">{f.check}</span><span className="fw">+{f.score}</span></div>
                  <h4>{f.title}</h4>
                  <p>{f.detail}</p>
                </div>
              ))}
              {rep.notes?.length ? <p style={{ fontSize: 11.5, color: "var(--muted-2)", marginTop: 10 }}>{rep.notes.join(" ")}</p> : null}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
