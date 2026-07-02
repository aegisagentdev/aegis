"""Example: run a Hood Trade scan programmatically from Python."""

import asyncio
import json

from hoodtrade.config import Settings
from hoodtrade.engine import run_scan
from hoodtrade.export import to_json, to_markdown, severity_counts
from hoodtrade.models import Direction, TradeRequest


async def main():
    settings = Settings()
    settings.ai_enabled = False  # skip AI for this example

    request = TradeRequest(
        token="0x2222222222222222222222222222222222222222",
        quote="0x3333333333333333333333333333333333333333",
        amount_usd=5000,
        direction=Direction.BUY,
        pool="0x4444444444444444444444444444444444444444",
        venue="uniswap",
    )

    report = await run_scan(request, settings)

    # Access structured data
    print(f"Verdict: {report.verdict.value}")
    print(f"Score:   {report.score}")
    print(f"Checks:  {len(report.results)}")
    print(f"Worst:   {report.worst.value}")
    print()

    # Severity breakdown
    counts = severity_counts(report)
    print(f"Severity counts: {counts}")
    print()

    # Export as JSON
    print("--- JSON ---")
    print(to_json(report))
    print()

    # Export as Markdown
    print("--- Markdown ---")
    print(to_markdown(report))


if __name__ == "__main__":
    asyncio.run(main())
