"""Example: send scan results to a webhook (Slack, Discord, etc.)."""

import asyncio
import json

import httpx

from aegis.config import Settings
from aegis.engine import run_scan
from aegis.models import Direction, TradeRequest, Verdict

WEBHOOK_URL = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"


def format_slack_message(report) -> dict:
    emoji = {"GO": ":white_check_mark:", "CAUTION": ":warning:", "NO": ":no_entry:", "UNKNOWN": ":question:"}
    color = {"GO": "#2ecc71", "CAUTION": "#f39c12", "NO": "#e74c3c", "UNKNOWN": "#95a5a6"}

    findings = "\n".join(
        f"• [{r.severity.value}] {r.title}" for r in report.results if r.severity.value in ("warn", "danger")
    )

    return {
        "attachments": [
            {
                "color": color.get(report.verdict.value, "#95a5a6"),
                "title": f"{emoji.get(report.verdict.value, '')} Aegis: {report.verdict.value}",
                "text": f"Score: {report.score}\nToken: {report.request.token}\n\n{findings or 'No issues found.'}",
                "footer": "Aegis Pre-Trade Scanner",
            }
        ]
    }


async def main():
    settings = Settings()
    settings.ai_enabled = False

    request = TradeRequest(
        token="0x2222222222222222222222222222222222222222",
        quote="0x3333333333333333333333333333333333333333",
        amount_usd=5000,
        direction=Direction.BUY,
    )

    report = await run_scan(request, settings)
    payload = format_slack_message(report)

    print(json.dumps(payload, indent=2))

    # Uncomment to actually send:
    # async with httpx.AsyncClient() as client:
    #     await client.post(WEBHOOK_URL, json=payload)


if __name__ == "__main__":
    asyncio.run(main())
