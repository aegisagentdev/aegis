"""The default check battery, in execution order.

Order matters only through the shared cache: contract checks populate token metadata
(code size, symbol) that pool / stock-token / execution checks read. Each check is
independent otherwise and safe to run past a failure.
"""

from __future__ import annotations

from .base import Check, Context
from .concentration import BurnedSupplyCheck, TokenSelfHoldingCheck
from .contract import ContractExistsCheck, OwnershipCheck, SupplySanityCheck
from .execution import ChainIdentityCheck, SequencingContextCheck, SizeVsDepthCheck
from .honeypot import HoneypotApproveCheck, HoneypotTransferCheck
from .pool import PoolExistsCheck, PoolLiquidityCheck, PoolPairIntegrityCheck
from .reputation import ReputationHoneypotCheck, ReputationPermissionsCheck, ReputationSourceCheck
from .stock_token import StockTokenDisclosureCheck, StockTokenDivergenceCheck


def default_checks() -> list[Check]:
    return [
        ChainIdentityCheck(),
        ContractExistsCheck(),
        OwnershipCheck(),
        SupplySanityCheck(),
        HoneypotTransferCheck(),
        HoneypotApproveCheck(),
        TokenSelfHoldingCheck(),
        BurnedSupplyCheck(),
        ReputationHoneypotCheck(),
        ReputationPermissionsCheck(),
        ReputationSourceCheck(),
        PoolExistsCheck(),
        PoolPairIntegrityCheck(),
        PoolLiquidityCheck(),
        SizeVsDepthCheck(),
        StockTokenDisclosureCheck(),
        StockTokenDivergenceCheck(),
        SequencingContextCheck(),
    ]


__all__ = ["Check", "Context", "default_checks"]
