/**
 * Reputation checks backed by the GoPlus token-security dataset. Ported from
 * Hood Trade (MIT). These corroborate the on-chain simulation with a
 * third-party label set: honeypot / cannot-sell-all, dangerous owner
 * permissions, and source-verification / proxy signals.
 */

import type { CheckResult, TokenSnapshot } from "../types.js";

export function reputationHoneypot(s: TokenSnapshot): CheckResult[] {
  const g = s.goPlus;
  if (!g?.found) return [];
  const out: CheckResult[] = [];
  if (g.isHoneypot || g.cannotSellAll) {
    out.push({
      check: "REP-HONEYPOT",
      severity: "danger",
      score: 85,
      title: "Flagged as a honeypot by GoPlus",
      detail: "The GoPlus security dataset labels this token as a honeypot or 'cannot sell all'. Independent corroboration of the on-chain simulation.",
      evidence: { is_honeypot: String(!!g.isHoneypot), cannot_sell_all: String(!!g.cannotSellAll) },
    });
  }
  const sellTax = g.sellTax ?? 0;
  const buyTax = g.buyTax ?? 0;
  if (sellTax >= 0.5 || buyTax >= 0.5) {
    out.push({
      check: "REP-TAX",
      severity: "danger",
      score: 40,
      title: `Punitive transfer tax (${pct(Math.max(sellTax, buyTax))})`,
      detail: "Buy or sell tax is high enough to erase most of the position on a round trip.",
      evidence: { buy_tax: pct(buyTax), sell_tax: pct(sellTax) },
    });
  } else if (sellTax >= 0.1 || buyTax >= 0.1) {
    out.push({
      check: "REP-TAX",
      severity: "warn",
      score: 15,
      title: `Notable transfer tax (${pct(Math.max(sellTax, buyTax))})`,
      detail: "There is a meaningful buy/sell tax. Factor it into expected slippage.",
      evidence: { buy_tax: pct(buyTax), sell_tax: pct(sellTax) },
    });
  }
  if (!out.length) out.push({ check: "REP-HONEYPOT", severity: "ok", score: 0, title: "No honeypot label", detail: "GoPlus does not flag this token as a honeypot." });
  return out;
}

export function reputationPermissions(s: TokenSnapshot): CheckResult[] {
  const g = s.goPlus;
  if (!g?.found) return [];
  const out: CheckResult[] = [];
  if (g.ownerChangeBalance) out.push(danger("REP-BALANCE", 60, "Owner can change balances", "The contract lets a privileged address rewrite holder balances — a direct rug primitive."));
  if (g.isMintable) out.push(warn("REP-MINT", 20, "Token is mintable", "New supply can be minted, diluting holders. Confirm mint authority is renounced or time-locked."));
  if (g.transferPausable) out.push(warn("REP-PAUSE", 18, "Transfers are pausable", "A privileged address can pause all transfers, freezing your position."));
  if (g.hasBlacklist) out.push(warn("REP-BLACKLIST", 18, "Blacklist function present", "The contract can block specific addresses from transferring."));
  if (!out.length) out.push({ check: "REP-PERMISSIONS", severity: "ok", score: 0, title: "No dangerous owner permissions", detail: "No mint / pause / balance-rewrite / blacklist powers detected." });
  return out;
}

export function reputationSource(s: TokenSnapshot): CheckResult[] {
  const g = s.goPlus;
  if (!g?.found) return [];
  const out: CheckResult[] = [];
  if (g.isOpenSource === false) out.push(warn("REP-SOURCE", 15, "Source code not verified", "The contract source is not verified, so its behavior can't be audited from bytecode alone."));
  if (g.isProxy) out.push(warn("REP-PROXY", 12, "Upgradeable proxy", "The token is a proxy; its logic can be swapped by whoever controls the admin key."));
  if (!out.length) out.push({ check: "REP-SOURCE", severity: "ok", score: 0, title: "Verified, non-proxy contract", detail: "Source is verified and the contract is not an upgradeable proxy." });
  return out;
}

function danger(check: string, score: number, title: string, detail: string): CheckResult {
  return { check, severity: "danger", score, title, detail };
}
function warn(check: string, score: number, title: string, detail: string): CheckResult {
  return { check, severity: "warn", score, title, detail };
}
function pct(r: number): string {
  return `${Math.round(r * 100)}%`;
}
