/**
 * @aegis/firewall — a prompt-injection firewall for MCP tool responses and an
 * action guard for agentic trades.
 *
 * Way in:  scanText(untrustedToolOutput)  → allow / flag / block
 * Way out: guardAction(proposedTx)         → deterministic action signals
 *
 * Neither gate is decided by an LLM. Both return the evidence behind the
 * decision so it can be logged, shown to a user, or written to an on-chain
 * receipt.
 */

export { scanText } from "./scan.js";
export type { ScanOptions } from "./scan.js";
export { guardAction } from "./actionGuard.js";
export type { ProposedAction, GuardContext } from "./actionGuard.js";
export { decodeAll, stripZeroWidth, normalizeHomoglyphs } from "./decoders.js";
export { runHeuristics, RULE_IDS } from "./heuristics.js";
export type { Signal, ScanResult, Decision, Severity, Source } from "./types.js";
export { SEVERITY_WEIGHT } from "./types.js";
