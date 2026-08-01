from typing import Optional
from devin_cli.api.client import client

def list_audit_logs(limit: int = 100, after: Optional[str] = None, order: Optional[str] = "desc"):
    """List enterprise audit logs."""
    params = {"limit": limit}
    if after:
        params["after"] = after
    if order:
        params["order"] = order
    return client.get("enterprise/audit-logs", params=params)

def list_org_audit_logs(limit: int = 100, after: Optional[str] = None, order: Optional[str] = "desc"):
    """List organization audit logs."""
    params = {"limit": limit}
    if after:
        params["after"] = after
    if order:
        params["order"] = order
    return client.get("audit-logs", params=params)
