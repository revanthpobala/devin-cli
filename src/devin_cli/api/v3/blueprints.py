from typing import Optional
from devin_cli.api.client import client

def list_blueprints():
    """List blueprints for organization."""
    return client.get("blueprints")

def get_blueprint(blueprint_id: str):
    """Get blueprint by ID."""
    return client.get(f"blueprints/{blueprint_id}")

def trigger_build():
    """Trigger a manual snapshot build for the organization."""
    return client.post("builds")

def list_builds():
    """List snapshot builds for the organization."""
    return client.get("builds")

def get_build(build_id: str):
    """Get snapshot build details."""
    return client.get(f"builds/{build_id}")
