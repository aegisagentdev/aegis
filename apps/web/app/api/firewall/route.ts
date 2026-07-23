import { NextResponse } from "next/server";
import { scanText } from "@aegis/firewall";

/** Way-in gate: scan an untrusted MCP tool response for prompt injection. */
export async function POST(req: Request) {
  try {
    const body = await req.json();
    const text = typeof body?.text === "string" ? body.text : "";
    if (!text.trim()) {
      return NextResponse.json({ error: "empty text" }, { status: 400 });
    }
    const result = scanText(text.slice(0, 8000), {
      source: { server: body?.server ?? "demo", tool: body?.tool ?? "tool_response" },
    });
    return NextResponse.json(result);
  } catch {
    return NextResponse.json({ error: "bad request" }, { status: 400 });
  }
}
