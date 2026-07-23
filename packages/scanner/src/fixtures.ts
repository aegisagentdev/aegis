/**
 * Demo token snapshots for the web playground. These are illustrative fixtures,
 * not live chain reads — each mirrors a real risk profile the scanner is built
 * to catch. In production the same `TokenSnapshot` is filled from live RPC +
 * GoPlus + DexScreener (see packages/scanner-py for the upstream data layer).
 */

import type { TokenSnapshot } from "./types.js";

export interface Fixture {
  key: string;
  label: string;
  address: string;
  blurb: string;
  snapshot: TokenSnapshot;
}

export const FIXTURES: Fixture[] = [
  {
    key: "usdg",
    label: "USDG — clean stablecoin",
    address: "0x1a2b3c4d5e6f708192a3b4c5d6e7f8091a2b3c4d",
    blurb: "Verified, deep liquidity, renounced. Should return GO.",
    snapshot: {
      chainId: 5678,
      expectedChainId: 5678,
      name: "USD Gold",
      symbol: "USDG",
      codeSize: 12800,
      ownerRenounced: true,
      totalSupply: 250_000_000,
      selfBalance: 0,
      burnedBalance: 0,
      transferRevert: "balance",
      approveRevert: "ok",
      goPlus: { found: true, isHoneypot: false, buyTax: 0, sellTax: 0, isOpenSource: true, isProxy: false, isMintable: false },
      market: { found: true, priceUsd: 1.0, marketCap: 250_000_000, liquidityUsd: 2_100_000, volume24h: 840_000 },
      pool: { exists: true, pairIntegrityOk: true, liquidityUsd: 2_100_000 },
    },
  },
  {
    key: "honeypot",
    label: "MOON — honeypot",
    address: "0xdead111122223333444455556666777788889999",
    blurb: "Buys fine, sells blocked, owner can rewrite balances. Should return NO-GO.",
    snapshot: {
      chainId: 5678,
      expectedChainId: 5678,
      name: "MoonRocket",
      symbol: "MOON",
      codeSize: 4200,
      ownerRenounced: false,
      totalSupply: 1_000_000_000,
      selfBalance: 620_000_000,
      burnedBalance: 0,
      transferRevert: "restriction",
      approveRevert: "restriction",
      goPlus: { found: true, isHoneypot: true, cannotSellAll: true, buyTax: 0.05, sellTax: 0.99, isOpenSource: false, isProxy: true, isMintable: true, ownerChangeBalance: true, transferPausable: true },
      market: { found: true, priceUsd: 0.0004, marketCap: 400_000, liquidityUsd: 8_000, volume24h: 500 },
      pool: { exists: true, pairIntegrityOk: true, liquidityUsd: 8_000 },
    },
  },
  {
    key: "thin",
    label: "PEPE2 — thin memecoin",
    address: "0xabcabcabcabcabcabcabcabcabcabcabcabcabca",
    blurb: "Not a scam, but shallow liquidity and no volume. Should return CAUTION.",
    snapshot: {
      chainId: 5678,
      expectedChainId: 5678,
      name: "Pepe Two",
      symbol: "PEPE2",
      codeSize: 3100,
      ownerRenounced: true,
      totalSupply: 420_000_000,
      selfBalance: 0,
      burnedBalance: 410_000_000,
      transferRevert: "balance",
      approveRevert: "ok",
      goPlus: { found: true, isHoneypot: false, buyTax: 0.02, sellTax: 0.02, isOpenSource: true, isProxy: false, isMintable: false },
      market: { found: true, priceUsd: 0.0000021, marketCap: 90_000, liquidityUsd: 14_000, volume24h: 600 },
      pool: { exists: true, pairIntegrityOk: true, liquidityUsd: 14_000 },
    },
  },
  {
    key: "rif",
    label: "TSLA.rif — divergent stock token",
    address: "0x7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f",
    blurb: "Tokenized stock whose pool price drifts from the reference. Should return NO-GO.",
    snapshot: {
      chainId: 5678,
      expectedChainId: 5678,
      name: "Tesla (tokenized)",
      symbol: "TSLA.rif",
      codeSize: 9800,
      ownerRenounced: true,
      totalSupply: 5_000_000,
      selfBalance: 0,
      burnedBalance: 0,
      transferRevert: "balance",
      approveRevert: "ok",
      goPlus: { found: true, isHoneypot: false, buyTax: 0, sellTax: 0, isOpenSource: true, isProxy: false, isMintable: false },
      market: { found: true, priceUsd: 210, marketCap: 1_050_000_000, liquidityUsd: 320_000, volume24h: 45_000 },
      pool: { exists: true, pairIntegrityOk: true, liquidityUsd: 320_000 },
      stock: { isStockToken: true, hasDisclosure: true, priceDivergence: 0.18 },
    },
  },
];

export function fixtureByKey(key: string): Fixture | undefined {
  return FIXTURES.find((f) => f.key === key);
}
