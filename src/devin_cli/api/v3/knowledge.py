from typing import List, Optional
from devin_cli.api.client import client

def list_knowledge():
    return client.get("knowledge/notes")

def create_knowledge(
    title: str,
    body: str,
):
    data = {
        "title": title,
        "body": body,
    }
    return client.post("knowledge/notes", json=data)

def get_knowledge(note_id: str):
    return client.get(f"knowledge/notes/{note_id}")

def update_knowledge(
    note_id: str,
    title: Optional[str] = None,
    body: Optional[str] = None,
):
    data = {}
    if title:
        data["title"] = title
    if body:
        data["body"] = body
        
    return client.put(f"knowledge/notes/{note_id}", json=data)

def delete_knowledge(note_id: str):
    return client.delete(f"knowledge/notes/{note_id}")

# Enterprise Knowledge
def list_enterprise_knowledge():
    return client.get("enterprise/knowledge/notes")

def get_enterprise_knowledge(note_id: str):
    return client.get(f"enterprise/knowledge/notes/{note_id}")
