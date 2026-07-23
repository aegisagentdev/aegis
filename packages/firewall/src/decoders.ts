/**
 * Deterministic decoding layer.
 *
 * Prompt injections routinely hide the payload from a naive substring scan by
 * encoding it: base64, hex, percent-encoding, HTML entities, unicode escapes,
 * or by splicing zero-width characters between letters ("i​g​nore").
 * Before any heuristic runs we peel these layers back and also scan the decoded
 * forms, so "aWdub3JlIGFsbCBwcmV2aW91cw==" is judged as the "ignore all
 * previous" it decodes to.
 *
 * This is the "deterministic decoding" leg of the detection stack — no model,
 * no network, fully reproducible.
 */

/** Characters used to break up trigger words so they slip past a plain match. */
const ZERO_WIDTH = /[​‌‍⁠﻿­]/g;

/** Confusable homoglyphs → ASCII, so Cyrillic "і/о/а" can't cloak "ignore". */
const HOMOGLYPHS: Record<string, string> = {
  "а": "a", // а
  "е": "e", // е
  "о": "o", // о
  "р": "p", // р
  "с": "c", // с
  "х": "x", // х
  "і": "i", // і
  "ԁ": "d",
  "ɡ": "g",
};

export function stripZeroWidth(text: string): string {
  return text.replace(ZERO_WIDTH, "");
}

export function normalizeHomoglyphs(text: string): string {
  let out = "";
  for (const ch of text) out += HOMOGLYPHS[ch] ?? ch;
  return out;
}

function tryBase64(text: string): string | null {
  // Only bother with reasonably long, base64-shaped runs.
  const matches = text.match(/[A-Za-z0-9+/]{16,}={0,2}/g);
  if (!matches) return null;
  const decoded: string[] = [];
  for (const m of matches) {
    if (m.length % 4 !== 0) continue;
    try {
      const s = Buffer.from(m, "base64").toString("utf8");
      // Keep only decodes that look like natural language, not binary noise.
      if (/[\x20-\x7e]/.test(s) && printableRatio(s) > 0.85) decoded.push(s);
    } catch {
      /* not valid base64 — ignore */
    }
  }
  return decoded.length ? decoded.join(" ") : null;
}

function tryHex(text: string): string | null {
  const matches = text.match(/(?:0x)?(?:[0-9a-fA-F]{2}){8,}/g);
  if (!matches) return null;
  const decoded: string[] = [];
  for (const raw of matches) {
    const m = raw.replace(/^0x/, "");
    if (m.length % 2 !== 0) continue;
    let s = "";
    for (let i = 0; i < m.length; i += 2) s += String.fromCharCode(parseInt(m.slice(i, i + 2), 16));
    if (printableRatio(s) > 0.85) decoded.push(s);
  }
  return decoded.length ? decoded.join(" ") : null;
}

function tryEscapes(text: string): string | null {
  if (!/\\u[0-9a-fA-F]{4}|\\x[0-9a-fA-F]{2}|%[0-9a-fA-F]{2}|&#\d+;/.test(text)) return null;
  let s = text
    .replace(/\\u([0-9a-fA-F]{4})/g, (_, h) => String.fromCharCode(parseInt(h, 16)))
    .replace(/\\x([0-9a-fA-F]{2})/g, (_, h) => String.fromCharCode(parseInt(h, 16)))
    .replace(/&#(\d+);/g, (_, d) => String.fromCharCode(parseInt(d, 10)))
    .replace(/&#x([0-9a-fA-F]+);/g, (_, h) => String.fromCharCode(parseInt(h, 16)));
  try {
    s = decodeURIComponent(s);
  } catch {
    /* leave partially decoded */
  }
  return s === text ? null : s;
}

function printableRatio(s: string): number {
  if (!s.length) return 0;
  let printable = 0;
  for (const c of s) {
    const code = c.charCodeAt(0);
    if (code === 9 || code === 10 || code === 13 || (code >= 32 && code <= 126) || code > 160) printable++;
  }
  return printable / s.length;
}

export interface DecodeResult {
  /** Normalized surface text (zero-width stripped, homoglyphs folded). */
  normalized: string;
  /** Every decoded layer we recovered, labelled by scheme. */
  layers: { scheme: string; text: string }[];
}

/**
 * Return the normalized text plus any nested decodes. We decode up to `maxDepth`
 * times because attackers double-encode (base64 of hex of the payload).
 */
export function decodeAll(input: string, maxDepth = 3): DecodeResult {
  const normalized = normalizeHomoglyphs(stripZeroWidth(input));
  const layers: { scheme: string; text: string }[] = [];
  const seen = new Set<string>([normalized]);
  let frontier = [normalized];

  for (let depth = 0; depth < maxDepth && frontier.length; depth++) {
    const next: string[] = [];
    for (const text of frontier) {
      const candidates: [string, string | null][] = [
        ["base64", tryBase64(text)],
        ["hex", tryHex(text)],
        ["escape", tryEscapes(text)],
      ];
      for (const [scheme, out] of candidates) {
        if (out && !seen.has(out)) {
          seen.add(out);
          layers.push({ scheme, text: out });
          next.push(out);
        }
      }
    }
    frontier = next;
  }

  return { normalized, layers };
}
