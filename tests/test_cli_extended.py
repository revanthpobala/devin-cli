import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock
from devin_cli.cli import app
from devin_cli.api.client import APIError

runner = CliRunner()

@patch("devin_cli.api.repositories.list_repositories")
def test_repos_list_pagination(mock_list):
    # First call returns a page with has_next_page=True and end_cursor
    # Second call returns a page with has_next_page=False
    mock_list.side_effect = [
        {
            "repositories": [{"repo_path": "owner/repo1"}],
            "has_next_page": True,
            "end_cursor": "cursor123"
        },
        {
            "repositories": [{"repo_path": "owner/repo2"}],
            "has_next_page": False,
            "end_cursor": None
        }
    ]
    
    result = runner.invoke(app, ["repos", "list", "--all"])
    assert result.exit_code == 0
    assert "owner/repo1" in result.stdout
    assert "owner/repo2" in result.stdout
    assert mock_list.call_count == 2


@patch("devin_cli.api.repositories.get_indexing_status")
def test_repos_status_enabled(mock_status):
    mock_status.return_value = {
        "repo_path": "owner/repo",
        "indexing_enabled": True,
        "latest_index": {"status": "completed"}
    }
    
    result = runner.invoke(app, ["repos", "status", "owner/repo"])
    assert result.exit_code == 0
    assert "indexing_enabled" in result.stdout


@patch("devin_cli.api.repositories.get_indexing_status")
def test_repos_status_disabled(mock_status):
    mock_status.return_value = {
        "repo_path": "owner/repo",
        "indexing_enabled": False
    }
    
    result = runner.invoke(app, ["repos", "status", "owner/repo"])
    assert result.exit_code == 1


@patch("devin_cli.api.repositories.get_indexing_status")
def test_repos_status_not_registered(mock_status):
    # Raise a 404 APIError
    mock_status.side_effect = APIError("Not found", 404)
    
    result = runner.invoke(app, ["repos", "status", "owner/repo"])
    assert result.exit_code == 2
    assert "Not registered in Devin" in result.stdout


@patch("devin_cli.api.repositories.get_indexing_status")
def test_repos_status_multi(mock_status):
    mock_status.side_effect = [
        {"repo_path": "owner/repo1", "indexing_enabled": True},
        APIError("Not found", 404),
    ]
    
    result = runner.invoke(app, ["repos", "status", "owner/repo1", "owner/repo2"])
    assert result.exit_code == 0 # Multi-path doesn't fail exit code on 404
    assert "Repository Indexing Status" in result.stdout
    assert "owner/repo1" in result.stdout
    assert "owner/repo2" in result.stdout


@patch("devin_cli.api.sessions.get_session")
def test_sessions_get_terminal_state(mock_get):
    mock_get.return_value = {
        "session_id": "sess_123",
        "status_enum": "finished",
        "title": "Test"
    }
    
    result = runner.invoke(app, ["sessions", "get", "sess_123"])
    assert result.exit_code == 0
    assert '"terminal_state": "completed"' in result.stdout


@patch("devin_cli.api.sessions.get_session")
def test_sessions_wait(mock_get):
    mock_get.side_effect = [
        {"session_id": "sess_123", "status_enum": "running"},
        {"session_id": "sess_123", "status_enum": "finished"}
    ]
    
    result = runner.invoke(app, ["sessions", "wait", "sess_123", "--interval", "0"])
    assert result.exit_code == 0
    assert "completed successfully" in result.stdout
    assert mock_get.call_count == 2


@patch("devin_cli.api.repositories.get_indexing_status")
def test_repos_status_other_error(mock_status):
    # Raise a non-404 APIError (e.g., 403 Forbidden)
    mock_status.side_effect = APIError("Forbidden", 403)
    
    result = runner.invoke(app, ["repos", "status", "owner/repo"])
    assert result.exit_code == 3
    assert "API Error" in result.stdout or "Forbidden" in result.stdout


def test_sessions_wait_negative_timeout():
    result = runner.invoke(app, ["sessions", "wait", "sess_123", "--timeout", "-10s"])
    assert result.exit_code == 1
    assert "cannot be negative" in result.stdout

