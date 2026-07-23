import pytest

from aegis.exceptions import (
    ChainMismatchError,
    ConfigError,
    ExportError,
    AegisError,
    RpcConnectionError,
    ScanError,
)


def test_hierarchy():
    assert issubclass(ConfigError, AegisError)
    assert issubclass(RpcConnectionError, AegisError)
    assert issubclass(ChainMismatchError, AegisError)
    assert issubclass(ScanError, AegisError)
    assert issubclass(ExportError, AegisError)


def test_raise_config_error():
    with pytest.raises(ConfigError):
        raise ConfigError("bad config")


def test_base_catches_all():
    with pytest.raises(AegisError):
        raise RpcConnectionError("no connection")
