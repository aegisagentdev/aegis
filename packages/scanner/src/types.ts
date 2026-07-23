/**
 * Core types for the pre-trade scanner.
 *
 * Part of the Aegis token-scanning skill. These are the contract between the on-chain /
 * market data layer, the deterministic check battery, and the human-facing
 * summary. The verdict is decided by the engine from validated, structured
 * signals — never from a raw data blob and never by an LLM.
 */

export type Severity = "ok" | "info" | "warn" | "danger";
export type Direction = "buy" | "sell";
export type Verdict = "GO" | "CAUTION" | "NO" | "UNKNOWN";

export interface TradeRequest {
  /** Token being acquired or disposed of. */
  token: string;
  /** Counter asset (e.g. USDG, WETH). */
  quote: string;
  /** Notional size of the trade in USD. */
  amountUsd: number;
  direction?: Direction;
  venue?: string;
}

export interface CheckResult {
  /** Stable check id, e.g. CONTRACT-HONEYPOT. */
  check: string;
  severity: Severity;
  /** Risk points contributed toward the verdict. */
  score: number;
  title: string;
  detail: string;
  evidence?: Record<string, string>;
}

/** Reason an eth_call transfer/approve simulation reverted, pre-classified. */
export type RevertKind = "restriction" | "balance" | "unknown" | "ok" | null;

/**
 * A point-in-time view of everything the checks need. Populated from live RPC
 * + GoPlus + DexScreener in production, or from a fixture in the web demo. The
 * checks are pure functions of this snapshot, so the verdict is reproducible.
 */
export interface TokenSnapshot {
  chainId?: number;
  expectedChainId?: number;
  name?: string;
  symbol?: string;

  /** Bytecode size at the token address; 0 means "not a contract". */
  codeSize?: number;
  ownerRenounced?: boolean;
  totalSupply?: number;
  /** Balance held by the token contract itself. */
  selfBalance?: number;
  /** Balance held in burn addresses (0x0 + 0x…dead). */
  burnedBalance?: number;

  /** Classified honeypot simulation results. */
  transferRevert?: RevertKind;
  approveRevert?: RevertKind;

  /** GoPlus / reputation signals. */
  goPlus?: {
    isHoneypot?: boolean;
    cannotSellAll?: boolean;
    buyTax?: number;
    sellTax?: number;
    isOpenSource?: boolean;
    isProxy?: boolean;
    isMintable?: boolean;
    ownerChangeBalance?: boolean;
    transferPausable?: boolean;
    hasBlacklist?: boolean;
    found?: boolean;
  };

  /** DexScreener / market snapshot. */
  market?: {
    found?: boolean;
    priceUsd?: number;
    marketCap?: number;
    liquidityUsd?: number;
    volume24h?: number;
  };

  /** Pool sanity. */
  pool?: {
    exists?: boolean;
    pairIntegrityOk?: boolean;
    liquidityUsd?: number;
  };

  /** Robinhood Chain tokenized-stock (RIF) fields. */
  stock?: {
    isStockToken?: boolean;
    hasDisclosure?: boolean;
    /** Divergence between pool price and oracle/reference price, as a fraction. */
    priceDivergence?: number;
  };
}

export interface RiskSummary {
  headline: string;
  keyRisks: string[];
  whatToCheck: string[];
}

export interface ScanReport {
  request: TradeRequest;
  verdict: Verdict;
  score: number;
  tokenName?: string;
  tokenSymbol?: string;
  priceUsd?: number;
  marketCap?: number;
  liquidityUsd?: number;
  volume24h?: number;
  results: CheckResult[];
  summary?: RiskSummary;
  notes: string[];
}

export interface Settings {
  cautionScore: number;
  nogoScore: number;
  /** Relax market-maturity gates (auto-on for a young chain like Robinhood). */
  lenient: boolean;
  /** Force full strictness even on a young chain. */
  strict: boolean;
}

export const DEFAULT_SETTINGS: Settings = {
  cautionScore: 25,
  nogoScore: 60,
  lenient: false,
  strict: false,
};
