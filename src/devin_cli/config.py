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

    def _save(self):
        with open(self._config_file, "w") as f:
            json.dump(self._data, f, indent=2)

    @property
    def api_token(self) -> Optional[str]:
        # Env var takes precedence
        return os.environ.get("DEVIN_API_TOKEN") or self._data.get("api_token")

    @api_token.setter
    def api_token(self, value: str):
        self._data["api_token"] = value
        self._save()

    @property
    def base_url(self) -> str:
        return os.environ.get("DEVIN_BASE_URL") or self._data.get("base_url", "https://api.devin.ai/v1")

    @base_url.setter
    def base_url(self, value: str):
        self._data["base_url"] = value
        self._save()

    @property
    def current_session_id(self) -> Optional[str]:
        return self._data.get("current_session_id")

    @current_session_id.setter
    def current_session_id(self, value: str):
        self._data["current_session_id"] = value
        self._save()

config = Config()
