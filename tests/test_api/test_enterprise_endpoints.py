import pytest
import respx
from httpx import Response
from devin_cli.api import ip_access_list, guardrail_violations, code_scans, queue, audit_logs, tags, blueprints, service_users
from devin_cli.config import config

@pytest.fixture(autouse=True)
def setup_config():
    config.base_url = "https://api.devin.ai/v3"
    config.api_token = "test_token"
    config.org_id = "test_org"

@respx.mock
def test_ip_access_list():
    respx.get("https://api.devin.ai/v3/enterprise/ip-access-list").mock(
        return_value=Response(200, json={"ip_ranges": ["1.1.1.1/32"]})
    )
    resp = ip_access_list.get_ip_access_list()
    assert resp["ip_ranges"] == ["1.1.1.1/32"]

@respx.mock
def test_guardrail_violations():
    respx.get("https://api.devin.ai/v3beta1/enterprise/guardrail-violations").mock(
        return_value=Response(200, json={"items": []})
    )
    resp = guardrail_violations.list_guardrail_violations()
    assert "items" in resp

@respx.mock
def test_code_scans():
    respx.get("https://api.devin.ai/v3beta1/enterprise/code-scans/findings").mock(
        return_value=Response(200, json={"findings": []})
    )
    resp = code_scans.list_code_scan_findings()
    assert "findings" in resp

@respx.mock
def test_queue_status():
    respx.get("https://api.devin.ai/v3/enterprise/queue").mock(
        return_value=Response(200, json={"queued_count": 0, "status": "normal"})
    )
    resp = queue.get_queue_status()
    assert resp["status"] == "normal"

@respx.mock
def test_audit_logs():
    respx.get("https://api.devin.ai/v3/enterprise/audit-logs").mock(
        return_value=Response(200, json={"items": []})
    )
    resp = audit_logs.list_audit_logs()
    assert "items" in resp

@respx.mock
def test_org_tags():
    respx.get("https://api.devin.ai/v3/organizations/test_org/tags").mock(
        return_value=Response(200, json={"tags": ["tag1", "tag2"]})
    )
    resp = tags.get_org_tags()
    assert resp["tags"] == ["tag1", "tag2"]

@respx.mock
def test_blueprints():
    respx.get("https://api.devin.ai/v3/organizations/test_org/blueprints").mock(
        return_value=Response(200, json={"blueprints": []})
    )
    resp = blueprints.list_blueprints()
    assert "blueprints" in resp
