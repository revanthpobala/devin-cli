import pytest
import respx
from httpx import Response
from devin_cli.api import secrets
from devin_cli.config import config

@pytest.fixture(autouse=True)
def setup_config():
    config.base_url = "https://api.devin.ai/v1"
    config.api_token = "test_token"

@respx.mock
def test_list_secrets():
    respx.get("https://api.devin.ai/v1/secrets").mock(
        return_value=Response(200, json={"secrets": []})
    )
    secrets.list_secrets()

@respx.mock
def test_delete_secret():
    route = respx.delete("https://api.devin.ai/v1/secrets/sec_123").mock(
        return_value=Response(204)
    )
    secrets.delete_secret("sec_123")
    assert route.called
