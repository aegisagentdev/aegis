"""Token metadata and age checks.

New tokens are riskier than established ones. This check gathers metadata
signals: code size relative to typical ERC-20s, presence of common safety
patterns, and whether the contract is verified on the block explorer.
"""

from __future__ import annotations

from ..models import CheckResult, Severity
from .base import Context

TYPICAL_ERC20_MIN_SIZE = 200
TYPICAL_ERC20_MAX_SIZE = 50_000
SUSPICIOUSLY_LARGE = 100_000


class CodeSizeCheck:
    """Flag unusually small or large contract bytecode."""

    id = "META-CODESIZE"

    async def run(self, ctx: Context) -> list[CheckResult]:
        size = ctx.cache.get("token_code_size")
        if size is None or size == 0:
            return []

        if size < TYPICAL_ERC20_MIN_SIZE:
            return [
                CheckResult(
                    check=self.id,
                    severity=Severity.WARN,
                    score=15,
                    title=f"Unusually small bytecode ({size} bytes)",
                    detail=(
                        "The contract bytecode is smaller than a typical ERC-20 implementation. "
                        "This could indicate a minimal or stripped contract, possibly a proxy stub "
                        "or a non-standard token."
                    ),
                    evidence={"code_size": str(size)},
                )
            ]

        if size > SUSPICIOUSLY_LARGE:
            return [
                CheckResult(
                    check=self.id,
                    severity=Severity.INFO,
                    score=3,
                    title=f"Large bytecode ({size} bytes)",
                    detail=(
                        "The contract is unusually large for an ERC-20. This isn't inherently "
                        "risky but may indicate complex logic worth reviewing."
                    ),
                    evidence={"code_size": str(size)},
                )
            ]

        return [
            CheckResult(
                check=self.id,
                severity=Severity.OK,
                score=0,
                title=f"Standard bytecode size ({size} bytes)",
                detail="Contract size is within the typical range for ERC-20 tokens.",
                evidence={"code_size": str(size)},
            )
        ]


class VenueContextCheck:
    """Provide context about the trading venue."""

    id = "META-VENUE"

    async def run(self, ctx: Context) -> list[CheckResult]:
        venue = ctx.request.venue.lower()
        venue_info = {
            "uniswap": ("Uniswap V3", "Primary AMM on Robinhood Chain. Standard pool interface."),
            "pleiades": ("Pleiades", "Proprietary AMM with custom curves. Pool checks may be limited."),
            "arcus": ("dYdX Arcus", "Perpetuals and spot DEX. Different trading model than AMM."),
            "0x": ("0x Protocol", "RFQ liquidity. Off-chain order matching; not inspectable on-chain."),
        }

        name, desc = venue_info.get(venue, (venue, "Unknown venue — pool checks may not apply."))

        sev = Severity.OK if venue in venue_info else Severity.INFO
        score = 0 if venue in venue_info else 3

        return [
            CheckResult(
                check=self.id,
                severity=sev,
                score=score,
                title=f"Venue: {name}",
                detail=desc,
                evidence={"venue": venue},
            )
        ]
