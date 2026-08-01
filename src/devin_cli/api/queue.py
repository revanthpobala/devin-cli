from devin_cli.config import config
import importlib

def _get_impl():
    if config.api_version == "v1":
        try:
            return importlib.import_module(f"devin_cli.api.v1.queue")
        except ImportError:
            raise NotImplementedError(f"'queue' feature is only available in Devin API v3, or is not implemented for v1. Run 'devin configure' to switch your API version to v3.")
    return importlib.import_module(f"devin_cli.api.v3.queue")

def __getattr__(name):
    return getattr(_get_impl(), name)
