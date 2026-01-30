import os
import json
from pathlib import Path
from devin_cli.config import Config

def test_config_defaults(tmp_path):
    # Mock config dir and clear env
    if "DEVIN_API_TOKEN" in os.environ:
        del os.environ["DEVIN_API_TOKEN"]
    if "DEVIN_BASE_URL" in os.environ:
        del os.environ["DEVIN_BASE_URL"]
        
    config = Config(config_dir=tmp_path)
    
    assert config.api_token is None
    assert config.current_session_id is None
    assert config.base_url == "https://api.devin.ai/v1"

def test_config_save_load(tmp_path):
    config = Config(config_dir=tmp_path)
    config.api_token = "apk_user_test"
    config.current_session_id = "sess_123"
    
    # Reload
    config2 = Config(config_dir=tmp_path)
    assert config2.api_token == "apk_user_test"
    assert config2.current_session_id == "sess_123"
