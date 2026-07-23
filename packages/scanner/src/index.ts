/**
 * @aegis/scanner — deterministic pre-trade safety scanner.
 *
 * The Aegis token-scanning skill's deterministic check battery. Feed it a
 * `TokenSnapshot` (from live RPC + GoPlus + DexScreener in production, or a
 * fixture in the demo) and a `TradeRequest`; get back a reproducible
 * GO / CAUTION / NO-GO verdict with every finding and its evidence.
 */

export { runScan, decide } from "./engine.js";
export { runChecks } from "./checks/index.js";
export {
  SEVERITY_WEIGHT,
  riskLevel,
  dangerCount,
  warnCount,
  passingCount,
  scoreBreakdown,
} from "./scoring.js";
export { DEFAULT_SETTINGS } from "./types.js";
export type {
  Severity,
  Direction,
  Verdict,
  TradeRequest,
  CheckResult,
  RevertKind,
  TokenSnapshot,
  RiskSummary,
  ScanReport,
  Settings,
} from "./types.js";
