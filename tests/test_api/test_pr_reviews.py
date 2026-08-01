import pytest
import respx
from httpx import Response
from devin_cli.api import pr_reviews
from devin_cli.config import config

@pytest.fixture(autouse=True)
def setup_config():
    config.base_url = "https://api.devin.ai/v3"
    config.api_token = "test_token"
    config.org_id = "test_org"

@respx.mock
def test_trigger_pr_review():
    route = respx.post("https://api.devin.ai/v3/organizations/test_org/pr-reviews").mock(
        return_value=Response(200, json={"status": "pending", "pr_number": 123, "repo_path": "github.com/owner/repo", "commit_sha": "abc", "created_at": "2026-08-01T12:00:00Z"})
    )
    
    resp = pr_reviews.trigger_pr_review("https://github.com/owner/repo/pull/123")
    assert resp["status"] == "pending"
    assert route.called

@respx.mock
def test_get_pr_review_status():
    route = respx.get("https://api.devin.ai/v3/organizations/test_org/pr-reviews").mock(
        return_value=Response(200, json={"status": "completed", "pr_number": 123, "repo_path": "github.com/owner/repo", "commit_sha": "abc", "created_at": "2026-08-01T12:00:00Z"})
    )
    
    resp = pr_reviews.get_pr_review_status(pr_url="https://github.com/owner/repo/pull/123")
    assert resp["status"] == "completed"
    assert route.called
