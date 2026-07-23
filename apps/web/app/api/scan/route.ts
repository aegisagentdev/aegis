import { NextResponse } from "next/server";
import { runScan, DEFAULT_SETTINGS } from "@aegis/scanner";
import { fixtureByKey, FIXTURES } from "@aegis/scanner/fixtures";
import { buildLiveSnapshot, isAddress, LIVE_CHAINS } from "@/lib/live";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  return NextResponse.json({
    tokens: FIXTURES.map((f) => ({ key: f.key, label: f.label, address: f.address, blurb: f.blurb })),
    chains: LIVE_CHAINS.map((c) => ({ key: c.key, label: c.label, live: c.goplus != null })),
  });
}

/**
 * Way-out gate. Two modes:
 *  - { address, chain }  → real scan on live GoPlus + DexScreener data.
 *  - { token }           → curated sample fixture (for a guaranteed demo).
 */
export async function POST(req: Request) {
  try {
    const body = await req.json();
    const amountUsd = Number.isFinite(body?.amountUsd) ? Math.max(1, Number(body.amountUsd)) : 1000;
    const settings = { ...DEFAULT_SETTINGS, lenient: true };

    if (typeof body?.address === "string" && body.address.trim()) {
      const address = body.address.trim();
      if (!isAddress(address)) {
        return NextResponse.json({ error: "That is not a valid 0x… contract address." }, { status: 400 });
      }
      const chain = typeof body?.chain === "string" ? body.chain : "ethereum";
      const { snapshot, notes, sources } = await buildLiveSnapshot(address, chain);
      const report = runScan(snapshot, { token: address, quote: "native", amountUsd, direction: "buy" }, settings);
      return NextResponse.json({ ...report, notes: [...report.notes, ...notes], live: true, sources, chain });
    }

    const fx = fixtureByKey(body?.token ?? "");
    if (!fx) return NextResponse.json({ error: "unknown token" }, { status: 400 });
    const report = runScan(fx.snapshot, { token: fx.address, quote: "USDG", amountUsd, direction: "buy" }, settings);
    return NextResponse.json({ ...report, live: false, sources: ["sample data"] });
  } catch {
    return NextResponse.json({ error: "bad request" }, { status: 400 });
  }
}
