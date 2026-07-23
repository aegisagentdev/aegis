/**
 * Scoring utilities for risk aggregation. Part of the Aegis token-scanning skill.
 *
 * Severity weighting mirrors the firewall's, so a trader reads one consistent
 * scale across both gates.
 */

import type { CheckResult, Severity } from "./types.js";

export const SEVERITY_WEIGHT: Record<Severity, number> = {
  ok: 0,
  info: 1,
  warn: 3,
  danger: 10,
};

export function riskLevel(score: number, caution = 25, nogo = 60): "low" | "medium" | "high" {
  if (score >= nogo) return "high";
  if (score >= caution) return "medium";
  return "low";
}

export function dangerCount(results: CheckResult[]): number {
  return results.filter((r) => r.severity === "danger").length;
}

export function warnCount(results: CheckResult[]): number {
  return results.filter((r) => r.severity === "warn").length;
}

export function passingCount(results: CheckResult[]): number {
  return results.filter((r) => r.severity === "ok").length;
}

/** Group cumulative score by check family (the prefix before the first "-"). */
export function scoreBreakdown(results: CheckResult[]): Record<string, number> {
  const out: Record<string, number> = {};
  for (const r of results) {
    const area = r.check.includes("-") ? r.check.split("-")[0]! : r.check;
    out[area] = (out[area] ?? 0) + r.score;
  }
  return out;
}
