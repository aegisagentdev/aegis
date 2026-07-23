/**
 * Robinhood Chain tokenized-stock (RIF) checks. Ported from Hood Trade (MIT).
 *
 * RIF tokens wrap a real equity. Two things matter that don't apply to a normal
 * memecoin: is the token actually disclosed/backed as a stock token, and does
 * the on-pool price diverge wildly from the reference price (a sign of a stale
 * or manipulated pool you shouldn't trade against).
 */

import type { CheckResult, TokenSnapshot } from "../types.js";

export function stockDisclosure(s: TokenSnapshot): CheckResult[] {
  const st = s.stock;
  if (!st?.isStockToken) return [];
  if (st.hasDisclosure === false) {
    return [
      {
        check: "STOCK-DISCLOSURE",
        severity: "warn",
        score: 20,
        title: "Stock token without disclosure",
        detail: "This looks like a tokenized-stock (RIF) token but carries no backing/disclosure metadata. Confirm it is a genuine issued token, not an unbacked look-alike.",
      },
    ];
  }
  return [{ check: "STOCK-DISCLOSURE", severity: "ok", score: 0, title: "Stock token disclosed", detail: "Tokenized-stock backing/disclosure metadata is present." }];
}

export function stockDivergence(s: TokenSnapshot): CheckResult[] {
  const st = s.stock;
  if (!st?.isStockToken || st.priceDivergence == null) return [];
  const d = Math.abs(st.priceDivergence);
  if (d >= 0.1) {
    return [
      {
        check: "STOCK-DIVERGENCE",
        severity: "danger",
        score: 35,
        title: `Pool price diverges ${Math.round(d * 100)}% from reference`,
        detail: "The pool price is far from the reference/oracle price for the underlying equity — the pool is stale or manipulated. Trading against it means buying at a bad mark.",
        evidence: { divergence: `${Math.round(d * 100)}%` },
      },
    ];
  }
  return [{ check: "STOCK-DIVERGENCE", severity: "ok", score: 0, title: "Pool tracks reference price", detail: `Pool price is within ${Math.round(d * 100)}% of the reference.` }];
}
