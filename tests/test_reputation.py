"""Tests for GoPlus-backed reputation checks."""

import pytest

from hoodtrade.checks.reputation import (
    ReputationHoneypotCheck,
    ReputationPermissionsCheck,
    ReputationSourceCheck,
)
from hoodtrade.models import Severity
from hoodtrade.sources.goplus import GoPlusReport


def _rep(**kwargs) -> GoPlusReport:
    return GoPlusReport(address="0xabc", chain_id=1, **kwargs)


@pytest.mark.asyncio
async def test_no_data_returns_nothing(make_context):
    ctx = make_context(rpc=None)  # no goplus in cache
    assert await ReputationHoneypotCheck().run(ctx) == []
    assert await ReputationPermissionsCheck().run(ctx) == []
    assert await ReputationSourceCheck().run(ctx) == []


@pytest.mark.asyncio
async def test_honeypot_flag_is_danger(make_context):
    ctx = make_context(rpc=None, cache={"goplus": _rep(is_honeypot=True)})
    results = await ReputationHoneypotCheck().run(ctx)
    assert any(r.severity is Severity.DANGER for r in results)


@pytest.mark.asyncio
async def test_extreme_tax_is_danger(make_context):
    ctx = make_context(rpc=None, cache={"goplus": _rep(buy_tax=0.0, sell_tax=0.99)})
    results = await ReputationHoneypotCheck().run(ctx)
    assert any(r.severity is Severity.DANGER and "tax" in r.title.lower() for r in results)


@pytest.mark.asyncio
async def test_high_tax_is_warn(make_context):
    ctx = make_context(rpc=None, cache={"goplus": _rep(buy_tax=0.12, sell_tax=0.12)})
    results = await ReputationHoneypotCheck().run(ctx)
    assert any(r.severity is Severity.WARN for r in results)


@pytest.mark.asyncio
async def test_zero_tax_no_honeypot_is_quiet(make_context):
    ctx = make_context(rpc=None, cache={"goplus": _rep(is_honeypot=False, buy_tax=0.0, sell_tax=0.0)})
    results = await ReputationHoneypotCheck().run(ctx)
    assert results == []


@pytest.mark.asyncio
async def test_dangerous_permissions_flagged(make_context):
    rep = _rep(
        owner_change_balance=True,
        can_take_back_ownership=True,
        is_mintable=True,
        transfer_pausable=True,
    )
    ctx = make_context(rpc=None, cache={"goplus": rep})
    results = await ReputationPermissionsCheck().run(ctx)
    titles = {r.title for r in results}
    assert "Owner can modify balances" in titles
    assert "Ownership can be reclaimed" in titles
    assert any(r.severity is Severity.DANGER for r in results)


@pytest.mark.asyncio
async def test_clean_permissions_is_ok(make_context):
    rep = _rep(
        owner_change_balance=False,
        can_take_back_ownership=False,
        hidden_owner=False,
        is_mintable=False,
        transfer_pausable=False,
        is_blacklisted=False,
    )
    ctx = make_context(rpc=None, cache={"goplus": rep})
    results = await ReputationPermissionsCheck().run(ctx)
    assert len(results) == 1
    assert results[0].severity is Severity.OK


@pytest.mark.asyncio
async def test_unverified_source_is_warn(make_context):
    ctx = make_context(rpc=None, cache={"goplus": _rep(is_open_source=False)})
    results = await ReputationSourceCheck().run(ctx)
    assert any(r.severity is Severity.WARN for r in results)


@pytest.mark.asyncio
async def test_low_holder_count_is_warn(make_context):
    ctx = make_context(rpc=None, cache={"goplus": _rep(is_open_source=True, holder_count=10)})
    results = await ReputationSourceCheck().run(ctx)
    assert any(r.severity is Severity.WARN and "holder" in r.title.lower() for r in results)
