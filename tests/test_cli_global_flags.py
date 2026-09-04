import json
from unittest.mock import patch
from typer.testing import CliRunner
from devin_cli.cli import app
from devin_cli.config import config

runner = CliRunner()


@patch("devin_cli.api.repositories.list_repositories")
def test_global_flags_on_the_fly_without_config_file(mock_list, tmp_path, monkeypatch):
    non_existent_config = tmp_path / "never_created.json"
    monkeypatch.setenv("DEVIN_CONFIG_FILE", str(non_existent_config))
    monkeypatch.delenv("DEVIN_API_TOKEN", raising=False)
    monkeypatch.delenv("DEVIN_ORG_ID", raising=False)

    mock_list.return_value = {
        "repositories": [{"repo_path": "owner/repo"}],
        "has_next_page": False,
        "end_cursor": None,
    }

    result = runner.invoke(app, [
        "--token", "cog_ephemeral_token",
        "--org", "org-ephemeral-123",
        "repos", "list"
    ])

    assert result.exit_code == 0
    assert "owner/repo" in result.stdout
    # Verify disk was never touched
    assert not non_existent_config.exists()
    assert config.api_token == "cog_ephemeral_token"
    assert config.org_id == "org-ephemeral-123"


@patch("devin_cli.api.repositories.list_repositories")
def test_global_flags_json_mode(mock_list, tmp_path, monkeypatch):
    non_existent_config = tmp_path / "no_file.json"
    monkeypatch.setenv("DEVIN_CONFIG_FILE", str(non_existent_config))

    mock_list.return_value = {
        "repositories": [{"repo_path": "my-org/my-service"}],
        "has_next_page": False
    }

    result = runner.invoke(app, [
        "--token", "cog_agent_test",
        "--org", "org-agent",
        "--json",
        "repos", "list"
    ])

    assert result.exit_code == 0
    parsed = json.loads(result.stdout)
    assert parsed["repositories"][0]["repo_path"] == "my-org/my-service"


@patch("devin_cli.api.repositories.list_repositories")
def test_subcommand_org_overrides_global_org(mock_list, tmp_path, monkeypatch):
    monkeypatch.delenv("DEVIN_CONFIG_FILE", raising=False)
    mock_list.return_value = {"repositories": []}

    result = runner.invoke(app, [
        "--token", "cog_test",
        "--org", "org-global-override",
        "repos", "list",
        "--org", "org-subcommand-specific"
    ])

    assert result.exit_code == 0
    assert config.org_id == "org-subcommand-specific"


@patch("devin_cli.api.repositories.list_repositories")
def test_cli_flag_beats_env_in_subcommand(mock_list, tmp_path, monkeypatch):
    mock_list.return_value = {"repositories": []}
    monkeypatch.setenv("DEVIN_API_TOKEN", "token_from_env_var")
    monkeypatch.setenv("DEVIN_ORG_ID", "org_from_env_var")

    result = runner.invoke(app, [
        "--token", "token_from_explicit_flag",
        "--org", "org_from_explicit_flag",
        "repos", "list"
    ])

    assert result.exit_code == 0
    assert config.api_token == "token_from_explicit_flag"
    assert config.org_id == "org_from_explicit_flag"


@patch("devin_cli.api.repositories.list_repositories")
def test_config_file_flag_override(mock_list, tmp_path):
    mock_list.return_value = {"repositories": []}
    custom_file = tmp_path / "ci_settings.json"
    custom_file.write_text(json.dumps({
        "profiles": {
            "default": {
                "api_token": "apk_from_custom_file",
                "org_id": "org_from_custom_file"
            }
        }
    }))

    result = runner.invoke(app, [
        "--config-file", str(custom_file),
        "repos", "list"
    ])

    assert result.exit_code == 0
    assert config.api_token == "apk_from_custom_file"
    assert config.org_id == "org_from_custom_file"
