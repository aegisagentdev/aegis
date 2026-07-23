/**
 * Shared types for the firewall. The contract is deliberately small: every
 * detector returns `Signal[]`, the aggregator turns signals into a `Verdict`.
 *
 * The verdict is decided by summing signal weights against thresholds — never
 * by an LLM. A model may *explain* a block, but the allow/block gate must be
 * reproducible and auditable, the same way the pre-trade scanner decides GO /
 * NO-GO deterministically.
 */

export type Severity = "info" | "warn" | "danger";

/** Where the untrusted text came from, for the audit trail. */
export interface Source {
  /** MCP server name, e.g. "dexscreener" or "web-fetch". */
  server?: string;
  /** Tool that produced the response, e.g. "get_token_info". */
  tool?: string;
}

export interface Signal {
  /** Stable detector id, e.g. INJ-IMPERATIVE or ENC-BASE64. */
  detector: string;
  severity: Severity;
  /** Risk points contributed toward the block decision. */
  weight: number;
  title: string;
  detail: string;
  /** The offending excerpt, truncated. Never the whole payload. */
  excerpt?: string;
  /** Character offset in the (possibly decoded) text, when known. */
  offset?: number;
}

export type Decision = "allow" | "flag" | "block";

export interface ScanResult {
  decision: Decision;
  /** Summed weight of all signals. */
  score: number;
  signals: Signal[];
  /** Layers of encoding that were peeled back before scanning. */
  decodedLayers: string[];
  /** The text the agent will actually see if allowed (sanitized when flagged). */
  sanitized: string;
  source?: Source;
}

export const SEVERITY_WEIGHT: Record<Severity, number> = {
  info: 1,
  warn: 3,
  danger: 10,
};
