from typing import Optional
from devin_cli.api.client import client

def list_guardrail_violations(
    limit: int = 100,
    after: Optional[str] = None,
    session_id: Optional[str] = None,
    guardrail_id: Optional[str] = None,
):
    """List enterprise guardrail violations."""
    params = {"limit": limit}
    if after:
        params["after"] = after
    if session_id:
        params["session_id"] = session_id
    if guardrail_id:
        params["guardrail_id"] = guardrail_id
    return client.get("v3beta1/enterprise/guardrail-violations", params=params)

def list_org_guardrail_violations(
    limit: int = 100,
    after: Optional[str] = None,
    session_id: Optional[str] = None,
    guardrail_id: Optional[str] = None,
):
    """List organization guardrail violations."""
    params = {"limit": limit}
    if after:
        params["after"] = after
    if session_id:
        params["session_id"] = session_id
    if guardrail_id:
        params["guardrail_id"] = guardrail_id
    return client.get("v3beta1/guardrail-violations", params=params)
