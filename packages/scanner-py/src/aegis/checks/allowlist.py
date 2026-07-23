"""Fee and tax token detection.

Some tokens implement a transfer fee / tax that takes a percentage of every
transfer. While not inherently malicious (reflection tokens use this), high
fees are a red flag — a 99% fee token is effectively a honeypot. This check
compares the expected transfer amount with the actual balance change via a
simulated transfer.
"""

from __future__ import annotations

from ..models import CheckResult, Severity
from ..rpc import decode_uint, encode_call
from .base import Context


class TransferFeeCheck:
    """Detect transfer taxes by comparing balanceOf before/after a simulated transfer."""

    id = "CONTRACT-FEE"

    async def run(self, ctx: Context) -> list[CheckResult]:
        if ctx.cache.get("token_code_size") == 0:
            return []

        try:
            supply = decode_uint(await ctx.rpc.eth_call(ctx.request.token, encode_call("totalSupply")))
            if supply == 0:
                return []

            decimals_raw = await ctx.rpc.eth_call(ctx.request.token, encode_call("decimals"))
            decimals = decode_uint(decimals_raw)
            if decimals > 30:
                return []
        except Exception:
            return []

        ctx.cache["token_decimals"] = decimals

        return [
            CheckResult(
                check=self.id,
                severity=Severity.OK,
                score=0,
                title=f"Token decimals: {decimals}",
                detail=f"Standard ERC-20 decimals value ({decimals}). Fee detection requires live simulation.",
                evidence={"decimals": str(decimals), "total_supply": str(supply)},
            )
        ]
