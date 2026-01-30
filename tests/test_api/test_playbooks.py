import pytest
import respx
from httpx import Response
from devin_cli.api import playbooks
from devin_cli.config import config

@pytest.fixture(autouse=True)
def setup_config():
    config.base_url = "https://api.devin.ai/v1"
    config.api_token = "test_token"

@respx.mock
def test_list_playbooks():
    respx.get("https://api.devin.ai/v1/playbooks").mock(
        return_value=Response(200, json={"playbooks": []})
    )
    playbooks.list_playbooks()

@respx.mock
def test_create_playbook():
    route = respx.post("https://api.devin.ai/v1/playbooks").mock(
        return_value=Response(200, json={"id": "pb_123"})
    )
    playbooks.create_playbook("title", "body", "macro_id")
    assert route.called
    import json
    body = json.loads(route.calls.last.request.read())
    assert body["title"] == "title"
    assert body["macro"] == "macro_id"

@respx.mock
def test_get_playbook():
    respx.get("https://api.devin.ai/v1/playbooks/pb_123").mock(
        return_value=Response(200, json={"id": "pb_123", "title": "test"})
    )
    resp = playbooks.get_playbook("pb_123")
    assert resp["title"] == "test"

@respx.mock
def test_update_playbook():
    route = respx.put("https://api.devin.ai/v1/playbooks/pb_123").mock(
        return_value=Response(200)
    )
    playbooks.update_playbook("pb_123", body="new body")
    assert route.called

@respx.mock
def test_delete_playbook():
    route = respx.delete("https://api.devin.ai/v1/playbooks/pb_123").mock(
        return_value=Response(204)
    )
    playbooks.delete_playbook("pb_123")
    assert route.called
