from typing import List, Optional
from devin_cli.api.client import client

def list_sessions(limit: int = 100, offset: int = 0, tags: Optional[List[str]] = None):
    params = {"limit": limit, "offset": offset}
    if tags:
        params["tags"] = tags
    return client.get("sessions", params=params)

def create_session(
    prompt: str,
    idempotent: bool = False,
    snapshot_id: Optional[str] = None,
    playbook_id: Optional[str] = None,
    unlisted: bool = False,
    tags: Optional[List[str]] = None,
    session_secrets: Optional[List[dict]] = None,
    title: Optional[str] = None,
    knowledge_ids: Optional[List[str]] = None,
    secret_ids: Optional[List[str]] = None,
    max_acu_limit: Optional[int] = None,
    advanced_mode: Optional[str] = None,
    repos: Optional[List[str]] = None,
    session_links: Optional[List[str]] = None,
    attachment_urls: Optional[List[str]] = None,
    create_as_user_id: Optional[str] = None,
):
    data = {
        "prompt": prompt,
        "idempotent": idempotent,
        "unlisted": unlisted,
    }
    if snapshot_id:
        data["snapshot_id"] = snapshot_id
    if playbook_id:
        data["playbook_id"] = playbook_id
    if tags:
        data["tags"] = tags
    if session_secrets:
        data["session_secrets"] = session_secrets
    if title:
        data["title"] = title
    if knowledge_ids:
        data["knowledge_ids"] = knowledge_ids
    if secret_ids:
        data["secret_ids"] = secret_ids
    if max_acu_limit:
        data["max_acu_limit"] = max_acu_limit

    return client.post("sessions", json=data)

def get_session(session_id: str):
    return client.get(f"sessions/{session_id}")

def get_session_messages(session_id: str):
    resp = get_session(session_id)
    return {"messages": resp.get("messages", [])}

def get_session_insights(session_id: str):
    return {"error": "Insights are not available in the v1 API. Please upgrade to v3."}

def send_message(session_id: str, message: str):
    return client.post(f"sessions/{session_id}/message", json={"message": message})

def update_session_tags(session_id: str, tags: List[str]):
    return client.put(f"sessions/{session_id}/tags", json={"tags": tags})

def terminate_session(session_id: str):
    return client.delete(f"sessions/{session_id}")
