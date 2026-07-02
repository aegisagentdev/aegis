from typer.testing import CliRunner

from hoodtrade.cli import app

runner = CliRunner()


def test_version_command():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "0.2" in result.output


def test_scan_missing_args():
    result = runner.invoke(app, ["scan"])
    assert result.exit_code != 0


def test_doctor_bad_rpc():
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code != 0
