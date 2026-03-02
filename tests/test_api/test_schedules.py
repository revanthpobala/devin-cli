import pytest
import respx
from httpx import Response
from devin_cli.api import schedules
from devin_cli.config import config

@pytest.fixture(autouse=True)
def setup_config():
    config.base_url = "https://api.devin.ai/v3"
    config.api_token = "test_token"
    config.org_id = "test_org"

@respx.mock
def test_list_schedules():
    respx.get("https://api.devin.ai/v3/organizations/test_org/schedules").mock(
        return_value=Response(200, json={"items": []})
    )
    schedules.list_schedules()

@respx.mock
def test_create_schedule():
    route = respx.post("https://api.devin.ai/v3/organizations/test_org/schedules").mock(
        return_value=Response(200, json={"id": "sch_123"})
    )
    schedules.create_schedule("test prompt", "0 0 * * *")
    assert route.called
    import json
    body = json.loads(route.calls.last.request.read())
    assert body["prompt"] == "test prompt"
    assert body["cron"] == "0 0 * * *"

@respx.mock
def test_delete_schedule():
    route = respx.delete("https://api.devin.ai/v3/organizations/test_org/schedules/sch_123").mock(
        return_value=Response(204)
    )
    schedules.delete_schedule("sch_123")
    assert route.called
