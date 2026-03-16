from typing import List, Optional
from devin_cli.api.client import client

def list_knowledge():
    return client.get("knowledge")

def create_knowledge(
    name: str = None,
    body: str = None,
    trigger_description: str = None,
    parent_folder_id: str = None,
    pinned_repo: str = None,
    title: str = None, # v3 fallback
    trigger: str = None, # v3 fallback
    **kwargs
):
    data = {
        "name": name or title,
        "body": body,
        "trigger_description": trigger_description or trigger or ""
    }
    if parent_folder_id:
        data["parent_folder_id"] = parent_folder_id
    if pinned_repo:
        data["pinned_repo"] = pinned_repo
        
    return client.post("knowledge", json=data)

def update_knowledge(
    knowledge_id: str,
    name: str = None,
    body: str = None,
    trigger_description: str = None,
    title: str = None, # v3 fallback
    trigger: str = None, # v3 fallback
    **kwargs
):
    data = {}
    if name or title:
        data["name"] = name or title
    if body:
        data["body"] = body
    if trigger_description or trigger:
        data["trigger_description"] = trigger_description or trigger
        
    return client.put(f"knowledge/{knowledge_id}", json=data)

def get_knowledge(knowledge_id: str):
    return client.get(f"knowledge/{knowledge_id}")

def delete_knowledge(knowledge_id: str):
    return client.delete(f"knowledge/{knowledge_id}")
