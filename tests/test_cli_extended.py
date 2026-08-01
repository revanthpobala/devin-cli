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
    print(result.stdout)
    if result.exception:
        print(result.exception)
    assert result.exit_code == 3
    assert "API Error" in result.stdout or "Forbidden" in result.stdout


def test_sessions_wait_negative_timeout():
    result = runner.invoke(app, ["sessions", "wait", "sess_123", "--timeout", "-10s"])
    assert result.exit_code == 1
    assert "cannot be negative" in result.stdout

@patch("devin_cli.cli.sessions.list_sessions")
def test_sessions_list_pagination(mock_list):
    mock_list.side_effect = [
        {
            "items": [{"session_id": "sess_1"}],
            "has_next_page": True,
            "end_cursor": "cur_1"
        },
        {
            "items": [{"session_id": "sess_2"}],
            "has_next_page": False,
            "end_cursor": None
        }
    ]
    
    with patch("devin_cli.cli.config") as mock_config:
        mock_config.api_version = "v3"
        result = runner.invoke(app, ["sessions", "list", "--all"])
        
    assert result.exit_code == 0
    assert "sess_1" in result.stdout
    assert "sess_2" in result.stdout
    assert mock_list.call_count == 2

@patch("devin_cli.cli.sessions.get_session_messages")
def test_sessions_messages_pagination(mock_get_messages):
    mock_get_messages.side_effect = [
        {
            "messages": [{"message": "hello", "role": "user"}],
            "has_next_page": True,
            "end_cursor": "cur_1"
        },
        {
            "messages": [{"message": "world", "role": "assistant"}],
            "has_next_page": False,
            "end_cursor": None
        }
    ]
    
    with patch("devin_cli.cli.config") as mock_config:
        mock_config.api_version = "v3"
        result = runner.invoke(app, ["sessions", "messages", "sess_123", "--all"])
        
    assert result.exit_code == 0
    assert "hello" in result.stdout
    assert "world" in result.stdout
    assert mock_get_messages.call_count == 2

@patch("devin_cli.cli.consumption.get_session_consumption")
@patch("devin_cli.cli.sessions.get_session")
def test_sessions_cost_v3(mock_get_session, mock_consumption):
    mock_get_session.return_value = {
        "session_id": "sess_123",
        "status_enum": "completed",
        "acus_consumed": 15
    }
    mock_consumption.return_value = {"breakdown": "details"}
    
    with patch("devin_cli.cli.config") as mock_config:
        mock_config.api_version = "v3"
        result = runner.invoke(app, ["sessions", "cost", "sess_123"])
        
    assert result.exit_code == 0
    assert "15" in result.stdout
    assert mock_consumption.call_count == 1
    assert "breakdown" in result.stdout

@patch("devin_cli.api.v3.sessions.create_session")
def test_create_session_devin_mode_flag(mock_create):
    mock_create.return_value = {"session_id": "sess_fast", "url": "https://devin.ai/sess_fast"}
    with patch("devin_cli.cli.config") as mock_config:
        mock_config.api_version = "v3"
        mock_config.get_session_by_prompt_hash.return_value = None
        result = runner.invoke(app, ["sessions", "create", "test prompt", "--devin-mode", "fast"])
    assert result.exit_code == 0
    mock_create.assert_called_once()
    assert mock_create.call_args.kwargs.get("devin_mode") == "fast"

@patch("devin_cli.cli.pr_reviews.trigger_pr_review")
def test_pr_review_trigger(mock_trigger):
    mock_trigger.return_value = {"status": "pending", "pr_number": 10}
    with patch("devin_cli.cli.config") as mock_config:
        mock_config.api_version = "v3"
        result = runner.invoke(app, ["pr-reviews", "trigger", "--pr-url", "https://github.com/owner/repo/pull/10"])
    assert result.exit_code == 0
    assert "Devin PR Review Triggered" in result.stdout

@patch("devin_cli.cli.queue.get_queue_status")
def test_enterprise_queue_command(mock_queue):
    mock_queue.return_value = {"status": "normal", "queued_count": 2}
    with patch("devin_cli.cli.config") as mock_config:
        mock_config.api_version = "v3"
        result = runner.invoke(app, ["enterprise", "queue"])
    assert result.exit_code == 0
    assert "Queue Health Status" in result.stdout

@patch("devin_cli.api.v3.sessions.create_session")
def test_create_session_session_secret_flag(mock_create):
    mock_create.return_value = {"session_id": "sess_secret", "url": "https://devin.ai/sess_secret"}
    with patch("devin_cli.cli.config") as mock_config:
        mock_config.api_version = "v3"
        mock_config.get_session_by_prompt_hash.return_value = None
        result = runner.invoke(app, ["sessions", "create", "test prompt", "--session-secret", "MY_KEY=SECRET_VAL"])
    assert result.exit_code == 0
    mock_create.assert_called_once()
    assert mock_create.call_args.kwargs.get("session_secrets") == [{"key": "MY_KEY", "value": "SECRET_VAL", "sensitive": True}]

@patch("devin_cli.cli.pr_reviews.trigger_pr_review")
def test_pr_review_trigger_json(mock_trigger):
    mock_trigger.return_value = {"status": "pending", "pr_number": 10}
    with patch("devin_cli.cli.config") as mock_config:
        mock_config.api_version = "v3"
        result = runner.invoke(app, ["pr-reviews", "trigger", "--pr-url", "https://github.com/owner/repo/pull/10", "--json"])
    assert result.exit_code == 0
    assert '"status": "pending"' in result.stdout

@patch("devin_cli.cli.queue.get_queue_status")
def test_enterprise_queue_command_json(mock_queue):
    mock_queue.return_value = {"status": "normal", "queued_count": 2}
    with patch("devin_cli.cli.config") as mock_config:
        mock_config.api_version = "v3"
        result = runner.invoke(app, ["enterprise", "queue", "--json"])
    assert result.exit_code == 0
    assert '"status": "normal"' in result.stdout


