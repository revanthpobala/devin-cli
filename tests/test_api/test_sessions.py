import pytest
import respx
from httpx import Response
from devin_cli.api import sessions
from devin_cli.config import config

@pytest.fixture(autouse=True)
def setup_config():
    config.base_url = "https://api.devin.ai/v3"
    config.api_token = "test_token"
    config.org_id = "test_org"

@respx.mock
def test_create_session():
    respx.post("https://api.devin.ai/v3/organizations/test_org/sessions").mock(
        return_value=Response(200, json={"session_id": "sess_123", "url": "https://preview.devin.ai/sess_123"})
    )
    
    resp = sessions.create_session("test prompt", bypass_approval=True)
    assert resp["session_id"] == "sess_123"

@respx.mock
def test_list_sessions():
    respx.get("https://api.devin.ai/v3/organizations/test_org/sessions").mock(
        return_value=Response(200, json={"items": [{"session_id": "sess_1"}]})
    )
    
    resp = sessions.list_sessions(limit=5)
    assert len(resp["items"]) == 1
    assert resp["items"][0]["session_id"] == "sess_1"

@respx.mock
def test_get_session():
    respx.get("https://api.devin.ai/v3/organizations/test_org/sessions/sess_123").mock(
        return_value=Response(200, json={"session_id": "sess_123", "status": "working"})
    )
    
    resp = sessions.get_session("sess_123")
    assert resp["status"] == "working"

@respx.mock
def test_send_message():
    route = respx.post("https://api.devin.ai/v3/organizations/test_org/sessions/sess_123/messages").mock(
        return_value=Response(200, json={"status": "ok"})
    )
    
    sessions.send_message("sess_123", "hello")
    assert route.called
    import json
    body = json.loads(route.calls.last.request.read())
    assert body["message"] == "hello"

@respx.mock
def test_terminate_session():
    route = respx.post("https://api.devin.ai/v3/organizations/test_org/sessions/sess_123/terminate").mock(
        return_value=Response(204)
    )
    
    sessions.terminate_session("sess_123")
    assert route.called

@respx.mock
def test_get_session_insights():
    respx.get("https://api.devin.ai/v3/organizations/test_org/sessions/sess_123/insights").mock(
        return_value=Response(200, json={"session_id": "sess_123", "analysis": {}})
    )
    
    resp = sessions.get_session_insights("sess_123")
    assert resp["session_id"] == "sess_123"
