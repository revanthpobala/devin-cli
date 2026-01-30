from typing import List, Optional
from devin_cli.api.client import client

def list_playbooks():
    return client.get("playbooks")

def create_playbook(title: str, body: str, macro: str = None):
    data = {"title": title, "body": body}
    if macro:
        data["macro"] = macro
    return client.post("playbooks", data=data)

def get_playbook(playbook_id: str):
    return client.get(f"playbooks/{playbook_id}")

def update_playbook(playbook_id: str, title: str = None, body: str = None, macro: str = None):
    data = {}
    if title:
        data["title"] = title
    if body:
        data["body"] = body
    if macro:
        data["macro"] = macro
    return client.put(f"playbooks/{playbook_id}", data=data)

def delete_playbook(playbook_id: str):
    return client.delete(f"playbooks/{playbook_id}")
