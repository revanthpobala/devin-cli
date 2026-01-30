from typing import List, Optional
from devin_cli.api.client import client

def list_sessions(limit: int = 100, offset: int = 0, tags: List[str] = None):
    params = {"limit": limit, "offset": offset}
    if tags:
        params["tags"] = tags
    return client.get("sessions", params=params)

def create_session(
    prompt: str,
    idempotent: bool = False,
    snapshot_id: str = None,
    playbook_id: str = None,
    unlisted: bool = False,
    tags: List[str] = None,
    session_secrets: List[dict] = None,
    title: Optional[str] = None,
    knowledge_ids: Optional[List[str]] = None,
    secret_ids: Optional[List[str]] = None,
    max_acu_limit: Optional[int] = None,
):
    data = {
        "prompt": prompt,
        "idempotent": idempotent,
        "unlisted": unlisted
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
        
    return client.post("sessions", data=data)

def get_session(session_id: str):
    return client.get(f"sessions/{session_id}")

def send_message(session_id: str, message: str):
    return client.post(f"sessions/{session_id}/message", data={"message": message})

def update_session_tags(session_id: str, tags: List[str]):
    return client.put(f"sessions/{session_id}/tags", data={"tags": tags})

def terminate_session(session_id: str):
    return client.delete(f"sessions/{session_id}")
