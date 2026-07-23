/**
 * Scan engine: run the battery, aggregate, decide a verdict. Part of the Aegis
 * token-scanning skill.
 *
 * The verdict is decided here, deterministically, from the summed risk score
 * and any DANGER-severity finding. A summary layer may *explain* the result but
 * never overrides the gate — the go/no-go a trader relies on must be
 * reproducible and auditable, not a model's judgement call.
 */

import { runChecks } from "./checks/index.js";
import { DEFAULT_SETTINGS } from "./types.js";
import type { CheckResult, ScanReport, Settings, TokenSnapshot, TradeRequest, Verdict } from "./types.js";

export function decide(score: number, results: CheckResult[], settings: Settings): Verdict {
  if (results.some((r) => r.severity === "danger")) return "NO";
  if (score >= settings.nogoScore) return "NO";
  if (score >= settings.cautionScore) return "CAUTION";
  return "GO";
}

export function runScan(
  snapshot: TokenSnapshot,
  request: TradeRequest,
  settings: Settings = DEFAULT_SETTINGS,
): ScanReport {
  const notes: string[] = [];
  if (snapshot.goPlus && !snapshot.goPlus.found) notes.push("GoPlus had no record for this token — reputation checks skipped.");
  if (snapshot.market && !snapshot.market.found) notes.push("No DexScreener market data — liquidity/volume inferred from pool only.");

  const results = runChecks(snapshot, request, settings);

  if (results.length === 0) {
    return { request, verdict: "UNKNOWN", score: 0, results: [], notes: notes.length ? notes : ["No checks produced output — data may be unavailable."] };
  }

  const score = results.reduce((sum, r) => sum + r.score, 0);
  const verdict = decide(score, results, settings);

  return {
    request,
    verdict,
    score,
    tokenName: snapshot.name,
    tokenSymbol: snapshot.symbol,
    priceUsd: snapshot.market?.priceUsd,
    marketCap: snapshot.market?.marketCap,
    liquidityUsd: snapshot.market?.liquidityUsd ?? snapshot.pool?.liquidityUsd,
    volume24h: snapshot.market?.volume24h,
    results,
    notes,
  };
}
