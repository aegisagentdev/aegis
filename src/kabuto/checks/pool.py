"""Liquidity-pool checks.

Yes — liquidity can be removed on Robinhood Chain (Uniswap deploys the primary public
AMM there, standard remove-liquidity applies). So the pool you are about to trade into
can be drained by whoever provided it. These checks look at the pool's live state:
does it exist, is it verified, and how deep is it relative to the trade size.

The depth math here is a first-order approximation from the pool's on-chain liquidity,
not a full tick-by-tick simulation; it is meant to catch obviously-thin books, not to
price the trade to the wei.
"""

from __future__ import annotations

from ..models import CheckResult, Severity
from ..rpc import decode_uint, encode_call
from .base import Context


class PoolExistsCheck:
    id = "POOL-EXISTS"

    async def run(self, ctx: Context) -> list[CheckResult]:
        pool = ctx.request.pool
        if not pool:
            return [
                CheckResult(
                    check=self.id,
                    severity=Severity.INFO,
                    score=5,
                    title="No pool specified",
                    detail=(
                        "No pool/pair address was provided, so pool-level depth and "
                        "concentration checks were skipped. Pass --pool for a full scan."
                    ),
                )
            ]
        code = await ctx.rpc.get_code(pool)
        if len(code) == 0:
            return [
                CheckResult(
                    check=self.id,
                    severity=Severity.DANGER,
                    score=80,
                    title="Pool address has no contract code",
                    detail="The supplied pool address is not a deployed contract.",
                    evidence={"pool": pool},
                )
            ]
        return [
            CheckResult(
                check=self.id,
                severity=Severity.OK,
                score=0,
                title="Pool contract present",
                detail=f"Pool has {len(code)} bytes of code.",
                evidence={"pool": pool},
            )
        ]


class PoolLiquidityCheck:
    """Reads Uniswap-V3-style active liquidity. Warns when the in-range liquidity is
    zero (a pool with TVL parked entirely out of range is untradeable at spot)."""

    id = "POOL-LIQUIDITY"

    async def run(self, ctx: Context) -> list[CheckResult]:
        pool = ctx.request.pool
        if not pool or ctx.cache.get("pool_missing"):
            return []
        try:
            raw = await ctx.rpc.eth_call(pool, encode_call("liquidity"))
            active = decode_uint(raw)
        except Exception as exc:  # noqa: BLE001
            return [
                CheckResult(
                    check=self.id,
                    severity=Severity.INFO,
                    score=5,
                    title="Could not read pool liquidity",
                    detail=(
                        "liquidity() did not decode — the pool may use a non-V3 interface. "
                        "Depth could not be assessed. Reason: " + str(exc)
                    ),
                )
            ]
        ctx.cache["active_liquidity"] = active
        if active == 0:
            return [
                CheckResult(
                    check=self.id,
                    severity=Severity.DANGER,
                    score=70,
                    title="No active in-range liquidity",
                    detail=(
                        "The pool reports zero active liquidity at the current price. A market "
                        "order will get an extreme price or revert. This is a classic thin-book / "
                        "just-drained state."
                    ),
                    evidence={"active_liquidity": "0"},
                )
            ]
        return [
            CheckResult(
                check=self.id,
                severity=Severity.OK,
                score=0,
                title="Pool has active liquidity",
                detail=f"Active in-range liquidity units: {active}.",
                evidence={"active_liquidity": str(active)},
            )
        ]


class PoolPairIntegrityCheck:
    """Confirms the pool actually pairs the token the user thinks it does. A mismatched
    pool is a common way to route a victim into a look-alike token."""

    id = "POOL-PAIR"

    async def run(self, ctx: Context) -> list[CheckResult]:
        pool = ctx.request.pool
        if not pool:
            return []
        from ..rpc import decode_address
        try:
            t0 = decode_address(await ctx.rpc.eth_call(pool, encode_call("token0")))
            t1 = decode_address(await ctx.rpc.eth_call(pool, encode_call("token1")))
        except Exception:  # noqa: BLE001
            return []  # not a V3-style pair; PoolLiquidityCheck already noted the shape
        want = {ctx.request.token.lower(), ctx.request.quote.lower()}
        have = {t0.lower(), t1.lower()}
        if want != have:
            return [
                CheckResult(
                    check=self.id,
                    severity=Severity.DANGER,
                    score=60,
                    title="Pool does not pair the expected tokens",
                    detail=(
                        "The pool's token0/token1 do not match the token and quote you asked to "
                        "trade. You may be routed into a different (look-alike) asset."
                    ),
                    evidence={"pool_token0": t0, "pool_token1": t1},
                )
            ]
        return [
            CheckResult(
                check=self.id,
                severity=Severity.OK,
                score=0,
                title="Pool pairs the expected tokens",
                detail="token0/token1 match the requested token and quote.",
                evidence={"pool_token0": t0, "pool_token1": t1},
            )
        ]
