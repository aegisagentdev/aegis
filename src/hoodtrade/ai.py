"""AI risk-summary layer.

The deterministic engine produces a verdict and a list of structured findings. This
module turns those findings into a short, plain-language brief for the trader using
Claude. It is strictly explanatory: it is given the already-decided verdict and the
findings, and asked to summarize — it cannot change the go/no-go call.

If the ``anthropic`` package or an API key is unavailable, ``summarize`` returns a
deterministic template built from the findings, so the scanner is fully functional
offline.
"""

from __future__ import annotations

import json

from .config import Settings
from .models import RiskSummary, ScanReport, Severity

_SYSTEM = (
    "You are the risk-explanation layer of Hood Trade, a pre-trade safety scanner for the "
    "Robinhood Chain (an Arbitrum-Orbit L2). You are given a trade, a verdict that has "
    "ALREADY been decided by deterministic on-chain checks, and the list of findings. "
    "Your job is only to explain the risk to a trader in plain language. Do not contradict "
    "or second-guess the verdict. Do not invent findings that are not in the input. Never "
    "give financial advice or tell the user whether to buy — describe risk and what they "
    "can verify. Be concise and specific."
)


def _template_summary(report: ScanReport) -> RiskSummary:
    ordered = sorted(
        report.results,
        key=lambda r: [Severity.DANGER, Severity.WARN, Severity.INFO, Severity.OK].index(r.severity),
    )
    risks = [f"{r.title}: {r.detail}" for r in ordered if r.severity in (Severity.DANGER, Severity.WARN)]
    headline = {
        "NO-GO": "High-risk trade — the scanner flagged blocking issues.",
        "CAUTION": "Proceed carefully — the scanner found notable risks.",
        "GO": "No blocking issues found by the automated checks.",
        "UNKNOWN": "Inconclusive — the scanner could not gather enough data.",
    }[report.verdict.value]
    return RiskSummary(
        headline=headline,
        key_risks=risks[:5] or ["No warning- or danger-level findings."],
        what_to_check=[
            "Confirm the token and pool addresses against the project's official source.",
            "Check the pool's real depth for your size on the DEX UI before signing.",
            "Set a tight slippage limit; split large orders or route via an aggregator.",
        ],
    )


def summarize(report: ScanReport, settings: Settings) -> RiskSummary:
    if not settings.ai_enabled:
        return _template_summary(report)
    try:
        import anthropic
    except ImportError:
        return _template_summary(report)

    try:
        client = anthropic.Anthropic()  # resolves ANTHROPIC_API_KEY from env
    except Exception:  # noqa: BLE001 — no/invalid credentials -> offline fallback
        return _template_summary(report)

    payload = {
        "trade": report.request.model_dump(mode="json"),
        "verdict": report.verdict.value,
        "score": report.score,
        "findings": [r.model_dump(mode="json") for r in report.results],
    }
    try:
        response = client.messages.parse(
            model=settings.ai_model,
            max_tokens=1500,
            thinking={"type": "adaptive"},
            system=_SYSTEM,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Summarize the risk of this Robinhood Chain trade for the user. "
                        "Return the verdict-consistent brief.\n\n"
                        + json.dumps(payload, indent=2)
                    ),
                }
            ],
            output_format=RiskSummary,
        )
        parsed = response.parsed_output
        if parsed is not None:
            return parsed
    except Exception:  # noqa: BLE001 — any API failure degrades to the template
        pass
    return _template_summary(report)
