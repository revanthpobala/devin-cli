from devin_cli.api.client import client
from pathlib import Path

def upload_file(file_path: str):
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
        
    with open(path, "rb") as f:
        files = {"file": f}
        # client.post handles Content-Type removal for files
        return client.post("attachments", files=files)
