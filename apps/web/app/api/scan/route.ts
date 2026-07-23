import { NextResponse } from "next/server";
import { runScan, DEFAULT_SETTINGS } from "@aegis/scanner";
import { fixtureByKey, FIXTURES } from "@aegis/scanner/fixtures";

export async function GET() {
  return NextResponse.json({
    tokens: FIXTURES.map((f) => ({ key: f.key, label: f.label, address: f.address, blurb: f.blurb })),
  });
}

/** Way-out gate: run the pre-trade scanner over a chosen token fixture. */
export async function POST(req: Request) {
  try {
    const body = await req.json();
    const fx = fixtureByKey(body?.token ?? "");
    if (!fx) return NextResponse.json({ error: "unknown token" }, { status: 400 });

    const amountUsd = Number.isFinite(body?.amountUsd) ? Math.max(1, Number(body.amountUsd)) : 1000;
    // Robinhood Chain is young — relax market-maturity gates, keep security gates hard.
    const settings = { ...DEFAULT_SETTINGS, lenient: true };
    const report = runScan(
      fx.snapshot,
      { token: fx.address, quote: "USDG", amountUsd, direction: "buy" },
      settings,
    );
    return NextResponse.json(report);
  } catch {
    return NextResponse.json({ error: "bad request" }, { status: 400 });
  }
}
