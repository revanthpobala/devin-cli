from typing import List, Optional, Union
from devin_cli.api.client import client

def list_repositories(limit: int = 100, after: Optional[str] = None):
    params = {"limit": limit}
    if after:
        params["after"] = after
    return client.get("v3beta1/repositories", params=params)

def list_indexed_repositories():
    return client.get("v3beta1/repositories/indexing")

def get_indexing_status(repository_path: str):
    """repository_path should be owner/repo"""
    return client.get(f"v3beta1/repositories/{repository_path}/indexing")

def index_repository(repository_path: str, branch_name: Optional[str] = None):
    data = {}
    if branch_name:
        data["branch_name"] = branch_name
    return client.put(f"v3beta1/repositories/{repository_path}/indexing", json=data)

def index_repositories_bulk(repository_paths: List[str]):
    return client.put("v3beta1/repositories/indexing/bulk", json={"repository_paths": repository_paths})

def remove_from_indexing(repository_path: str):
    return client.delete(f"v3beta1/repositories/{repository_path}/indexing")

def remove_from_indexing_bulk(repository_paths: List[str]):
    return client.delete("v3beta1/repositories/indexing/bulk", json={"repository_paths": repository_paths})

# Enterprise Git Management
def list_git_connections():
    return client.get("enterprise/git-providers/connections")

def list_git_permissions():
    return client.get("enterprise/git-providers/permissions")

def create_git_permission(org_id: str, permission: str):
    data = {"org_id": org_id, "permission": permission}
    return client.post("enterprise/git-providers/permissions", json=data)

def delete_git_permission(org_id: str):
    return client.delete(f"enterprise/git-providers/permissions", params={"org_id": org_id})
