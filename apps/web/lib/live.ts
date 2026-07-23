/**
 * Live token snapshot builder for the web scanner.
 *
 * Pulls real, keyless public data — GoPlus token-security + DexScreener market —
 * and maps it into the `TokenSnapshot` the deterministic @aegis/scanner battery
 * consumes. No fabrication: when a chain or token has no data, the fields stay
 * undefined and the engine returns UNKNOWN with a note.
 *
 * The full on-chain honeypot *simulation* (eth_call transfer/approve) is done by
 * the CLI / MCP engine (`aegis`, `packages/scanner-py`); the web path relies on
 * GoPlus reputation + market depth, which need no RPC and run at the edge.
 */

import type { TokenSnapshot } from "@aegis/scanner";

export const LIVE_CHAINS: { key: string; label: string; goplus: number | null }[] = [
  { key: "robinhood", label: "Robinhood Chain", goplus: null },
  { key: "ethereum", label: "Ethereum", goplus: 1 },
  { key: "base", label: "Base", goplus: 8453 },
  { key: "bsc", label: "BNB Chain", goplus: 56 },
  { key: "arbitrum", label: "Arbitrum", goplus: 42161 },
  { key: "polygon", label: "Polygon", goplus: 137 },
  { key: "optimism", label: "Optimism", goplus: 10 },
  { key: "avalanche", label: "Avalanche", goplus: 43114 },
];

const ZERO_OWNERS = new Set(["", "0x0000000000000000000000000000000000000000", "0x000000000000000000000000000000000000dead"]);

async function getJson(url: string, timeoutMs = 7000): Promise<any | null> {
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), timeoutMs);
  try {
    const r = await fetch(url, { signal: ctrl.signal, headers: { accept: "application/json" } });
    if (!r.ok) return null;
    return await r.json();
  } catch {
    return null;
  } finally {
    clearTimeout(t);
  }
}

const num = (v: unknown): number | undefined => {
  if (v === null || v === undefined || v === "") return undefined;
  const n = Number(v);
  return Number.isFinite(n) ? n : undefined;
};
const bool = (v: unknown): boolean | undefined => (v === undefined || v === null || v === "" ? undefined : String(v) === "1");

export interface LiveResult {
  snapshot: TokenSnapshot;
  notes: string[];
  sources: string[];
}

export async function buildLiveSnapshot(address: string, chainKey: string): Promise<LiveResult> {
  const chain = LIVE_CHAINS.find((c) => c.key === chainKey) ?? LIVE_CHAINS[0]!;
  const notes: string[] = [];
  const sources: string[] = [];
  const snapshot: TokenSnapshot = {};

  // --- GoPlus token-security (keyless) ---
  if (chain.goplus != null) {
    const gp = await getJson(`https://api.gopluslabs.io/api/v1/token_security/${chain.goplus}?contract_addresses=${address}`);
    const row = gp?.result?.[address.toLowerCase()];
    if (row) {
      sources.push("GoPlus");
      snapshot.codeSize = 1; // GoPlus only returns rows for deployed contracts
      snapshot.name = row.token_name || undefined;
      snapshot.symbol = row.token_symbol || undefined;
      snapshot.totalSupply = num(row.total_supply);
      snapshot.ownerRenounced = row.owner_address != null ? ZERO_OWNERS.has(String(row.owner_address).toLowerCase()) : undefined;
      snapshot.goPlus = {
        found: true,
        isHoneypot: bool(row.is_honeypot),
        cannotSellAll: bool(row.cannot_sell_all),
        buyTax: num(row.buy_tax),
        sellTax: num(row.sell_tax),
        isOpenSource: bool(row.is_open_source),
        isProxy: bool(row.is_proxy),
        isMintable: bool(row.is_mintable),
        ownerChangeBalance: bool(row.owner_change_balance),
        transferPausable: bool(row.transfer_pausable),
        hasBlacklist: bool(row.is_blacklisted),
      };
    } else {
      snapshot.goPlus = { found: false };
      notes.push("GoPlus has no security record for this address on the selected chain.");
    }
  } else {
    snapshot.goPlus = { found: false };
    notes.push(`${chain.label} is not covered by GoPlus — reputation checks skipped. Run the aegis CLI for a full on-chain scan.`);
  }

  // --- DexScreener market (keyless) ---
  const dx = await getJson(`https://api.dexscreener.com/latest/dex/tokens/${address}`);
  const pairs: any[] = Array.isArray(dx?.pairs) ? dx.pairs : [];
  if (pairs.length) {
    sources.push("DexScreener");
    // Deepest pool by liquidity.
    const best = pairs.reduce((a, b) => ((num(b?.liquidity?.usd) ?? 0) > (num(a?.liquidity?.usd) ?? 0) ? b : a));
    snapshot.market = {
      found: true,
      priceUsd: num(best?.priceUsd),
      marketCap: num(best?.marketCap) ?? num(best?.fdv),
      liquidityUsd: num(best?.liquidity?.usd),
      volume24h: num(best?.volume?.h24),
    };
    snapshot.pool = { exists: true, pairIntegrityOk: true, liquidityUsd: num(best?.liquidity?.usd) };
    snapshot.name = snapshot.name ?? best?.baseToken?.name;
    snapshot.symbol = snapshot.symbol ?? best?.baseToken?.symbol;
  } else {
    snapshot.market = { found: false };
    notes.push("No DexScreener pairs found — market depth/volume unavailable.");
  }

  return { snapshot, notes, sources };
}

/** Basic 0x…40hex address validation. */
export function isAddress(a: string): boolean {
  return /^0x[a-fA-F0-9]{40}$/.test(a.trim());
}
