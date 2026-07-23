import pytest

from hoodtrade.exceptions import (
    ChainMismatchError,
    ConfigError,
    ExportError,
    HoodTradeError,
    RpcConnectionError,
    ScanError,
)


def test_hierarchy():
    assert issubclass(ConfigError, HoodTradeError)
    assert issubclass(RpcConnectionError, HoodTradeError)
    assert issubclass(ChainMismatchError, HoodTradeError)
    assert issubclass(ScanError, HoodTradeError)
    assert issubclass(ExportError, HoodTradeError)


def test_raise_config_error():
    with pytest.raises(ConfigError):
        raise ConfigError("bad config")


def test_base_catches_all():
    with pytest.raises(HoodTradeError):
        raise RpcConnectionError("no connection")
