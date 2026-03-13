import pytest
import respx
from httpx import Response
from devin_cli.api import knowledge
from devin_cli.config import config

@pytest.fixture(autouse=True)
def setup_config():
    config.base_url = "https://api.devin.ai/v3"
    config.api_token = "test_token"
    config.org_id = "test_org"

@respx.mock
def test_list_knowledge():
    respx.get("https://api.devin.ai/v3/organizations/test_org/knowledge/notes").mock(
        return_value=Response(200, json={"items": []})
    )
    knowledge.list_knowledge()

@respx.mock
def test_create_knowledge():
    route = respx.post("https://api.devin.ai/v3/organizations/test_org/knowledge/notes").mock(
        return_value=Response(200, json={"id": "k_123"})
    )
    knowledge.create_knowledge(
        title="test",
        body="content",
        trigger="my_trigger"
    )
    assert route.called
    import json
    body = json.loads(route.calls.last.request.read())
    assert body["name"] == "test"
    assert body["trigger"] == "my_trigger"

@respx.mock
def test_update_knowledge():
    route = respx.put("https://api.devin.ai/v3/organizations/test_org/knowledge/notes/k_123").mock(
        return_value=Response(200)
    )
    knowledge.update_knowledge("k_123", title="new", trigger="new_trigger")
    assert route.called

@respx.mock
def test_delete_knowledge():
    route = respx.delete("https://api.devin.ai/v3/organizations/test_org/knowledge/notes/k_123").mock(
        return_value=Response(204)
    )
    knowledge.delete_knowledge("k_123")
    assert route.called
