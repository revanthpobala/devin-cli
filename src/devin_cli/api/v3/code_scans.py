from typing import Optional
from devin_cli.api.client import client

def list_code_scan_findings(limit: int = 100, after: Optional[str] = None):
    """List enterprise code scan findings."""
    params = {"limit": limit}
    if after:
        params["after"] = after
    return client.get("v3beta1/enterprise/code-scans/findings", params=params)

def get_code_scan_metrics():
    """Get metrics for enterprise code scans."""
    return client.get("v3beta1/enterprise/code-scans/metrics")

def remediate_code_scan_finding(finding_id: str, prompt_override: Optional[str] = None):
    """Launch a Devin session to remediate a code scan finding."""
    data = {"finding_id": finding_id}
    if prompt_override:
        data["prompt_override"] = prompt_override
    return client.post("v3beta1/enterprise/code-scans/remediate", json=data)
