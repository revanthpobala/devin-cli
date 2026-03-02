import pytest
import respx
from httpx import Response
from devin_cli.api import repositories
from devin_cli.config import config

@pytest.fixture(autouse=True)
def setup_config():
    config.base_url = "https://api.devin.ai/v3"
    config.api_token = "test_token"
    config.org_id = "test_org"

@respx.mock
def test_list_repositories():
    respx.get("https://api.devin.ai/v3beta1/organizations/test_org/repositories").mock(
        return_value=Response(200, json={"items": []})
    )
    repositories.list_repositories()

@respx.mock
def test_index_repository():
    route = respx.put("https://api.devin.ai/v3beta1/organizations/test_org/repositories/owner/repo/indexing").mock(
        return_value=Response(200)
    )
    repositories.index_repository("owner/repo")
    assert route.called

@respx.mock
def test_list_git_connections():
    respx.get("https://api.devin.ai/v3/enterprise/git-providers/connections").mock(
        return_value=Response(200, json={"items": []})
    )
    repositories.list_git_connections()
