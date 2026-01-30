from typer.testing import CliRunner
from unittest.mock import patch
from devin_cli.cli import app

runner = CliRunner()

def test_app_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Unofficial CLI for Devin AI" in result.stdout

def test_app_configure_help():
    result = runner.invoke(app, ["configure", "--help"])
    assert result.exit_code == 0
    assert "Configure the CLI" in result.stdout
    assert "Devin API Base URL" in result.stdout

def test_cli_handles_api_error():
    # Mock create_session to raise an exception
    with patch("devin_cli.api.sessions.create_session") as mock_create:
        mock_create.side_effect = Exception("API BOOM")
        # create-session requires prompt argument
        result = runner.invoke(app, ["create-session", "test prompt"])
        print(result.stdout)
        assert result.exit_code == 1
        assert "Unexpected Error" in result.stdout
        assert "API BOOM" in result.stdout

