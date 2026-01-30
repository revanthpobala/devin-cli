import pytest
import respx
from httpx import Response
from devin_cli.api import sessions
from devin_cli.config import config

@pytest.fixture(autouse=True)
def setup_config():
    config.base_url = "https://api.devin.ai/v1"
    config.api_token = "test_token"

@respx.mock
def test_create_session():
    respx.post("https://api.devin.ai/v1/sessions").mock(
        return_value=Response(200, json={"session_id": "sess_123", "url": "https://preview.devin.ai/sess_123"})
    )
    
    resp = sessions.create_session("test prompt", idempotent=True, unlisted=False)
    assert resp["session_id"] == "sess_123"

@respx.mock
def test_list_sessions():
    respx.get("https://api.devin.ai/v1/sessions").mock(
        return_value=Response(200, json={"sessions": [{"session_id": "sess_1"}]})
    )
    
    resp = sessions.list_sessions(limit=5)
    assert len(resp["sessions"]) == 1
    assert resp["sessions"][0]["session_id"] == "sess_1"

@respx.mock
def test_get_session():
    respx.get("https://api.devin.ai/v1/sessions/sess_123").mock(
        return_value=Response(200, json={"session_id": "sess_123", "status_enum": "working"})
    )
    
    resp = sessions.get_session("sess_123")
    assert resp["status_enum"] == "working"

@respx.mock
def test_send_message():
    route = respx.post("https://api.devin.ai/v1/sessions/sess_123/message").mock(
        return_value=Response(200, json={"status": "ok"})
    )
    
    sessions.send_message("sess_123", "hello")
    assert route.called
    import json
    body = json.loads(route.calls.last.request.read())
    assert body["message"] == "hello"

@respx.mock
def test_terminate_session():
    route = respx.delete("https://api.devin.ai/v1/sessions/sess_123").mock(
        return_value=Response(204)
    )
    
    sessions.terminate_session("sess_123")
    assert route.called
