from typing import Optional
from devin_cli.api.client import client

def list_service_users(limit: int = 100, after: Optional[str] = None):
    """List service users in the enterprise."""
    params = {"limit": limit}
    if after:
        params["after"] = after
    return client.get("enterprise/service-users", params=params)

def get_service_user(service_user_id: str):
    """Get service user details."""
    return client.get(f"enterprise/service-users/{service_user_id}")

def list_service_user_api_keys(service_user_id: str):
    """List API keys for a service user."""
    return client.get(f"enterprise/service-users/{service_user_id}/api-keys")

def create_service_user_api_key(service_user_id: str, name: str):
    """Create a new API key for a service user."""
    return client.post(f"enterprise/service-users/{service_user_id}/api-keys", json={"name": name})

def rotate_service_user_api_key(service_user_id: str, key_id: str):
    """Rotate an API key for a service user."""
    return client.post(f"enterprise/service-users/{service_user_id}/api-keys/{key_id}/rotate")

def revoke_service_user_api_key(service_user_id: str, key_id: str):
    """Revoke an API key for a service user."""
    return client.delete(f"enterprise/service-users/{service_user_id}/api-keys/{key_id}")
