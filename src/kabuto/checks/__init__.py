"""The default check battery, in execution order.

Order matters only through the shared cache: contract checks populate token metadata
(code size, symbol) that pool / stock-token / execution checks read. Each check is
independent otherwise and safe to run past a failure.
"""

from __future__ import annotations

from .base import Check, Context
from .contract import ContractExistsCheck, OwnershipCheck, SupplySanityCheck
from .execution import ChainIdentityCheck, SequencingContextCheck, SizeVsDepthCheck
from .pool import PoolExistsCheck, PoolLiquidityCheck, PoolPairIntegrityCheck
from .stock_token import StockTokenDisclosureCheck, StockTokenDivergenceCheck


def default_checks() -> list[Check]:
    return [
        ChainIdentityCheck(),
        ContractExistsCheck(),
        OwnershipCheck(),
        SupplySanityCheck(),
        PoolExistsCheck(),
        PoolPairIntegrityCheck(),
        PoolLiquidityCheck(),
        SizeVsDepthCheck(),
        StockTokenDisclosureCheck(),
        StockTokenDivergenceCheck(),
        SequencingContextCheck(),
    ]


__all__ = ["Check", "Context", "default_checks"]
