/**
 * Market & pool checks. Ported from Hood Trade (MIT).
 *
 * Thin liquidity, near-zero volume, and an oversized trade relative to pool
 * depth are the quiet ways a position becomes unexitable. On a young chain
 * (Robinhood Chain) the maturity gates relax to WARN unless `strict` is set —
 * security signals (honeypot, tax, mint) always block regardless.
 */

import type { CheckResult, Settings, TokenSnapshot, TradeRequest } from "../types.js";

export function poolChecks(s: TokenSnapshot): CheckResult[] {
  const p = s.pool;
  if (!p) return [];
  if (p.exists === false) {
    return [{ check: "POOL-EXISTS", severity: "danger", score: 50, title: "No liquidity pool found", detail: "No tradeable pool was located for this pair. There may be nowhere to sell." }];
  }
  const out: CheckResult[] = [];
  if (p.pairIntegrityOk === false) {
    out.push({ check: "POOL-INTEGRITY", severity: "danger", score: 40, title: "Pool pair integrity failed", detail: "The pool's token ordering / reserves do not match the expected pair. Possible spoofed pool." });
  }
  if (!out.length) out.push({ check: "POOL-EXISTS", severity: "ok", score: 0, title: "Pool found", detail: "A tradeable pool exists for this pair." });
  return out;
}

export function marketLiquidity(s: TokenSnapshot, settings: Settings): CheckResult[] {
  const liq = s.market?.liquidityUsd ?? s.pool?.liquidityUsd;
  if (liq == null) return [];
  const young = settings.lenient && !settings.strict;
  if (liq < 5_000) {
    return [mk("MARKET-LIQ", young ? "warn" : "danger", young ? 20 : 45, `Very thin liquidity ($${fmt(liq)})`, "Liquidity is low enough that exiting even a small position will move the price hard.", liq)];
  }
  if (liq < 25_000) {
    return [mk("MARKET-LIQ", "warn", 18, `Low liquidity ($${fmt(liq)})`, "Liquidity is modest. Size positions conservatively and expect slippage on exit.", liq)];
  }
  return [mk("MARKET-LIQ", "ok", 0, `Liquidity $${fmt(liq)}`, "Pool liquidity is adequate for retail-size trades.", liq)];
}

export function marketActivity(s: TokenSnapshot, settings: Settings): CheckResult[] {
  const vol = s.market?.volume24h;
  if (vol == null) return [];
  const young = settings.lenient && !settings.strict;
  if (vol < 1_000) {
    return [mk("MARKET-VOL", young ? "info" : "warn", young ? 1 : 12, `Near-zero 24h volume ($${fmt(vol)})`, "Almost no one is trading this. Low volume makes both price discovery and exit unreliable.", vol)];
  }
  return [mk("MARKET-VOL", "ok", 0, `24h volume $${fmt(vol)}`, "There is active trading in this pair.", vol)];
}

export function sizeVsDepth(s: TokenSnapshot, req: TradeRequest): CheckResult[] {
  const liq = s.market?.liquidityUsd ?? s.pool?.liquidityUsd;
  if (liq == null || liq <= 0) return [];
  const share = req.amountUsd / liq;
  if (share >= 0.1) {
    return [mk("EXEC-IMPACT", "danger", 40, `Trade is ${Math.round(share * 100)}% of pool liquidity`, "A trade this large relative to the pool will suffer severe slippage and may be impossible to unwind at a fair price.", req.amountUsd)];
  }
  if (share >= 0.02) {
    return [mk("EXEC-IMPACT", "warn", 15, `Trade is ${Math.round(share * 100)}% of pool liquidity`, "Expect meaningful price impact at this size relative to pool depth.", req.amountUsd)];
  }
  return [mk("EXEC-IMPACT", "ok", 0, "Trade size is comfortable vs depth", `The trade is ${(share * 100).toFixed(1)}% of pool liquidity.`, req.amountUsd)];
}

function mk(check: string, severity: CheckResult["severity"], score: number, title: string, detail: string, usd: number): CheckResult {
  return { check, severity, score, title, detail, evidence: { usd: String(Math.round(usd)) } };
}
function fmt(n: number): string {
  return n >= 1_000_000 ? `${(n / 1e6).toFixed(1)}M` : n >= 1_000 ? `${(n / 1e3).toFixed(0)}k` : String(Math.round(n));
}
