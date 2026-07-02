"""Contract-level safety checks.

Robinhood Chain launched with FCFS sequencing (which structurally blunts gas-auction
sandwiching), but it is permissionless and brand new — anyone can deploy, and the
token you are about to buy may be days old. These checks look at the token contract
itself, independent of the pool.
"""

from __future__ import annotations

from ..models import CheckResult, Severity
from ..rpc import decode_address, decode_string, decode_uint
from .base import Context

# EOA / empty code = not a contract at all. Buying a "token" with no code is a
# guaranteed loss (there is nothing to sell back).
ZERO = "0x" + "0" * 40


class ContractExistsCheck:
    id = "CONTRACT-EXISTS"

    async def run(self, ctx: Context) -> list[CheckResult]:
        code = await ctx.rpc.get_code(ctx.request.token)
        ctx.cache["token_code_size"] = len(code)
        if len(code) == 0:
            return [
                CheckResult(
                    check=self.id,
                    severity=Severity.DANGER,
                    score=100,
                    title="Token address has no contract code",
                    detail=(
                        "The token address is an externally-owned account or an undeployed "
                        "address. There is no ERC-20 to trade; a swap here cannot be reversed."
                    ),
                    evidence={"code_size": "0"},
                )
            ]
        return [
            CheckResult(
                check=self.id,
                severity=Severity.OK,
                score=0,
                title="Contract code present",
                detail=f"Token has {len(code)} bytes of deployed code.",
                evidence={"code_size": str(len(code))},
            )
        ]


class OwnershipCheck:
    id = "CONTRACT-OWNER"

    async def run(self, ctx: Context) -> list[CheckResult]:
        if ctx.cache.get("token_code_size") == 0:
            return []  # nothing to inspect
        owner = ZERO
        for fn in ("owner", "getOwner"):
            try:
                from ..rpc import encode_call

                raw = await ctx.rpc.eth_call(ctx.request.token, encode_call(fn))
                addr = decode_address(raw)
                if addr != ZERO:
                    owner = addr
                    break
            except Exception:  # noqa: BLE001 — absence of owner() is a finding, not an error
                continue

        if owner == ZERO:
            return [
                CheckResult(
                    check=self.id,
                    severity=Severity.OK,
                    score=0,
                    title="No active owner / renounced",
                    detail="No owner() found or ownership is renounced. Admin-key rug risk is lower.",
                )
            ]
        return [
            CheckResult(
                check=self.id,
                severity=Severity.WARN,
                score=15,
                title="Token has an active owner",
                detail=(
                    "An owner address can often pause transfers, mint supply, or change fees. "
                    "Not inherently malicious, but it is a live admin key you are trusting."
                ),
                evidence={"owner": owner},
            )
        ]


class SupplySanityCheck:
    id = "CONTRACT-SUPPLY"

    async def run(self, ctx: Context) -> list[CheckResult]:
        if ctx.cache.get("token_code_size") == 0:
            return []
        from ..rpc import encode_call

        try:
            name = decode_string(await ctx.rpc.eth_call(ctx.request.token, encode_call("name")))
            symbol = decode_string(await ctx.rpc.eth_call(ctx.request.token, encode_call("symbol")))
            supply = decode_uint(await ctx.rpc.eth_call(ctx.request.token, encode_call("totalSupply")))
        except Exception as exc:  # noqa: BLE001
            return [
                CheckResult(
                    check=self.id,
                    severity=Severity.WARN,
                    score=20,
                    title="Token does not implement standard ERC-20 reads",
                    detail=(
                        "name()/symbol()/totalSupply() did not decode. A non-standard token "
                        "can behave unpredictably in AMMs. Reason: " + str(exc)
                    ),
                )
            ]
        ctx.cache["token_symbol"] = symbol
        ctx.cache["token_name"] = name
        if supply == 0:
            return [
                CheckResult(
                    check=self.id,
                    severity=Severity.WARN,
                    score=15,
                    title="Zero total supply",
                    detail="totalSupply() is 0. Unusual for a live, tradable token.",
                    evidence={"name": name, "symbol": symbol},
                )
            ]
        return [
            CheckResult(
                check=self.id,
                severity=Severity.OK,
                score=0,
                title=f"Standard ERC-20: {symbol}",
                detail=f"{name} ({symbol}), total supply {supply}.",
                evidence={"name": name, "symbol": symbol, "total_supply": str(supply)},
            )
        ]
