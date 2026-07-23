/**
 * Contract-level checks: does the token exist as code, is ownership renounced,
 * is the supply sane. Ported from Hood Trade (MIT).
 */

import type { CheckResult, TokenSnapshot } from "../types.js";

export function chainIdentity(s: TokenSnapshot): CheckResult[] {
  if (s.chainId == null || s.expectedChainId == null) return [];
  if (s.chainId !== s.expectedChainId) {
    return [
      {
        check: "CHAIN-IDENTITY",
        severity: "danger",
        score: 40,
        title: "RPC reports an unexpected chain id",
        detail: `The endpoint returned chain id ${s.chainId} but ${s.expectedChainId} was expected. You may be scanning the wrong network.`,
        evidence: { got: String(s.chainId), expected: String(s.expectedChainId) },
      },
    ];
  }
  return [{ check: "CHAIN-IDENTITY", severity: "ok", score: 0, title: "Chain identity confirmed", detail: `Connected to chain id ${s.chainId}.` }];
}

export function contractExists(s: TokenSnapshot): CheckResult[] {
  if (s.codeSize == null) return [];
  if (s.codeSize === 0) {
    return [
      {
        check: "CONTRACT-EXISTS",
        severity: "danger",
        score: 80,
        title: "No contract code at this address",
        detail: "The token address holds no bytecode. It is an EOA or an empty address — there is nothing to trade.",
      },
    ];
  }
  return [{ check: "CONTRACT-EXISTS", severity: "ok", score: 0, title: "Contract code present", detail: `${s.codeSize} bytes of bytecode at the token address.` }];
}

export function ownership(s: TokenSnapshot): CheckResult[] {
  if (s.ownerRenounced == null) return [];
  if (!s.ownerRenounced) {
    return [
      {
        check: "CONTRACT-OWNER",
        severity: "warn",
        score: 12,
        title: "Ownership not renounced",
        detail: "The contract still has an active owner. Depending on the code, the owner may be able to mint, pause, or change fees. Renounced ownership removes that discretion.",
      },
    ];
  }
  return [{ check: "CONTRACT-OWNER", severity: "ok", score: 0, title: "Ownership renounced", detail: "No privileged owner can alter the contract." }];
}

export function supplySanity(s: TokenSnapshot): CheckResult[] {
  if (s.totalSupply == null) return [];
  if (s.totalSupply <= 0) {
    return [
      {
        check: "CONTRACT-SUPPLY",
        severity: "danger",
        score: 30,
        title: "Total supply is zero",
        detail: "totalSupply() returned 0 — the token has no issued supply and cannot be traded normally.",
      },
    ];
  }
  return [{ check: "CONTRACT-SUPPLY", severity: "ok", score: 0, title: "Supply looks sane", detail: `totalSupply is ${s.totalSupply.toLocaleString()}.` }];
}
