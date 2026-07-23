"""Proxy and upgradeable contract detection.

Proxied tokens can have their logic changed at any time by the admin. This
check reads the EIP-1967 implementation slot to detect transparent/UUPS
proxies and flags them as an elevated risk — the contract you audit today
may behave differently tomorrow.
"""

from __future__ import annotations

from ..models import CheckResult, Severity
from .base import Context

EIP1967_IMPL_SLOT = "0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc"
EIP1967_ADMIN_SLOT = "0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103"


class ProxyDetectionCheck:
    """Read EIP-1967 storage slots to detect proxy patterns."""

    id = "CONTRACT-PROXY"

    async def run(self, ctx: Context) -> list[CheckResult]:
        if ctx.cache.get("token_code_size") == 0:
            return []

        try:
            impl_raw = await ctx.rpc._call(
                "eth_getStorageAt",
                [ctx.request.token, EIP1967_IMPL_SLOT, "latest"],
            )
            impl = str(impl_raw).lower().removeprefix("0x").lstrip("0")
        except Exception:
            return []

        if impl and impl != "0" * 40 and len(impl) >= 38:
            impl_addr = "0x" + impl[-40:]
            ctx.cache["proxy_implementation"] = impl_addr

            try:
                admin_raw = await ctx.rpc._call(
                    "eth_getStorageAt",
                    [ctx.request.token, EIP1967_ADMIN_SLOT, "latest"],
                )
                admin = str(admin_raw).lower().removeprefix("0x").lstrip("0")
                admin_addr = "0x" + admin[-40:] if admin and admin != "0" * 40 else None
            except Exception:
                admin_addr = None

            evidence = {"implementation": impl_addr}
            if admin_addr:
                evidence["admin"] = admin_addr

            return [
                CheckResult(
                    check=self.id,
                    severity=Severity.WARN,
                    score=20,
                    title="Token is a proxy contract (EIP-1967)",
                    detail=(
                        "The token uses an upgradeable proxy pattern. The admin can change "
                        "the contract logic at any time. Verify the implementation address "
                        "and confirm it has been audited."
                    ),
                    evidence=evidence,
                )
            ]

        return [
            CheckResult(
                check=self.id,
                severity=Severity.OK,
                score=0,
                title="No proxy pattern detected",
                detail="EIP-1967 implementation slot is empty — not an upgradeable proxy.",
            )
        ]
