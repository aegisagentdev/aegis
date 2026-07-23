"""Aegis exception hierarchy."""

from __future__ import annotations


class AegisError(Exception):
    """Base exception for all Aegis errors."""


class ConfigError(AegisError):
    """Invalid configuration."""


class RpcConnectionError(AegisError):
    """Cannot reach the JSON-RPC endpoint."""


class ChainMismatchError(AegisError):
    """RPC reports a different chain id than expected."""


class ScanError(AegisError):
    """Error during scan execution."""


class ExportError(AegisError):
    """Error exporting a report."""
