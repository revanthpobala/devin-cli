import pytest
import respx
from httpx import Response
from devin_cli.api import secrets
from devin_cli.config import config

@pytest.fixture(autouse=True)
def setup_config():
    config.base_url = "https://api.devin.ai/v3"
    config.api_token = "test_token"
    config.org_id = "test_org"

@respx.mock
def test_list_secrets():
    respx.get("https://api.devin.ai/v3/organizations/test_org/secrets").mock(
        return_value=Response(200, json={"items": []})
    )
    secrets.list_secrets()

@respx.mock
def test_create_secret():
    route = respx.post("https://api.devin.ai/v3/organizations/test_org/secrets").mock(
        return_value=Response(200)
    )
    secrets.create_secret("name", "value")
    assert route.called

@respx.mock
def test_delete_secret():
    route = respx.delete("https://api.devin.ai/v3/organizations/test_org/secrets/sec_123").mock(
        return_value=Response(204)
    )
    secrets.delete_secret("sec_123")
    assert route.called
