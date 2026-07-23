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
}
interface TokenOpt {
  key: string;
  label: string;
  address: string;
  blurb: string;
}

function money(n?: number) {
  if (n == null) return "—";
  if (n >= 1e6) return `$${(n / 1e6).toFixed(2)}M`;
  if (n >= 1e3) return `$${(n / 1e3).toFixed(1)}k`;
  return `$${n.toLocaleString(undefined, { maximumFractionDigits: 6 })}`;
}

export default function ScannerDemo() {
  const [tokens, setTokens] = useState<TokenOpt[]>([]);
  const [token, setToken] = useState("honeypot");
  const [amount, setAmount] = useState(1000);
  const [rep, setRep] = useState<Report | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch("/api/scan")
      .then((r) => r.json())
      .then((d) => setTokens(d.tokens ?? []))
      .catch(() => {});
  }, []);

  async function run() {
    setLoading(true);
    try {
      const r = await fetch("/api/scan", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ token, amountUsd: amount }),
      });
      setRep(await r.json());
    } finally {
      setLoading(false);
    }
  }

  const vClass = rep ? `v-${rep.verdict.toLowerCase().replace("-", "")}` : "";
  const shown = rep?.results.filter((r) => r.severity !== "ok").slice(0, 8) ?? [];

  return (
    <div className="demo" id="scanner">
      <div className="demo-grid">
        <div className="demo-in">
          <label>token to scan (robinhood chain)</label>
          <select value={token} onChange={(e) => setToken(e.target.value)}>
            {tokens.map((t) => (
              <option key={t.key} value={t.key}>
                {t.label}
              </option>
            ))}
          </select>
          <p style={{ fontSize: 12, color: "var(--muted-2)" }}>
            {tokens.find((t) => t.key === token)?.blurb}
          </p>
          <label>trade size (usd)</label>
          <input
            type="number"
            value={amount}
            min={1}
            onChange={(e) => setAmount(Number(e.target.value))}
            style={{
              width: "100%",
              background: "var(--panel)",
              border: "1px solid var(--line-2)",
              borderRadius: 4,
              color: "var(--text)",
              fontFamily: "var(--mono)",
              fontSize: 13,
              padding: 12,
            }}
          />
          <button className="btn btn-primary" onClick={run} disabled={loading}>
            {loading ? "scanning…" : "▸ scan token"}
          </button>
        </div>
        <div className="demo-out">
          <label>pre-trade verdict</label>
          {!rep ? (
            <div className="out-empty">Pick a token and scan to see the verdict.</div>
          ) : (
            <div style={{ marginTop: 12 }}>
              <span className={`verdict ${vClass}`}>{rep.verdict}</span>
              <span className="score-pill">risk score {rep.score}</span>
              <div className="token-meta">
                <div>
                  <div className="mk">token</div>
                  <div className="mv">{rep.tokenSymbol ?? "—"}</div>
                </div>
                <div>
                  <div className="mk">price</div>
                  <div className="mv">{money(rep.priceUsd)}</div>
                </div>
                <div>
                  <div className="mk">liquidity</div>
                  <div className="mv">{money(rep.liquidityUsd)}</div>
                </div>
                <div>
                  <div className="mk">24h volume</div>
                  <div className="mv">{money(rep.volume24h)}</div>
                </div>
              </div>
              {shown.map((f, i) => (
                <div key={i} className={`finding sev-${f.severity}`}>
                  <div className="ft">
                    <span className="fid">{f.check}</span>
                    <span className="fw">+{f.score}</span>
                  </div>
                  <h4>{f.title}</h4>
                  <p>{f.detail}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
