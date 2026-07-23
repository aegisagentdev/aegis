/**
 * Action guard.
 *
 * The firewall protects the way *in* (what the agent reads). The action guard
 * protects the way *out* (what the agent is about to sign). Even a perfectly
 * clean prompt can produce a dangerous transaction, so we inspect the concrete
 * call the agent proposes before it is signed:
 *
 *   - unlimited / max-uint approvals
 *   - approvals or transfers to an address the operator never allow-listed
 *   - transfers that move an outsized share of the wallet in one call
 *
 * This mirrors the pre-trade scanner's philosophy: a deterministic gate on the
 * action, with a human-readable reason for every block.
 */

import type { Severity, Signal } from "./types.js";

const MAX_UINT = (1n << 256n) - 1n;
/** Approvals above this notionally-infinite threshold are treated as unlimited. */
const UNLIMITED_THRESHOLD = (1n << 200n);

export interface ProposedAction {
  kind: "approve" | "transfer" | "swap" | "other";
  /** Token contract the action touches. */
  token?: string;
  /** Spender (for approve) or recipient (for transfer). */
  to?: string;
  /** Raw integer amount, as a string to preserve precision. */
  amount?: string;
  /** Fraction of the wallet's balance this action moves, 0..1, if known. */
  fractionOfBalance?: number;
}

export interface GuardContext {
  /** Addresses the operator has explicitly allow-listed (routers, known spenders). */
  allowlist?: string[];
  /** Cap on a single transfer as a fraction of balance before it's flagged. */
  maxTransferFraction?: number;
}

function isUnlimited(amount?: string): boolean {
  if (!amount) return false;
  try {
    const v = BigInt(amount);
    return v >= UNLIMITED_THRESHOLD || v === MAX_UINT;
  } catch {
    return /^0x[fF]+$/.test(amount) || /unlimited|max/i.test(amount);
  }
}

export function guardAction(action: ProposedAction, ctx: GuardContext = {}): Signal[] {
  const signals: Signal[] = [];
  const allow = new Set((ctx.allowlist ?? []).map((a) => a.toLowerCase()));
  const to = action.to?.toLowerCase();

  const push = (detector: string, severity: Severity, weight: number, title: string, detail: string) =>
    signals.push({ detector, severity, weight, title, detail, excerpt: action.to });

  if (action.kind === "approve" && isUnlimited(action.amount)) {
    push(
      "ACT-UNLIMITED-APPROVE",
      "danger",
      40,
      "Unlimited token approval",
      "This approve() grants an effectively infinite allowance. A compromised or malicious spender could drain the token later. Approve only the amount the swap needs.",
    );
  }

  if ((action.kind === "approve" || action.kind === "transfer") && to && allow.size > 0 && !allow.has(to)) {
    push(
      "ACT-UNKNOWN-RECIPIENT",
      "danger",
      35,
      "Recipient not on the allow-list",
      `The ${action.kind} targets ${action.to}, which is not among the operator's allow-listed addresses. A prompt injection often swaps in an attacker address here.`,
    );
  }

  const cap = ctx.maxTransferFraction ?? 0.9;
  if (action.kind === "transfer" && typeof action.fractionOfBalance === "number" && action.fractionOfBalance >= cap) {
    push(
      "ACT-DRAIN",
      "danger",
      45,
      "Transfer moves most of the wallet",
      `This transfer moves ${Math.round(action.fractionOfBalance * 100)}% of the balance in one call — consistent with a drain. Confirm the recipient and size manually.`,
    );
  }

  if (action.token && to && action.token.toLowerCase() === to) {
    push(
      "ACT-SELF-SPENDER",
      "warn",
      15,
      "Approval to the token contract itself",
      "The spender equals the token contract, an unusual pattern seen in some malicious approval flows.",
    );
  }

  return signals;
}
