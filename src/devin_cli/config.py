import json
import os
import contextvars
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union

CONFIG_DIR = Path.home() / ".config" / "devin"
CONFIG_FILE = CONFIG_DIR / "config.json"


class APIError(Exception):
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


@dataclass
class RuntimeCredentials:
    api_token: Optional[str] = None
    org_id: Optional[str] = None
    base_url: Optional[str] = None
    api_version: Optional[str] = None
    config_file: Optional[Path] = None


_runtime_cv: contextvars.ContextVar[Optional[RuntimeCredentials]] = contextvars.ContextVar(
    "_runtime_credentials", default=None
)


class Config:
    def __init__(self, config_dir: Optional[Path] = None, config_file: Optional[Union[str, Path]] = None):
        self._initial_config_file: Optional[Path] = (
            Path(config_file).expanduser().resolve() if config_file else None
        )
        self._initial_config_dir: Optional[Path] = (
            Path(config_dir).expanduser().resolve() if config_dir else None
        )
        self._custom_config_file: Optional[Path] = self._initial_config_file
        self._custom_config_dir: Optional[Path] = self._initial_config_dir
        self._runtime: RuntimeCredentials = RuntimeCredentials()
        self.reset_runtime()
        self._data = {}
        self._loaded_file: Optional[Path] = None
        self._load()

    @property
    def runtime(self) -> RuntimeCredentials:
        rt = _runtime_cv.get()
        if rt is not None:
            return rt
        return self._runtime

    def reset_runtime(self):
        self._runtime = RuntimeCredentials()
        _runtime_cv.set(self._runtime)
        self._temporary_org_id = None
        self._runtime_profile = None
        self._custom_config_file = getattr(self, "_initial_config_file", None)
        self._custom_config_dir = getattr(self, "_initial_config_dir", None)

    def set_config_file(self, config_file: Union[str, Path]):
        self._custom_config_file = Path(config_file).expanduser().resolve()
        self._load()

    def reload(self):
        """Force re-reading configuration data from disk."""
        self._load()

    @property
    def config_file(self) -> Path:
        if self._custom_config_file:
            return self._custom_config_file
        if self.runtime.config_file:
            return self.runtime.config_file
        if os.environ.get("DEVIN_CONFIG_FILE"):
            return Path(os.environ["DEVIN_CONFIG_FILE"]).expanduser().resolve()
        if self._custom_config_dir:
            return (self._custom_config_dir / "config.json").resolve()
        return (Path.home() / ".config" / "devin" / "config.json").resolve()

    @property
    def config_dir(self) -> Path:
        return self.config_file.parent

    def _ensure_config_exists(self):
        """Creates directory and empty file only upon writing."""
        target_dir = self.config_dir
        if not target_dir.exists():
            target_dir.mkdir(parents=True, mode=0o700)

    def _load(self):
        target_file = self.config_file
        self._loaded_file = target_file
        if not target_file.exists():
            self._data = {}
            return

        try:
            with open(target_file, "r") as f:
                self._data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            self._data = {}
            return
            
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
            if target_file.exists():
                self._save()

    def _save(self):
        self._ensure_config_exists()
        target_file = self.config_file
        with open(target_file, "w") as f:
            json.dump(self._data, f, indent=2)
        try:
            target_file.chmod(0o600)
        except OSError:
            pass

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
        if self._loaded_file != self.config_file:
            self._load()
        return self._data.get("profiles", {}).get(self.active_profile, {})

    def _set_profile_data(self, key: str, value: str):
        if self._loaded_file != self.config_file:
            self._load()
        profile_name = self.active_profile
        if "profiles" not in self._data:
            self._data["profiles"] = {}
        if profile_name not in self._data["profiles"]:
            self._data["profiles"][profile_name] = {}
        self._data["profiles"][profile_name][key] = value
        self._save()

    @property
    def api_token(self) -> Optional[str]:
        # Precedence: CLI flag (runtime) -> Env var -> Config file profile
        val = (
            self.runtime.api_token
            or self._runtime.api_token
            or os.environ.get("DEVIN_API_TOKEN")
            or self._get_profile_data().get("api_token")
        )
        return val.strip() if isinstance(val, str) else val

    @api_token.setter
    def api_token(self, value: str):
        self._set_profile_data("api_token", value)

    @property
    def org_id(self) -> Optional[str]:
        # Precedence: CLI flag (runtime) -> temporary_org_id -> Env var -> Config file profile
        val = (
            self.runtime.org_id
            or getattr(self, "_temporary_org_id", None)
            or self._runtime.org_id
            or os.environ.get("DEVIN_ORG_ID")
            or self._get_profile_data().get("org_id")
        )
        return val.strip() if isinstance(val, str) else val

    @org_id.setter
    def org_id(self, value: str):
        self._set_profile_data("org_id", value)

    @property
    def temporary_org_id(self) -> Optional[str]:
        return self.runtime.org_id or getattr(self, "_temporary_org_id", None) or self._runtime.org_id

    @temporary_org_id.setter
    def temporary_org_id(self, value: Optional[str]):
        self._temporary_org_id = value
        self.runtime.org_id = value
        self._runtime.org_id = value

    @property
    def base_url(self) -> str:
        # Precedence: CLI flag (runtime) -> Env var -> Config file profile -> Default
        val = (
            self.runtime.base_url
            or self._runtime.base_url
            or os.environ.get("DEVIN_BASE_URL")
            or self._get_profile_data().get("base_url", "https://api.devin.ai/v3")
        )
        return val.rstrip("/") if isinstance(val, str) else "https://api.devin.ai/v3"

    @base_url.setter
    def base_url(self, value: str):
        self._set_profile_data("base_url", value)

    @property
    def api_version(self) -> str:
        # Precedence: CLI flag (runtime) -> Env var -> Config file profile -> Default
        val = (
            self.runtime.api_version
            or self._runtime.api_version
            or os.environ.get("DEVIN_API_VERSION")
            or self._get_profile_data().get("api_version", "v3")
        )
        return val.lower() if isinstance(val, str) else "v3"

    @api_version.setter
    def api_version(self, value: str):
        self._set_profile_data("api_version", value)

    @property
    def current_session_id(self) -> Optional[str]:
        return self._get_profile_data().get("current_session_id")

    @current_session_id.setter
    def current_session_id(self, value: str):
        self._set_profile_data("current_session_id", value)

    def validate_for_api(self, require_org: bool = False):
        """Validate API credentials before dispatching network requests."""
        if not self.api_token:
            raise APIError("Devin API token is required. Provide it via --token, DEVIN_API_TOKEN, or run 'devin configure'.")
        if require_org and not self.org_id:
            raise APIError("Devin Organization ID is required for this operation. Provide it via --org, DEVIN_ORG_ID, or run 'devin configure'.")

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
