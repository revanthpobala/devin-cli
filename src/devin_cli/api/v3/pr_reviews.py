from typing import Optional
from devin_cli.api.client import client

def trigger_pr_review(pr_url: str):
    """Trigger a Devin Review for a pull request."""
    return client.post("pr-reviews", json={"pr_url": pr_url})

def get_pr_review_status(pr_url: Optional[str] = None, repo_path: Optional[str] = None, pr_number: Optional[int] = None):
    """Get latest Devin Review status for a PR."""
    params = {}
    if pr_url:
        params["pr_url"] = pr_url
    if repo_path:
        params["repo_path"] = repo_path
    if pr_number:
        params["pr_number"] = pr_number
    return client.get("pr-reviews", params=params)

def trigger_enterprise_pr_review(pr_url: str):
    """Trigger an enterprise-scoped Devin Review."""
    return client.post("enterprise/pr-reviews", json={"pr_url": pr_url})

def get_enterprise_pr_review_status(pr_url: Optional[str] = None, repo_path: Optional[str] = None, pr_number: Optional[int] = None):
    """Get latest enterprise-scoped Devin Review status."""
    params = {}
    if pr_url:
        params["pr_url"] = pr_url
    if repo_path:
        params["repo_path"] = repo_path
    if pr_number:
        params["pr_number"] = pr_number
    return client.get("enterprise/pr-reviews", params=params)
