from devin_cli.api.client import client

def list_organizations():
    """List all organizations (Enterprise key required)"""
    return client.get("enterprise/organizations")

def get_organization(org_id: str):
    """Get details of a specific organization (Enterprise key required)"""
    return client.get(f"enterprise/organizations/{org_id}")
