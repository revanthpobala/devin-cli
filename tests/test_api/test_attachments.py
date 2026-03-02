import pytest
import respx
from httpx import Response
from unittest.mock import patch, mock_open
from devin_cli.api import attachments
from devin_cli.config import config

@respx.mock
def test_upload_file_success(tmp_path):
    # Setup
    config.base_url = "https://api.devin.ai/v3"
    config.api_token = "test_token"
    config.org_id = "test_org"
    
    file_path = tmp_path / "test.txt"
    file_path.write_text("content")
    
    # Mock endpoint
    route = respx.post("https://api.devin.ai/v3/organizations/test_org/attachments").mock(
        return_value=Response(200, json="https://devin.ai/files/123")
    )
    
    # Execute
    url = attachments.upload_file(str(file_path))
    
    # Verify
    assert url == "https://devin.ai/files/123"
    assert route.called
    request = route.calls.last.request
    assert "multipart/form-data" in request.headers["content-type"]

@respx.mock
def test_upload_file_api_error(tmp_path):
    config.base_url = "https://api.devin.ai/v3"
    config.org_id = "test_org"
    file_path = tmp_path / "test.txt"
    file_path.write_text("content")
    
    respx.post("https://api.devin.ai/v3/organizations/test_org/attachments").mock(
        return_value=Response(500, json={"error": "Server boom"})
    )
    
    with pytest.raises(Exception) as exc:
        attachments.upload_file(str(file_path))
    assert "Server error" in str(exc.value)

@respx.mock
def test_download_attachment():
    route = respx.get("https://api.devin.ai/v3/organizations/test_org/attachments/uuid1/file.txt").mock(
        return_value=Response(200, content=b"content", headers={"Content-Type": "application/octet-stream"})
    )
    resp = attachments.download_attachment("uuid1", "file.txt")
    assert resp == b"content"

def test_upload_file_not_found():
    with pytest.raises(FileNotFoundError):
        attachments.upload_file("/nonexistent/file.txt")
