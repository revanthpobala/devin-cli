import os
import json
import pytest
from pathlib import Path
from devin_cli.config import Config, APIError


def test_config_defaults(tmp_path, monkeypatch):
    monkeypatch.delenv("DEVIN_API_TOKEN", raising=False)
    monkeypatch.delenv("DEVIN_ORG_ID", raising=False)
    monkeypatch.delenv("DEVIN_BASE_URL", raising=False)
    monkeypatch.delenv("DEVIN_API_VERSION", raising=False)
    monkeypatch.delenv("DEVIN_CONFIG_FILE", raising=False)

    config = Config(config_dir=tmp_path)

    assert config.api_token is None
    assert config.org_id is None
    assert config.current_session_id is None
    assert config.base_url == "https://api.devin.ai/v3"
    assert config.api_version == "v3"


def test_deferred_file_creation(tmp_path, monkeypatch):
    monkeypatch.delenv("DEVIN_CONFIG_FILE", raising=False)
    non_existent_dir = tmp_path / "subdir" / "nested"
    assert not non_existent_dir.exists()

    config = Config(config_dir=non_existent_dir)
    # Reading config or initializing must NOT create the file or directory on disk
    assert not non_existent_dir.exists()
    assert not config.config_file.exists()

    # Once a value is saved, the directory and file are created
    config.api_token = "apk_persisted"
    assert non_existent_dir.exists()
    assert config.config_file.exists()
    with open(config.config_file) as f:
        data = json.load(f)
    assert data["profiles"]["default"]["api_token"] == "apk_persisted"


def test_config_save_load(tmp_path):
    config = Config(config_dir=tmp_path)
    config.api_token = "apk_user_test"
    config.current_session_id = "sess_123"

    # Reload
    config2 = Config(config_dir=tmp_path)
    assert config2.api_token == "apk_user_test"
    assert config2.current_session_id == "sess_123"


def test_cli_flag_beats_env_beats_file(tmp_path, monkeypatch):
    monkeypatch.delenv("DEVIN_CONFIG_FILE", raising=False)
    config = Config(config_dir=tmp_path)

    # 1. Base level: config file
    config.api_token = "token_from_file"
    assert config.api_token == "token_from_file"

    # 2. Env var beats file
    monkeypatch.setenv("DEVIN_API_TOKEN", "token_from_env")
    assert config.api_token == "token_from_env"

    # 3. CLI flag (runtime override) beats env var
    config.runtime.api_token = "token_from_cli_flag"
    assert config.api_token == "token_from_cli_flag"

    # Resetting runtime drops back to env
    config.reset_runtime()
    assert config.api_token == "token_from_env"

    # Removing env drops back to file
    monkeypatch.delenv("DEVIN_API_TOKEN")
    assert config.api_token == "token_from_file"


def test_org_id_precedence(tmp_path, monkeypatch):
    monkeypatch.delenv("DEVIN_CONFIG_FILE", raising=False)
    config = Config(config_dir=tmp_path)

    # File level
    config.org_id = "org_from_file"
    assert config.org_id == "org_from_file"

    # Env var level
    monkeypatch.setenv("DEVIN_ORG_ID", "org_from_env")
    assert config.org_id == "org_from_env"

    # Subcommand temporary_org_id
    config.temporary_org_id = "org_from_subcommand"
    assert config.org_id == "org_from_subcommand"

    # Global runtime override beats all
    config.runtime.org_id = "org_from_flag"
    assert config.org_id == "org_from_flag"


def test_base_url_and_version_precedence(tmp_path, monkeypatch):
    monkeypatch.delenv("DEVIN_CONFIG_FILE", raising=False)
    monkeypatch.delenv("DEVIN_BASE_URL", raising=False)
    monkeypatch.delenv("DEVIN_API_VERSION", raising=False)
    config = Config(config_dir=tmp_path)

    # Defaults
    assert config.base_url == "https://api.devin.ai/v3"
    assert config.api_version == "v3"

    # File overrides
    config.base_url = "https://file.devin.ai/v3"
    config.api_version = "v1"
    assert config.base_url == "https://file.devin.ai/v3"
    assert config.api_version == "v1"

    # Env overrides
    monkeypatch.setenv("DEVIN_BASE_URL", "https://env.devin.ai/v3")
    monkeypatch.setenv("DEVIN_API_VERSION", "v3")
    assert config.base_url == "https://env.devin.ai/v3"
    assert config.api_version == "v3"

    # CLI flag overrides
    config.runtime.base_url = "https://flag.devin.ai/v3"
    config.runtime.api_version = "v1"
    assert config.base_url == "https://flag.devin.ai/v3"
    assert config.api_version == "v1"


def test_devin_config_file_env(tmp_path, monkeypatch):
    custom_file = tmp_path / "custom_config.json"
    custom_file.write_text(json.dumps({
        "profiles": {
            "default": {
                "api_token": "apk_custom_file",
                "org_id": "org_custom_file"
            }
        }
    }))
    monkeypatch.setenv("DEVIN_CONFIG_FILE", str(custom_file))
    monkeypatch.delenv("DEVIN_API_TOKEN", raising=False)
    monkeypatch.delenv("DEVIN_ORG_ID", raising=False)

    config = Config()
    assert config.config_file == custom_file.resolve()
    assert config.api_token == "apk_custom_file"
    assert config.org_id == "org_custom_file"


def test_validate_for_api(tmp_path, monkeypatch):
    monkeypatch.delenv("DEVIN_API_TOKEN", raising=False)
    monkeypatch.delenv("DEVIN_ORG_ID", raising=False)
    config = Config(config_dir=tmp_path)

    with pytest.raises(APIError) as exc_token:
        config.validate_for_api()
    assert "Devin API token is required" in str(exc_token.value)

    config.runtime.api_token = "apk_token"
    # Should not raise when require_org is False
    config.validate_for_api(require_org=False)

    with pytest.raises(APIError) as exc_org:
        config.validate_for_api(require_org=True)
    config.runtime.org_id = "org_123"
    config.validate_for_api(require_org=True)


def test_whitespace_stripping(tmp_path, monkeypatch):
    monkeypatch.delenv("DEVIN_CONFIG_FILE", raising=False)
    config = Config(config_dir=tmp_path)

    # Token with trailing newline/spaces
    monkeypatch.setenv("DEVIN_API_TOKEN", "  apk_padded_token \n")
    monkeypatch.setenv("DEVIN_ORG_ID", "  org-padded-id \t")
    assert config.api_token == "apk_padded_token"
    assert config.org_id == "org-padded-id"

    # Runtime flag with trailing whitespace
    config.runtime.api_token = " cog_whitespace_token\n "
    config.runtime.org_id = " org-whitespace-id \n"
    assert config.api_token == "cog_whitespace_token"
    assert config.org_id == "org-whitespace-id"


def test_version_and_url_normalization(tmp_path, monkeypatch):
    monkeypatch.delenv("DEVIN_CONFIG_FILE", raising=False)
    config = Config(config_dir=tmp_path)

    config.runtime.api_version = "V1"
    assert config.api_version == "v1"

    config.runtime.base_url = "https://api.devin.ai/v3/"
    assert config.base_url == "https://api.devin.ai/v3"

