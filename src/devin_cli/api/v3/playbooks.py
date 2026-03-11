from typing import List, Optional
from devin_cli.api.client import client

def list_playbooks():
    return client.get("playbooks")

def create_playbook(title: str, body: str, macro: Optional[str] = None):
    data = {"title": title, "body": body}
    if macro:
        data["macro"] = macro
    return client.post("playbooks", json=data)

def get_playbook(playbook_id: str):
    return client.get(f"playbooks/{playbook_id}")

def update_playbook(playbook_id: str, title: str, body: Optional[str] = None, macro: Optional[str] = None):
    data = {"title": title}
    if body:
        data["body"] = body
    if macro:
        data["macro"] = macro
    return client.put(f"playbooks/{playbook_id}", json=data)

def delete_playbook(playbook_id: str):
    return client.delete(f"playbooks/{playbook_id}")

# Enterprise Playbooks
def list_enterprise_playbooks():
    return client.get("enterprise/playbooks")

def create_enterprise_playbook(title: str, body: str, macro: Optional[str] = None):
    data = {"title": title, "body": body}
    if macro:
        data["macro"] = macro
    return client.post("enterprise/playbooks", json=data)

def get_enterprise_playbook(playbook_id: str):
    return client.get(f"enterprise/playbooks/{playbook_id}")

def update_enterprise_playbook(playbook_id: str, title: str, body: Optional[str] = None, macro: Optional[str] = None):
    data = {"title": title}
    if body:
        data["body"] = body
    if macro:
        data["macro"] = macro
    return client.put(f"enterprise/playbooks/{playbook_id}", json=data)

def delete_enterprise_playbook(playbook_id: str):
    return client.delete(f"enterprise/playbooks/{playbook_id}")
