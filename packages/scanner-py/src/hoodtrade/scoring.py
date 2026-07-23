"""Scoring utilities for risk aggregation.

Provides helpers for weighted scoring, score normalization, and risk
categorization beyond the simple sum used in the engine.
"""

from __future__ import annotations

from .models import CheckResult, Severity

SEVERITY_WEIGHT = {
    Severity.OK: 0,
    Severity.INFO: 1,
    Severity.WARN: 3,
    Severity.DANGER: 10,
}


def weighted_score(results: list[CheckResult]) -> float:
    if not results:
        return 0.0
    total = sum(r.score * SEVERITY_WEIGHT.get(r.severity, 1) for r in results)
    return total / len(results)


def normalize_score(score: int, max_score: int = 200) -> float:
    return min(score / max_score, 1.0) if max_score > 0 else 0.0


def risk_level(score: int, caution: int = 25, nogo: int = 60) -> str:
    if score >= nogo:
        return "high"
    if score >= caution:
        return "medium"
    return "low"


def danger_count(results: list[CheckResult]) -> int:
    return sum(1 for r in results if r.severity is Severity.DANGER)


def warn_count(results: list[CheckResult]) -> int:
    return sum(1 for r in results if r.severity is Severity.WARN)


def passing_count(results: list[CheckResult]) -> int:
    return sum(1 for r in results if r.severity is Severity.OK)


def score_breakdown(results: list[CheckResult]) -> dict[str, int]:
    breakdown: dict[str, int] = {}
    for r in results:
        area = r.check.split("-")[0] if "-" in r.check else r.check
        breakdown[area] = breakdown.get(area, 0) + r.score
    return breakdown
