import json
import os
from pathlib import Path
from typing import Optional

CONFIG_DIR = Path.home() / ".config" / "devin"
CONFIG_FILE = CONFIG_DIR / "config.json"

class Config:
    def __init__(self, config_dir: Path = None):
        self._config_dir = config_dir or CONFIG_DIR
        self._config_file = self._config_dir / "config.json"
        self._ensure_config_exists()
        self._load()

    @property
    def config_file(self) -> Path:
        return self._config_file

    def _ensure_config_exists(self):
        if not self._config_dir.exists():
            self._config_dir.mkdir(parents=True, mode=0o700)
        if not self._config_file.exists():
            with open(self._config_file, "w") as f:
                json.dump({}, f)
            self._config_file.chmod(0o600)

    def _load(self):
        try:
            with open(self._config_file, "r") as f:
                self._data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            self._data = {}
            
        if "profiles" not in self._data:
            # Migrate legacy flat config to default profile
            legacy_keys = ["api_token", "base_url", "org_id", "api_version", "current_session_id"]
            legacy_data = {}
            for key in legacy_keys:
                if key in self._data:
                    legacy_data[key] = self._data.pop(key)
            self._data["profiles"] = {
                "default": legacy_data
            }
            if "active_profile" not in self._data:
                self._data["active_profile"] = "default"
            self._save()


    def _save(self):
        with open(self._config_file, "w") as f:
            json.dump(self._data, f, indent=2)

    @property
    def active_profile(self) -> str:
        return getattr(self, "_runtime_profile", None) or self._data.get("active_profile", "default")
        
    @active_profile.setter
    def active_profile(self, value: str):
        self._runtime_profile = value
        if "profiles" not in self._data:
            self._data["profiles"] = {}
        if value not in self._data["profiles"]:
            self._data["profiles"][value] = {}
            
    def _get_profile_data(self) -> dict:
        return self._data.get("profiles", {}).get(self.active_profile, {})

    def _set_profile_data(self, key: str, value: str):
        profile_name = self.active_profile
        if "profiles" not in self._data:
            self._data["profiles"] = {}
        if profile_name not in self._data["profiles"]:
            self._data["profiles"][profile_name] = {}
        self._data["profiles"][profile_name][key] = value
        self._save()

    @property
    def api_token(self) -> Optional[str]:
        # Env var takes precedence
        return os.environ.get("DEVIN_API_TOKEN") or self._get_profile_data().get("api_token")

    @api_token.setter
    def api_token(self, value: str):
        self._set_profile_data("api_token", value)

    @property
    def org_id(self) -> Optional[str]:
        # Temporary override takes highest precedence (CLI flag)
        # then env var, then config file
        return getattr(self, "_temporary_org_id", None) or os.environ.get("DEVIN_ORG_ID") or self._get_profile_data().get("org_id")

    @org_id.setter
    def org_id(self, value: str):
        self._set_profile_data("org_id", value)

    @property
    def temporary_org_id(self) -> Optional[str]:
        return getattr(self, "_temporary_org_id", None)

    @temporary_org_id.setter
    def temporary_org_id(self, value: Optional[str]):
        self._temporary_org_id = value

    @property
    def base_url(self) -> str:
        return os.environ.get("DEVIN_BASE_URL") or self._get_profile_data().get("base_url", "https://api.devin.ai/v3")

    @base_url.setter
    def base_url(self, value: str):
        self._set_profile_data("base_url", value)

    @property
    def api_version(self) -> str:
        return os.environ.get("DEVIN_API_VERSION") or self._get_profile_data().get("api_version", "v3")

    @api_version.setter
    def api_version(self, value: str):
        self._set_profile_data("api_version", value)

    @property
    def current_session_id(self) -> Optional[str]:
        return self._get_profile_data().get("current_session_id")

    @current_session_id.setter
    def current_session_id(self, value: str):
        self._set_profile_data("current_session_id", value)

    def get_session_by_prompt_hash(self, prompt_hash: str) -> Optional[str]:
        return self._get_profile_data().get("prompt_hashes", {}).get(prompt_hash)

    def save_prompt_hash(self, prompt_hash: str, session_id: str):
        profile_name = self.active_profile
        if "profiles" not in self._data:
            self._data["profiles"] = {}
        if profile_name not in self._data["profiles"]:
            self._data["profiles"][profile_name] = {}
            
        profile_data = self._data["profiles"][profile_name]
        if "prompt_hashes" not in profile_data:
            profile_data["prompt_hashes"] = {}
            
        profile_data["prompt_hashes"][prompt_hash] = session_id
        
        # Keep only the last 50 hashes to prevent config bloat
        if len(profile_data["prompt_hashes"]) > 50:
            keys_to_remove = list(profile_data["prompt_hashes"].keys())[:-50]
            for k in keys_to_remove:
                del profile_data["prompt_hashes"][k]
                
        self._save()

config = Config()
