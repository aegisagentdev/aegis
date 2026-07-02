"""Check protocol + shared context.

A check is an async callable that inspects a proposed trade and returns zero or more
CheckResults. Checks must never raise on ordinary on-chain conditions (missing owner,
unverified source, etc.) — those are *findings*, returned as results. They may raise
on infrastructure failure (RPC down); the engine catches that and records a note.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from ..config import Settings
from ..models import CheckResult, TradeRequest
from ..rpc import RpcClient


@dataclass
class Context:
    request: TradeRequest
    settings: Settings
    rpc: RpcClient
    cache: dict[str, object] = field(default_factory=dict)


class Check(Protocol):
    id: str

    async def run(self, ctx: Context) -> list[CheckResult]: ...
