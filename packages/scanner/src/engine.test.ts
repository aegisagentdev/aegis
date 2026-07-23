import assert from "node:assert/strict";
import { test } from "node:test";
import { runScan } from "./engine.js";
import { DEFAULT_SETTINGS } from "./types.js";
import { FIXTURES, fixtureByKey } from "./fixtures.js";
import type { TradeRequest } from "./types.js";

const req: TradeRequest = { token: "0x0", quote: "USDG", amountUsd: 1000, direction: "buy" };

test("clean stablecoin returns GO", () => {
  const r = runScan(fixtureByKey("usdg")!.snapshot, req, DEFAULT_SETTINGS);
  assert.equal(r.verdict, "GO");
});

test("honeypot returns NO-GO with a danger finding", () => {
  const r = runScan(fixtureByKey("honeypot")!.snapshot, req, DEFAULT_SETTINGS);
  assert.equal(r.verdict, "NO-GO");
  assert.ok(r.results.some((c) => c.severity === "danger"));
});

test("thin memecoin returns CAUTION (lenient young-chain mode)", () => {
  const r = runScan(fixtureByKey("thin")!.snapshot, req, { ...DEFAULT_SETTINGS, lenient: true });
  assert.equal(r.verdict, "CAUTION");
});

test("divergent stock token returns NO-GO", () => {
  const r = runScan(fixtureByKey("rif")!.snapshot, req, DEFAULT_SETTINGS);
  assert.equal(r.verdict, "NO-GO");
  assert.ok(r.results.some((c) => c.check === "STOCK-DIVERGENCE" && c.severity === "danger"));
});

test("a DANGER finding forces NO-GO regardless of total score", () => {
  const r = runScan(fixtureByKey("honeypot")!.snapshot, req, { ...DEFAULT_SETTINGS, nogoScore: 100000 });
  assert.equal(r.verdict, "NO-GO");
});

test("oversized trade escalates via price impact", () => {
  const big: TradeRequest = { ...req, amountUsd: 400_000 };
  const r = runScan(fixtureByKey("usdg")!.snapshot, big, DEFAULT_SETTINGS);
  assert.ok(r.results.some((c) => c.check === "EXEC-IMPACT" && c.severity !== "ok"));
});

test("every fixture scans without throwing", () => {
  for (const f of FIXTURES) {
    const r = runScan(f.snapshot, req, { ...DEFAULT_SETTINGS, lenient: true });
    assert.ok(["GO", "CAUTION", "NO-GO", "UNKNOWN"].includes(r.verdict));
  }
});
