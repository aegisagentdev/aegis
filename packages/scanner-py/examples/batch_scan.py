"""Example: scan multiple tokens in batch and generate a summary report."""

import asyncio

from hoodtrade.config import Settings
from hoodtrade.engine import run_scan
from hoodtrade.models import Direction, TradeRequest, Verdict


TOKENS_TO_SCAN = [
    {
        "name": "Token A",
        "token": "0xAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
        "quote": "0x3333333333333333333333333333333333333333",
        "amount": 1000,
    },
    {
        "name": "Token B",
        "token": "0xBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
        "quote": "0x3333333333333333333333333333333333333333",
        "amount": 5000,
    },
    {
        "name": "Token C",
        "token": "0xCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC",
        "quote": "0x3333333333333333333333333333333333333333",
        "amount": 50000,
    },
]


async def scan_one(name: str, settings: Settings, **kwargs) -> tuple[str, str, int]:
    request = TradeRequest(direction=Direction.BUY, **kwargs)
    try:
        report = await run_scan(request, settings)
        return name, report.verdict.value, report.score
    except Exception as exc:
        return name, "ERROR", -1


async def main():
    settings = Settings()
    settings.ai_enabled = False

    tasks = [
        scan_one(t["name"], settings, token=t["token"], quote=t["quote"], amount_usd=t["amount"])
        for t in TOKENS_TO_SCAN
    ]
    results = await asyncio.gather(*tasks)

    print(f"{'Token':<12} {'Verdict':<10} {'Score':<6}")
    print("-" * 30)
    for name, verdict, score in results:
        print(f"{name:<12} {verdict:<10} {score:<6}")

    go_count = sum(1 for _, v, _ in results if v == Verdict.GO.value)
    caution_count = sum(1 for _, v, _ in results if v == Verdict.CAUTION.value)
    nogo_count = sum(1 for _, v, _ in results if v in (Verdict.NO_GO.value, "ERROR"))

    print(f"\nSummary: {go_count} GO, {caution_count} CAUTION, {nogo_count} NO-GO/ERROR")


if __name__ == "__main__":
    asyncio.run(main())
