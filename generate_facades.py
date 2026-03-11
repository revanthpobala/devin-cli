import os

modules = ["attachments", "consumption", "knowledge", "members", "organizations", "playbooks", "repositories", "schedules", "secrets", "sessions"]

for mod in modules:
    content = f"""from devin_cli.config import config
import importlib

def _get_impl():
    if config.api_version == "v1":
        try:
            return importlib.import_module(f"devin_cli.api.v1.{mod}")
        except ImportError:
            raise NotImplementedError(f"'{mod}' feature is only available in Devin API v3, or is not implemented for v1. Run 'devin configure' to switch your API version to v3.")
    return importlib.import_module(f"devin_cli.api.v3.{mod}")

def __getattr__(name):
    return getattr(_get_impl(), name)
"""
    with open(f"src/devin_cli/api/{mod}.py", "w") as f:
        f.write(content)
