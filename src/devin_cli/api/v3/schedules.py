from typing import List, Optional, Dict, Any
from devin_cli.api.client import client

def list_schedules(limit: int = 100, after: Optional[str] = None):
    params = {"limit": limit}
    if after:
        params["after"] = after
    return client.get("schedules", params=params)

def create_schedule(
    prompt: str,
    cron: str,
    title: Optional[str] = None,
    # Additional v3 parameters
    advanced_mode: Optional[str] = None,
    playbook_id: Optional[str] = None,
    repos: Optional[List[str]] = None,
    tags: Optional[List[str]] = None,
):
    data = {
        "prompt": prompt,
        "cron": cron,
    }
    if title:
        data["title"] = title
    if advanced_mode:
        data["advanced_mode"] = advanced_mode
    if playbook_id:
        data["playbook_id"] = playbook_id
    if repos:
        data["repos"] = repos
    if tags:
        data["tags"] = tags
        
    return client.post("schedules", json=data)

def get_schedule(schedule_id: str):
    return client.get(f"schedules/{schedule_id}")

def update_schedule(
    schedule_id: str,
    prompt: Optional[str] = None,
    cron: Optional[str] = None,
    title: Optional[str] = None,
    enabled: Optional[bool] = None,
):
    data = {}
    if prompt:
        data["prompt"] = prompt
    if cron:
        data["cron"] = cron
    if title:
        data["title"] = title
    if enabled is not None:
        data["enabled"] = enabled
        
    return client.put(f"schedules/{schedule_id}", json=data)

def delete_schedule(schedule_id: str):
    return client.delete(f"schedules/{schedule_id}")
