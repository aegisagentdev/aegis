"""Reputation checks backed by the GoPlus token-security data source.

These consume a pre-fetched ``GoPlusReport`` stashed in ``ctx.cache["goplus"]``
by the engine. They are strictly additive: when GoPlus has no data (new token,
unsupported chain, or the source was disabled) every check returns nothing and
the on-chain battery stands alone. GoPlus flags never set the verdict directly —
they contribute score and evidence like any other finding.
"""

from __future__ import annotations

from ..models import CheckResult, Severity
from ..sources.goplus import GoPlusReport
from .base import Context


def _report(ctx: Context) -> GoPlusReport | None:
    data = ctx.cache.get("goplus")
    return data if isinstance(data, GoPlusReport) else None


class ReputationHoneypotCheck:
    """GoPlus honeypot + trading-tax signal, independent of our eth_call sim."""

    id = "REP-HONEYPOT"

    async def run(self, ctx: Context) -> list[CheckResult]:
        rep = _report(ctx)
        if rep is None:
            return []
        out: list[CheckResult] = []

        if rep.is_honeypot:
            out.append(
                CheckResult(
                    check=self.id,
                    severity=Severity.DANGER,
                    score=90,
                    title="GoPlus flags this as a honeypot",
                    detail=(
                        "GoPlus Security reports is_honeypot=1 for this token. Independent of "
                        "our own transfer simulation, external scanners see sells being blocked "
                        "or reverted. Do not buy."
                    ),
                    evidence={"source": "goplus", "is_honeypot": "1"},
                )
            )

        buy = rep.buy_tax if rep.buy_tax is not None else 0.0
        sell = rep.sell_tax if rep.sell_tax is not None else 0.0
        worst = max(buy, sell)
        if worst >= 0.50:
            out.append(
                CheckResult(
                    check=self.id,
                    severity=Severity.DANGER,
                    score=80,
                    title=f"Extreme trading tax ({worst:.0%})",
                    detail=(
                        f"GoPlus reports buy tax {buy:.0%} / sell tax {sell:.0%}. A tax this high "
                        "means most of your position is confiscated on entry or exit — a common "
                        "soft-rug pattern."
                    ),
                    evidence={"source": "goplus", "buy_tax": str(buy), "sell_tax": str(sell)},
                )
            )
        elif worst >= 0.10:
            out.append(
                CheckResult(
                    check=self.id,
                    severity=Severity.WARN,
                    score=25,
                    title=f"High trading tax ({worst:.0%})",
                    detail=(
                        f"GoPlus reports buy tax {buy:.0%} / sell tax {sell:.0%}. Factor this into "
                        "your expected slippage — it is charged on top of AMM price impact."
                    ),
                    evidence={"source": "goplus", "buy_tax": str(buy), "sell_tax": str(sell)},
                )
            )
        elif worst > 0.0:
            out.append(
                CheckResult(
                    check=self.id,
                    severity=Severity.INFO,
                    score=0,
                    title=f"Small trading tax ({worst:.1%})",
                    detail=f"GoPlus reports buy tax {buy:.1%} / sell tax {sell:.1%}.",
                    evidence={"source": "goplus"},
                )
            )
        return out


class ReputationPermissionsCheck:
    """Dangerous admin capabilities GoPlus surfaces from bytecode analysis."""

    id = "REP-PERMISSIONS"

    async def run(self, ctx: Context) -> list[CheckResult]:
        rep = _report(ctx)
        if rep is None:
            return []
        out: list[CheckResult] = []

        flags = [
            (
                rep.can_take_back_ownership,
                Severity.DANGER,
                60,
                "Ownership can be reclaimed",
                (
                    "GoPlus reports can_take_back_ownership=1: a renounced owner can be restored, "
                    "so any 'ownership renounced' claim is not final."
                ),
            ),
            (
                rep.owner_change_balance,
                Severity.DANGER,
                70,
                "Owner can modify balances",
                (
                    "GoPlus reports owner_change_balance=1: the owner can arbitrarily change holder "
                    "balances, effectively minting or zeroing your position."
                ),
            ),
            (
                rep.hidden_owner,
                Severity.DANGER,
                55,
                "Hidden owner detected",
                (
                    "GoPlus reports hidden_owner=1: privileged control is retained through a "
                    "non-obvious mechanism even if owner() looks renounced."
                ),
            ),
            (
                rep.is_mintable,
                Severity.WARN,
                20,
                "Supply is mintable",
                ("GoPlus reports is_mintable=1: the supply can be inflated, diluting holders."),
            ),
            (
                rep.transfer_pausable,
                Severity.WARN,
                25,
                "Transfers can be paused",
                ("GoPlus reports transfer_pausable=1: an admin can freeze all transfers, trapping your position."),
            ),
            (
                rep.is_blacklisted,
                Severity.WARN,
                20,
                "Blacklist function present",
                ("GoPlus reports is_blacklisted=1: specific addresses can be blocked from trading."),
            ),
        ]
        for present, severity, score, title, detail in flags:
            if present:
                out.append(
                    CheckResult(
                        check=self.id,
                        severity=severity,
                        score=score,
                        title=title,
                        detail=detail,
                        evidence={"source": "goplus"},
                    )
                )
        if not out:
            out.append(
                CheckResult(
                    check=self.id,
                    severity=Severity.OK,
                    score=0,
                    title="No dangerous admin permissions",
                    detail="GoPlus found no mint / pause / blacklist / balance-change powers.",
                    evidence={"source": "goplus"},
                )
            )
        return out


class ReputationSourceCheck:
    """Verified-source and holder-count context from GoPlus."""

    id = "REP-SOURCE"

    async def run(self, ctx: Context) -> list[CheckResult]:
        rep = _report(ctx)
        if rep is None:
            return []
        out: list[CheckResult] = []

        if rep.is_open_source is False:
            out.append(
                CheckResult(
                    check=self.id,
                    severity=Severity.WARN,
                    score=20,
                    title="Contract source is not verified",
                    detail=(
                        "GoPlus reports is_open_source=0: the contract's source is not published, "
                        "so its behavior cannot be reviewed. Treat unverified tokens with caution."
                    ),
                    evidence={"source": "goplus"},
                )
            )
        elif rep.is_open_source is True:
            out.append(
                CheckResult(
                    check=self.id,
                    severity=Severity.OK,
                    score=0,
                    title="Source verified",
                    detail="GoPlus reports the contract source is open/verified.",
                    evidence={"source": "goplus"},
                )
            )

        if rep.holder_count is not None:
            sev = Severity.WARN if rep.holder_count < 50 else Severity.INFO
            score = 15 if rep.holder_count < 50 else 0
            out.append(
                CheckResult(
                    check=self.id,
                    severity=sev,
                    score=score,
                    title=f"{rep.holder_count:,} holders",
                    detail=(
                        f"GoPlus reports {rep.holder_count:,} holders."
                        + (" Very few holders concentrate exit risk." if rep.holder_count < 50 else "")
                    ),
                    evidence={"source": "goplus", "holder_count": str(rep.holder_count)},
                )
            )
        return out
