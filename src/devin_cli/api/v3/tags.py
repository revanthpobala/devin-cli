from typing import List, Optional
from devin_cli.api.client import client

def get_org_tags():
    """Get allowed session tags for the organization."""
    return client.get("tags")

def append_org_tags(tags: List[str]):
    """Append tags to the allowed session tags for the organization."""
    return client.post("tags", json={"tags": tags})

def replace_org_tags(tags: List[str]):
    """Replace all allowed session tags for the organization."""
    return client.put("tags", json={"tags": tags})

def clear_org_tags():
    """Clear all allowed session tags for the organization."""
    return client.delete("tags")

def remove_org_tag(tag: str):
    """Remove a single tag from allowed tags for the organization."""
    return client.delete(f"tags/{tag}")

def get_default_tag():
    """Get default tag for organization."""
    return client.get("enterprise/organizations/default-tag")

def set_default_tag(tag: str):
    """Set default tag for organization."""
    return client.put("enterprise/organizations/default-tag", json={"tag": tag})

def clear_default_tag():
    """Clear default tag for organization."""
    return client.delete("enterprise/organizations/default-tag")
