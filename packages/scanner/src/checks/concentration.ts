/**
 * Holder-concentration checks. Part of the Aegis token-scanning skill.
 *
 * When a small set of wallets — or the token contract itself — controls a large
 * share of supply, the rug risk is high. Burned supply is reported too: a token
 * that is ~all burned has a razor-thin float where small trades move price hard.
 */

import type { CheckResult, TokenSnapshot } from "../types.js";

export function tokenSelfHolding(s: TokenSnapshot): CheckResult[] {
  if (s.codeSize === 0 || s.totalSupply == null || s.selfBalance == null || s.totalSupply <= 0) return [];
  const ratio = s.selfBalance / s.totalSupply;
  const ev = { self_balance: String(s.selfBalance), total_supply: String(s.totalSupply) };
  if (ratio >= 0.5) {
    return [
      {
        check: "CONC-SELF",
        severity: "danger",
        score: 50,
        title: `Token self-holds ${pct(ratio)} of supply`,
        detail: "The token contract holds more than half of its own supply. The circulating float is thin and the holder can dump the unreleased supply.",
        evidence: ev,
      },
    ];
  }
  if (ratio >= 0.2) {
    return [
      {
        check: "CONC-SELF",
        severity: "warn",
        score: 20,
        title: `Token self-holds ${pct(ratio)} of supply`,
        detail: "The token contract holds a significant share of its own supply — a reflection/tax mechanism or an unreleased allocation.",
        evidence: ev,
      },
    ];
  }
  return [{ check: "CONC-SELF", severity: "ok", score: 0, title: "Token self-holding negligible", detail: `The contract holds ${pct(ratio)} of its own supply.`, evidence: ev }];
}

export function burnedSupply(s: TokenSnapshot): CheckResult[] {
  if (s.codeSize === 0 || s.totalSupply == null || s.burnedBalance == null || s.totalSupply <= 0) return [];
  const ratio = s.burnedBalance / s.totalSupply;
  const ev = { burned: String(s.burnedBalance), total_supply: String(s.totalSupply) };
  if (ratio >= 0.95) {
    return [
      {
        check: "CONC-BURNED",
        severity: "warn",
        score: 15,
        title: `${pct(ratio)} of supply is burned`,
        detail: "Nearly all supply is in burn addresses. The remaining float is extremely thin — small trades can cause outsized price impact.",
        evidence: ev,
      },
    ];
  }
  return [{ check: "CONC-BURNED", severity: "ok", score: 0, title: `${pct(ratio)} of supply burned`, detail: `${s.burnedBalance.toLocaleString()} tokens in burn addresses.`, evidence: ev }];
}

function pct(r: number): string {
  return `${(r * 100).toFixed(r < 0.1 ? 1 : 0)}%`;
}
