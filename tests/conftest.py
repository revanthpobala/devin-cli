import pytest
import os
from devin_cli.config import config

@pytest.fixture(autouse=True)
def clean_config_for_tests():
    config.reset_runtime()
    config._custom_config_file = None
    config._custom_config_dir = None
    os.environ["DEVIN_API_VERSION"] = "v3"
    config.runtime.api_version = "v3"
    yield
    config.reset_runtime()
    config._custom_config_file = None
    config._custom_config_dir = None
