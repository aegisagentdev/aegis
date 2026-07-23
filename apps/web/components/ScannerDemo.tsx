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
  verdict: "GO" | "CAUTION" | "NO-GO" | "UNKNOWN";
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
interface TokenOpt { key: string; label: string; address: string; blurb: string }
interface ChainOpt { key: string; label: string; live: boolean }

function money(n?: number) {
  if (n == null) return "—";
  if (n >= 1e6) return `$${(n / 1e6).toFixed(2)}M`;
  if (n >= 1e3) return `$${(n / 1e3).toFixed(1)}k`;
  return `$${n.toLocaleString(undefined, { maximumFractionDigits: 6 })}`;
}

const inputStyle: React.CSSProperties = {
  width: "100%", background: "var(--panel)", border: "1px solid var(--line-2)", borderRadius: 4,
  color: "var(--text)", fontFamily: "var(--mono)", fontSize: 13, padding: 12,
};

// A well-known safe token per chain, so "scan live" works on first click.
const SAMPLE_ADDR: Record<string, string> = {
  ethereum: "0x6b175474e89094c44da98b954eedeac495271d0f", // DAI
  base: "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913", // USDC
  bsc: "0xe9e7cea3dedca5984780bafc599bd69add087d56", // BUSD
};

export default function ScannerDemo() {
  const [mode, setMode] = useState<"live" | "sample">("live");
  const [tokens, setTokens] = useState<TokenOpt[]>([]);
  const [chains, setChains] = useState<ChainOpt[]>([]);
  const [token, setToken] = useState("honeypot");
  const [address, setAddress] = useState("0x6b175474e89094c44da98b954eedeac495271d0f");
  const [chain, setChain] = useState("ethereum");
  const [amount, setAmount] = useState(1000);
  const [rep, setRep] = useState<Report | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch("/api/scan").then((r) => r.json()).then((d) => {
      setTokens(d.tokens ?? []);
      setChains(d.chains ?? []);
    }).catch(() => {});
  }, []);

  async function run() {
    setLoading(true);
    setRep(null);
    try {
      const payload = mode === "live" ? { address, chain, amountUsd: amount } : { token, amountUsd: amount };
      const r = await fetch("/api/scan", {
        method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(payload),
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
      <div className="seg">
        <button className={mode === "live" ? "on" : ""} onClick={() => setMode("live")}>▸ Live contract address</button>
        <button className={mode === "sample" ? "on" : ""} onClick={() => setMode("sample")}>Sample token</button>
      </div>
      <div className="demo-grid">
        <div className="demo-in">
          {mode === "live" ? (
            <>
              <label>contract address</label>
              <input style={inputStyle} spellCheck={false} value={address}
                onChange={(e) => setAddress(e.target.value)} placeholder="0x…" />
              <label>network</label>
              <select value={chain} onChange={(e) => { setChain(e.target.value); if (SAMPLE_ADDR[e.target.value]) setAddress(SAMPLE_ADDR[e.target.value]!); }}>
                {chains.map((c) => (
                  <option key={c.key} value={c.key}>{c.label}{c.live ? "" : " (no reputation data)"}</option>
                ))}
              </select>
              <p style={{ fontSize: 11.5, color: "var(--muted-2)" }}>
                Real scan over live GoPlus + DexScreener data. Paste any ERC-20; unsupported chains return UNKNOWN.
              </p>
            </>
          ) : (
            <>
              <label>sample token</label>
              <select value={token} onChange={(e) => setToken(e.target.value)}>
                {tokens.map((t) => (<option key={t.key} value={t.key}>{t.label}</option>))}
              </select>
              <p style={{ fontSize: 12, color: "var(--muted-2)" }}>{tokens.find((t) => t.key === token)?.blurb}</p>
            </>
          )}
          <label>trade size (usd)</label>
          <input type="number" min={1} value={amount} onChange={(e) => setAmount(Number(e.target.value))} style={inputStyle} />
          <button className="btn btn-primary" onClick={run} disabled={loading}>
            {loading ? "scanning…" : "▸ scan token"}
          </button>
        </div>
        <div className="demo-out">
          <label>pre-trade verdict</label>
          {!rep ? (
            <div className="out-empty">{loading ? "querying on-chain reputation + market…" : "Scan a contract to see the verdict."}</div>
          ) : rep.error ? (
            <div className="out-empty" style={{ color: "var(--red)" }}>{rep.error}</div>
          ) : (
            <div style={{ marginTop: 12 }}>
              <span className={`verdict ${vClass}`}>{rep.verdict}</span>
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
