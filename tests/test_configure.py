import json
import pytest
from typer.testing import CliRunner
from devin_cli.cli import app
from devin_cli.config import Config

runner = CliRunner()


def test_configure_non_interactive_yes(tmp_path, monkeypatch):
    custom_cfg = tmp_path / "devin_test.json"
    monkeypatch.setenv("DEVIN_CONFIG_FILE", str(custom_cfg))

    result = runner.invoke(app, [
        "configure",
        "--token", "apk_test_secret_123",
        "--org", "org-test-456",
        "--base-url", "https://api.devin.ai/v3",
        "--api-version", "v3",
        "--yes"
    ])

    assert result.exit_code == 0
    assert "Configuration saved to" in result.stdout

    # Verify written content
    assert custom_cfg.exists()
    data = json.loads(custom_cfg.read_text())
    profile = data["profiles"]["default"]
    assert profile["api_token"] == "apk_test_secret_123"
    assert profile["org_id"] == "org-test-456"
    assert profile["base_url"] == "https://api.devin.ai/v3"
    assert profile["api_version"] == "v3"


def test_configure_non_interactive_missing_token(tmp_path, monkeypatch):
    custom_cfg = tmp_path / "devin_test.json"
    monkeypatch.setenv("DEVIN_CONFIG_FILE", str(custom_cfg))
    monkeypatch.delenv("DEVIN_API_TOKEN", raising=False)

    # In CliRunner, stdin is not a tty by default, or with --yes
    result = runner.invoke(app, ["configure", "--yes"])
    assert result.exit_code == 1
    assert "API token is required" in result.stdout
    assert not custom_cfg.exists()


def test_configure_non_interactive_defaults(tmp_path, monkeypatch):
    custom_cfg = tmp_path / "devin_test.json"
    monkeypatch.setenv("DEVIN_CONFIG_FILE", str(custom_cfg))

    result = runner.invoke(app, [
        "configure",
        "--token", "apk_test_default",
        "--yes"
    ])

    assert result.exit_code == 0
    data = json.loads(custom_cfg.read_text())
    profile = data["profiles"]["default"]
    assert profile["api_token"] == "apk_test_default"
    assert profile["base_url"] == "https://api.devin.ai/v3"
    assert profile["api_version"] == "v3"


def test_configure_non_interactive_v1_mode(tmp_path, monkeypatch):
    custom_cfg = tmp_path / "devin_test.json"
    monkeypatch.setenv("DEVIN_CONFIG_FILE", str(custom_cfg))

    result = runner.invoke(app, [
        "configure",
        "--token", "apk_legacy",
        "--api-version", "v1",
        "--yes"
    ])

    assert result.exit_code == 0
    data = json.loads(custom_cfg.read_text())
    profile = data["profiles"]["default"]
    assert profile["api_token"] == "apk_legacy"
    assert profile["api_version"] == "v1"
    assert "v1" in profile["base_url"]


def test_configure_custom_profile(tmp_path, monkeypatch):
    custom_cfg = tmp_path / "devin_test.json"
    monkeypatch.setenv("DEVIN_CONFIG_FILE", str(custom_cfg))

    result = runner.invoke(app, [
        "configure",
        "--token", "cog_service_token",
        "--org", "org-enterprise",
        "--profile", "ci-runner",
        "--yes"
    ])

    assert result.exit_code == 0
    data = json.loads(custom_cfg.read_text())
    assert "ci-runner" in data["profiles"]
    profile = data["profiles"]["ci-runner"]
    assert profile["api_token"] == "cog_service_token"
    assert profile["org_id"] == "org-enterprise"


def test_configure_non_interactive_when_token_provided_without_yes(tmp_path, monkeypatch):
    custom_cfg = tmp_path / "devin_test.json"
    monkeypatch.setenv("DEVIN_CONFIG_FILE", str(custom_cfg))
    monkeypatch.delenv("DEVIN_API_TOKEN", raising=False)
    monkeypatch.delenv("DEVIN_ORG_ID", raising=False)

    # Calling configure with --token and --org should NOT prompt even without --yes
    result = runner.invoke(app, [
        "configure",
        "--token", "apk_auto_token_999",
        "--org", "org-auto-ci-999",
    ])

    assert result.exit_code == 0
    assert "Configuration saved to" in result.stdout
    data = json.loads(custom_cfg.read_text())
    profile = data["profiles"]["default"]
    assert profile["api_token"] == "apk_auto_token_999"
    assert profile["org_id"] == "org-auto-ci-999"
    assert profile["api_version"] == "v3"
    assert profile["base_url"] == "https://api.devin.ai/v3"


def test_configure_global_flags_before_subcommand_without_yes(tmp_path, monkeypatch):
    custom_cfg = tmp_path / "devin_test.json"
    monkeypatch.setenv("DEVIN_CONFIG_FILE", str(custom_cfg))
    monkeypatch.delenv("DEVIN_API_TOKEN", raising=False)
    monkeypatch.delenv("DEVIN_ORG_ID", raising=False)

    # Calling devin --token ... --org ... configure should NOT prompt
    result = runner.invoke(app, [
        "--token", "apk_global_token_777",
        "--org", "org-global-ci-777",
        "configure",
    ])

    assert result.exit_code == 0
    assert "Configuration saved to" in result.stdout
    data = json.loads(custom_cfg.read_text())
    profile = data["profiles"]["default"]
    assert profile["api_token"] == "apk_global_token_777"
    assert profile["org_id"] == "org-global-ci-777"


def test_configure_ci_environment_uses_env_token(tmp_path, monkeypatch):
    custom_cfg = tmp_path / "devin_test.json"
    monkeypatch.setenv("DEVIN_CONFIG_FILE", str(custom_cfg))
    monkeypatch.setenv("CI", "true")
    monkeypatch.setenv("DEVIN_API_TOKEN", "apk_ci_env_token")
    monkeypatch.setenv("DEVIN_ORG_ID", "org-ci-env")

    result = runner.invoke(app, ["configure"])
    assert result.exit_code == 0
    data = json.loads(custom_cfg.read_text())
    profile = data["profiles"]["default"]
    assert profile["api_token"] == "apk_ci_env_token"
    assert profile["org_id"] == "org-ci-env"

