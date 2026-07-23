/**
 * Honeypot detection. Part of the Aegis token-scanning skill.
 *
 * A honeypot lets you buy but blocks or taxes sells. Upstream, a read-only
 * eth_call simulates transfer()/approve() and the revert reason is classified
 * into `restriction` (a blacklist / pause / trading gate — a real signal),
 * `balance` (a compliant ERC-20 refusing a zero-balance sender — healthy), or
 * `unknown`. Here we turn that classification into scored findings.
 */

import type { CheckResult, TokenSnapshot } from "../types.js";

export function honeypotTransfer(s: TokenSnapshot): CheckResult[] {
  if (s.codeSize === 0 || s.transferRevert === undefined) return [];
  switch (s.transferRevert) {
    case "restriction":
      return [
        {
          check: "CONTRACT-HONEYPOT",
          severity: "danger",
          score: 90,
          title: "Honeypot risk — transfer blocked",
          detail:
            "A simulated transfer reverted with a restriction error (blacklist / pause / trading-gate). Strong signal the token blocks transfers for ordinary holders — you could buy but not sell.",
        },
      ];
    case "balance":
    case "ok":
      return [{ check: "CONTRACT-HONEYPOT", severity: "ok", score: 0, title: "Transfer behaves normally", detail: "transfer() behaved as a compliant ERC-20 should." }];
    default:
      return [
        {
          check: "CONTRACT-HONEYPOT",
          severity: "info",
          score: 0,
          title: "Transfer simulation inconclusive",
          detail: "The transfer simulation reverted without a clear reason. Rely on the GoPlus honeypot signal and real trade history.",
        },
      ];
  }
}

export function honeypotApprove(s: TokenSnapshot): CheckResult[] {
  if (s.codeSize === 0 || s.approveRevert === undefined) return [];
  if (s.approveRevert === "restriction") {
    return [
      {
        check: "CONTRACT-APPROVE",
        severity: "warn",
        score: 25,
        title: "Approve blocked by a restriction",
        detail: "approve(spender, maxUint) reverted with a restriction error. Some honeypots block approval to stop the victim selling via a DEX router.",
      },
    ];
  }
  return [{ check: "CONTRACT-APPROVE", severity: "ok", score: 0, title: "Approve simulation passed", detail: "approve() did not revert." }];
}
