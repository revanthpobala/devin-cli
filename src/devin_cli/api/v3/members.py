from devin_cli.api.client import client

def get_self():
    """Get current authenticated user info (Enterprise context)"""
    # Based on Devin API v3 "Self" category info
    return client.get("enterprise/members/self")

def get_user(user_id: str):
    """Get info for a specific user"""
    return client.get(f"enterprise/members/users/{user_id}")
