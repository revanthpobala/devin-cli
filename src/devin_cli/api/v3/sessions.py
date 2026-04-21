from typing import List, Optional
from devin_cli.api.client import client

def list_sessions(limit: int = 100, after: Optional[str] = None):
    params = {"limit": limit}
    if after:
        params["after"] = after
    return client.get("sessions", params=params)

def create_session(
    prompt: str,
    advanced_mode: Optional[str] = None,
    attachment_urls: Optional[List[str]] = None,
    bypass_approval: bool = False,
    knowledge_ids: Optional[List[str]] = None,
    max_acu_limit: Optional[int] = None,
    playbook_id: Optional[str] = None,
    child_playbook_id: Optional[str] = None,
    repos: Optional[List[str]] = None,
    secret_ids: Optional[List[str]] = None,
    session_links: Optional[List[str]] = None,
    session_secrets: Optional[List[dict]] = None,
    tags: Optional[List[str]] = None,
    title: Optional[str] = None,
    create_as_user_id: Optional[str] = None,
    structured_output_schema: Optional[str] = None,
):
    data = {
        "prompt": prompt,
    }
    if bypass_approval:
        data["bypass_approval"] = bypass_approval
    if advanced_mode:
        data["advanced_mode"] = advanced_mode
    if attachment_urls:
        data["attachment_urls"] = attachment_urls
    if knowledge_ids:
        data["knowledge_ids"] = knowledge_ids
    if max_acu_limit:
        data["max_acu_limit"] = max_acu_limit
    if playbook_id:
        data["playbook_id"] = playbook_id
    if child_playbook_id:
        data["child_playbook_id"] = child_playbook_id
    if repos:
        data["repos"] = repos
    if secret_ids:
        data["secret_ids"] = secret_ids
    if session_links:
        data["session_links"] = session_links
    if session_secrets:
        data["session_secrets"] = session_secrets
    if tags:
        data["tags"] = tags
    if title:
        data["title"] = title
    if create_as_user_id:
        data["create_as_user_id"] = create_as_user_id
    if structured_output_schema:
        data["structured_output_schema"] = structured_output_schema

    return client.post("sessions", json=data)

def get_session(session_id: str):
    from devin_cli.api.client import APIError
    try:
        return client.get(f"sessions/{session_id}")
    except APIError as e:
        if e.status_code in (403, 404):
            # Fallback to list endpoint with session_ids filter (especially for cog_ tokens)
            res = client.get("sessions", params={"session_ids": [session_id]})
            items = res.get("items", [])
            if items:
                return items[0]
            raise
        raise

def get_session_messages(session_id: str):
    return client.get(f"sessions/{session_id}/messages")

def send_message(session_id: str, message: str):
    return client.post(f"sessions/{session_id}/messages", json={"message": message})

def get_session_attachments(session_id: str):
    return client.get(f"sessions/{session_id}/attachments")

def get_session_tags(session_id: str):
    return client.get(f"sessions/{session_id}/tags")

def update_session_tags(session_id: str, tags: List[str]):
    return client.put(f"sessions/{session_id}/tags", json={"tags": tags})

def append_session_tags(session_id: str, tags: List[str]):
    return client.post(f"sessions/{session_id}/tags", json={"tags": tags})

def terminate_session(session_id: str):
    return client.post(f"sessions/{session_id}/terminate", timeout=5.0)

def archive_session(session_id: str):
    return client.post(f"sessions/{session_id}/archive")

def list_sessions_with_insights(limit: int = 100, after: Optional[str] = None):
    params = {"limit": limit}
    if after:
        params["after"] = after
    return client.get("sessions/insights", params=params)

def get_session_insights(session_id: str):
    return client.get(f"sessions/{session_id}/insights")
