from typing import List, Optional
from devin_cli.api.client import client

def list_knowledge():
    return client.get("knowledge")

def create_knowledge(
    name: str,
    body: str,
    trigger_description: str,
    macro: str = None,
    parent_folder_id: str = None,
    pinned_repo: str = None
):
    data = {
        "name": name,
        "body": body,
        "trigger_description": trigger_description
    }
    if macro:
        data["macro"] = macro
    if parent_folder_id:
        data["parent_folder_id"] = parent_folder_id
    if pinned_repo:
        data["pinned_repo"] = pinned_repo
        
    return client.post("knowledge", data=data)

def update_knowledge(
    knowledge_id: str,
    name: str = None,
    body: str = None,
    trigger_description: str = None
):
    data = {}
    if name:
        data["name"] = name
    if body:
        data["body"] = body
    if trigger_description:
        data["trigger_description"] = trigger_description
        
    return client.put(f"knowledge/{knowledge_id}", data=data)

def delete_knowledge(knowledge_id: str):
    return client.delete(f"knowledge/{knowledge_id}")
