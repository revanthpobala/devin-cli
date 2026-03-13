import os
import json
from functools import wraps
import builtins

class Console:
    def print(self, *args, **kwargs):
        builtins.print("RICH_PRINT:", *args)

console = Console()

def handle_api_error(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            is_json = os.environ.get("DEVIN_OUTPUT_FORMAT") == "json"
            if is_json:
                original_print = console.print
                console.print = lambda *args, **kwargs: None
            
            try:
                result = func(*args, **kwargs)
            finally:
                if is_json:
                    console.print = original_print
                    
            if is_json and result is not None:
                builtins.print(json.dumps(result, indent=2))
            return result
        except Exception as e:
            builtins.print("ERROR:", e)
    return wrapper

@handle_api_error
def create_session_cmd():
    console.print("[green]Session created[/green]")
    resp = {"session_id": "123", "status": "running"}
    return resp

print("--- NORMAL MODE ---")
os.environ.pop("DEVIN_OUTPUT_FORMAT", None)
create_session_cmd()

print("\n--- JSON MODE ---")
os.environ["DEVIN_OUTPUT_FORMAT"] = "json"
create_session_cmd()
