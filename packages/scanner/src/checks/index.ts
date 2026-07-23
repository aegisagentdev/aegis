/**
 * The default check battery, in execution order. Part of the Aegis token-scanning skill.
 *
 * Each check is a pure function of the snapshot (and, for a few, the trade
 * request / settings). They are independent and safe to run in any order — the
 * order here just matches the upstream battery for readability.
 */

import type { CheckResult, Settings, TokenSnapshot, TradeRequest } from "../types.js";
import { chainIdentity, contractExists, ownership, supplySanity } from "./contract.js";
import { honeypotApprove, honeypotTransfer } from "./honeypot.js";
import { burnedSupply, tokenSelfHolding } from "./concentration.js";
import { reputationHoneypot, reputationPermissions, reputationSource } from "./reputation.js";
import { marketActivity, marketLiquidity, poolChecks, sizeVsDepth } from "./market.js";
import { stockDisclosure, stockDivergence } from "./stock.js";

export function runChecks(snapshot: TokenSnapshot, req: TradeRequest, settings: Settings): CheckResult[] {
  return [
    ...chainIdentity(snapshot),
    ...contractExists(snapshot),
    ...ownership(snapshot),
    ...supplySanity(snapshot),
    ...honeypotTransfer(snapshot),
    ...honeypotApprove(snapshot),
    ...tokenSelfHolding(snapshot),
    ...burnedSupply(snapshot),
    ...reputationHoneypot(snapshot),
    ...reputationPermissions(snapshot),
    ...reputationSource(snapshot),
    ...poolChecks(snapshot),
    ...marketLiquidity(snapshot, settings),
    ...marketActivity(snapshot, settings),
    ...sizeVsDepth(snapshot, req),
    ...stockDisclosure(snapshot),
    ...stockDivergence(snapshot),
  ];
}
