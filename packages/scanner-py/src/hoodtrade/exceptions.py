"""Hood Trade exception hierarchy."""

from __future__ import annotations


class HoodTradeError(Exception):
    """Base exception for all Hood Trade errors."""


class ConfigError(HoodTradeError):
    """Invalid configuration."""


class RpcConnectionError(HoodTradeError):
    """Cannot reach the JSON-RPC endpoint."""


class ChainMismatchError(HoodTradeError):
    """RPC reports a different chain id than expected."""


class ScanError(HoodTradeError):
    """Error during scan execution."""


class ExportError(HoodTradeError):
    """Error exporting a report."""
