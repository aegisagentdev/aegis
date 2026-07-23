/**
 * Heuristic detectors for prompt-injection patterns.
 *
 * Each rule targets a class of attack observed in MCP tool responses: an
 * imperative aimed at the model, an attempt to override the system prompt, a
 * fake tool/authority frame, or an exfiltration instruction. Rules are
 * intentionally conservative — they fire on directive language, not on the mere
 * mention of a keyword — to keep the false-positive rate near zero on benign
 * documents (a token description saying "ignore the noise" must not trip it).
 */

import type { Severity, Signal } from "./types.js";

interface Rule {
  detector: string;
  severity: Severity;
  weight: number;
  title: string;
  detail: string;
  pattern: RegExp;
}

const RULES: Rule[] = [
  {
    detector: "INJ-OVERRIDE",
    severity: "danger",
    weight: 40,
    title: "Instruction-override attempt",
    detail:
      "Text tells the model to disregard prior or system instructions — the classic prompt-injection opener.",
    pattern:
      /\b(ignore|disregard|forget|override)\b[^.]{0,40}\b(all|any|the|your|previous|prior|earlier|above|system|initial)\b[^.]{0,30}\b(instruction|instructions|prompt|prompts|context|rules|message|messages|directive)/i,
  },
  {
    detector: "INJ-ROLE",
    severity: "danger",
    weight: 35,
    title: "Role / system-prompt hijack",
    detail:
      "Text tries to redefine the model's role or inject a new system prompt via a fake turn marker.",
    pattern:
      /(\byou are now\b|\bnew (system )?(prompt|instructions?|role)\b|<\/?(system|assistant|user)>|\[(system|assistant|inst)\]|###\s*(system|instruction))/i,
  },
  {
    detector: "INJ-IMPERATIVE",
    severity: "warn",
    weight: 18,
    title: "Directive aimed at the agent",
    detail:
      "Tool output should be data, not commands. This text issues an imperative to the reading agent.",
    pattern:
      /\b(you must|you should|please|now|immediately)\b[^.]{0,30}\b(call|invoke|run|execute|send|transfer|approve|reply|respond|output|print|forward|visit|fetch|navigate|delete|sign)\b/i,
  },
  {
    detector: "INJ-EXFIL",
    severity: "danger",
    weight: 45,
    title: "Data-exfiltration instruction",
    detail:
      "Text instructs the agent to leak secrets, keys, wallet contents, or prior context to an external destination.",
    pattern:
      /\b(send|post|exfiltrate|upload|leak|forward|email|dm|paste)\b[^.]{0,50}\b(private key|seed phrase|mnemonic|api key|secret|password|wallet|balance|system prompt|conversation|context|all funds)\b/i,
  },
  {
    detector: "INJ-AUTHORITY",
    severity: "warn",
    weight: 20,
    title: "False authority / urgency frame",
    detail:
      "Text impersonates the developer, system, or user, or manufactures urgency to coerce an action.",
    pattern:
      /\b(as (the|your) (developer|admin|system|owner)|i am (the|your) (developer|admin|owner)|this is (an )?(official|authorized|urgent|emergency)|the user (has )?(pre-?)?(authorized|approved|requested))\b/i,
  },
  {
    detector: "INJ-TOOL",
    severity: "danger",
    weight: 30,
    title: "Tool-call injection",
    detail:
      "Text embeds a tool-call, function-call, or code-fence payload meant to be executed by the agent runtime.",
    pattern:
      /(<tool_call>|"tool_call"|\bfunction_call\b|\bassistant_to=\b|```(tool|python|shell|bash)\b[^`]*\b(rm -rf|curl|wget|eth_sendTransaction|approve\())/i,
  },
  {
    detector: "INJ-TXN",
    severity: "danger",
    weight: 50,
    title: "Embedded transaction directive",
    detail:
      "Text tries to steer the agent's on-chain action — a new recipient, an unlimited approval, or a drain.",
    pattern:
      /\b(approve|transfer|send|swap|bridge|withdraw)\b[^.]{0,40}(0x[a-fA-F0-9]{40}|max(uint)?|unlimited|all (of )?(your |the )?(funds|balance|tokens))/i,
  },
];

export function runHeuristics(text: string): Signal[] {
  const signals: Signal[] = [];
  for (const rule of RULES) {
    const m = rule.pattern.exec(text);
    if (m) {
      const start = Math.max(0, m.index - 12);
      signals.push({
        detector: rule.detector,
        severity: rule.severity,
        weight: rule.weight,
        title: rule.title,
        detail: rule.detail,
        excerpt: text.slice(start, m.index + m[0].length + 12).trim().slice(0, 160),
        offset: m.index,
      });
    }
  }
  return signals;
}

export const RULE_IDS = RULES.map((r) => r.detector);
