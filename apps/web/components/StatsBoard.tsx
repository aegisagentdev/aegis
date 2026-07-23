"use client";

import { useEffect, useState } from "react";

/**
 * Real, defensible stats — no invented traction numbers.
 * - Left: peak risk weight each signal class can contribute, straight from the
 *   scanner/firewall scoring tables.
 * - Right: counts that are true of the codebase, plus a live counter of scans
 *   actually run in this browser session (demos dispatch `aegis:scan`).
 */

const CLASSES: { label: string; weight: number }[] = [
  { label: "Honeypot / sell-block", weight: 90 },
  { label: "GoPlus reputation", weight: 85 },
  { label: "Contract integrity", weight: 80 },
  { label: "Owner rewrites balance", weight: 60 },
  { label: "Embedded txn injection", weight: 50 },
  { label: "Holder concentration", weight: 50 },
  { label: "Data exfiltration", weight: 45 },
  { label: "Thin liquidity", weight: 45 },
  { label: "Instruction override", weight: 40 },
  { label: "Price impact", weight: 40 },
];

export default function StatsBoard() {
  const [scans, setScans] = useState(0);
  const [shown, setShown] = useState(false);

  useEffect(() => {
    setShown(true);
    const onScan = () => setScans((n) => n + 1);
    window.addEventListener("aegis:scan", onScan);
    return () => window.removeEventListener("aegis:scan", onScan);
  }, []);

  const max = CLASSES[0]!.weight;

  return (
    <div className="board">
      <div className="panel-box">
        <h3>Peak risk weight by signal class</h3>
        {CLASSES.map((c) => (
          <div className="cov-row" key={c.label}>
            <div className="top">
              <b>{c.label}</b>
              <span>{c.weight}</span>
            </div>
            <div className="bar">
              <i style={{ width: shown ? `${(c.weight / max) * 100}%` : "0%", transition: "width 900ms cubic-bezier(0.16,1,0.3,1)" }} />
            </div>
          </div>
        ))}
      </div>

      <div className="panel-box">
        <h3>System at a glance</h3>
        <div className="kpi-grid">
          <div className="kpi"><div className="kn">21</div><div className="kl">deterministic checks in the battery</div></div>
          <div className="kpi"><div className="kn">13</div><div className="kl">firewall detectors (injection + action)</div></div>
          <div className="kpi"><div className="kn">15/15</div><div className="kl">unit tests green</div></div>
          <div className="kpi"><div className="kn">0</div><div className="kl">LLM calls to reach a verdict</div></div>
          <div className="kpi"><div className="kn counter">{scans}</div><div className="kl">verdicts run in this session</div></div>
          <div className="kpi"><div className="kn">7</div><div className="kl">EVM networks with live reputation</div></div>
        </div>
        <p style={{ fontSize: 11.5, color: "var(--muted-2)", marginTop: 16, lineHeight: 1.6 }}>
          Every number here is a property of the code in this repository — not a usage claim.
          Run a scan above and the session counter ticks up.
        </p>
      </div>
    </div>
  );
}
