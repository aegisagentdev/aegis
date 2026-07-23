/**
 * The aggregator: decode → detect → decide.
 *
 * `scanText` is the way-in gate for a single MCP tool response. It decodes any
 * hidden layers, runs the heuristics over the normalized text *and* every
 * decoded layer, sums the weights, and returns a deterministic allow / flag /
 * block decision plus a sanitized copy of the text.
 */

import { decodeAll } from "./decoders.js";
import { runHeuristics } from "./heuristics.js";
import type { Decision, ScanResult, Signal, Source } from "./types.js";

export interface ScanOptions {
  /** Score at or above which the response is blocked outright. */
  blockThreshold?: number;
  /** Score at or above which the response is flagged (delivered, but marked). */
  flagThreshold?: number;
  source?: Source;
}

const DEFAULTS = { blockThreshold: 30, flagThreshold: 12 };

function dedupe(signals: Signal[]): Signal[] {
  const best = new Map<string, Signal>();
  for (const s of signals) {
    const prev = best.get(s.detector);
    if (!prev || s.weight > prev.weight) best.set(s.detector, s);
  }
  return [...best.values()].sort((a, b) => b.weight - a.weight);
}

/** Neutralize a blocked/flagged payload so a downstream agent can't act on it. */
function sanitize(text: string, signals: Signal[]): string {
  let out = text;
  for (const s of signals) {
    if (s.excerpt) out = out.split(s.excerpt).join("⟦removed by aegis: " + s.detector + "⟧");
  }
  return out;
}

export function scanText(text: string, opts: ScanOptions = {}): ScanResult {
  const blockThreshold = opts.blockThreshold ?? DEFAULTS.blockThreshold;
  const flagThreshold = opts.flagThreshold ?? DEFAULTS.flagThreshold;

  const { normalized, layers } = decodeAll(text);

  const all: Signal[] = [...runHeuristics(normalized)];
  for (const layer of layers) {
    for (const sig of runHeuristics(layer.text)) {
      // A payload hidden behind encoding is more suspicious, not less.
      all.push({
        ...sig,
        detector: `${sig.detector}+${layer.scheme.toUpperCase()}`,
        weight: sig.weight + 10,
        detail: `${sig.detail} (recovered from ${layer.scheme}-encoded text)`,
      });
    }
  }

  const signals = dedupe(all);
  const score = signals.reduce((sum, s) => sum + s.weight, 0);

  let decision: Decision = "allow";
  if (score >= blockThreshold) decision = "block";
  else if (score >= flagThreshold) decision = "flag";

  return {
    decision,
    score,
    signals,
    decodedLayers: layers.map((l) => l.scheme),
    sanitized: decision === "allow" ? normalized : sanitize(normalized, signals),
    source: opts.source,
  };
}
