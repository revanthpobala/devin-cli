import pytest
import os
from devin_cli.config import config

@pytest.fixture(autouse=True)
def ensure_v3_for_tests():
    os.environ["DEVIN_API_VERSION"] = "v3"
    config.api_version = "v3"
