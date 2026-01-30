import pytest
import respx
from httpx import Response
from devin_cli.api import knowledge
from devin_cli.config import config

@pytest.fixture(autouse=True)
def setup_config():
    config.base_url = "https://api.devin.ai/v1"
    config.api_token = "test_token"

@respx.mock
def test_list_knowledge():
    respx.get("https://api.devin.ai/v1/knowledge").mock(
        return_value=Response(200, json={"knowledge": []})
    )
    knowledge.list_knowledge()

@respx.mock
def test_create_knowledge():
    route = respx.post("https://api.devin.ai/v1/knowledge").mock(
        return_value=Response(200, json={"id": "k_123"})
    )
    knowledge.create_knowledge(
        name="test",
        body="content",
        trigger_description="trigger"
    )
    assert route.called
    import json
    body = json.loads(route.calls.last.request.read())
    assert body["name"] == "test"
    assert body["trigger_description"] == "trigger"

@respx.mock
def test_update_knowledge():
    route = respx.put("https://api.devin.ai/v1/knowledge/k_123").mock(
        return_value=Response(200)
    )
    knowledge.update_knowledge("k_123", name="new")
    assert route.called

@respx.mock
def test_delete_knowledge():
    route = respx.delete("https://api.devin.ai/v1/knowledge/k_123").mock(
        return_value=Response(204)
    )
    knowledge.delete_knowledge("k_123")
    assert route.called
