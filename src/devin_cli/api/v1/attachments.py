import mimetypes
from pathlib import Path
from devin_cli.api.client import client

def upload_file(file_path: str, **kwargs):
    path = Path(file_path)
    mime_type, _ = mimetypes.guess_type(path)
    mime_type = mime_type or "application/octet-stream"
    
    with open(path, "rb") as f:
        # V1 used multipart/form-data with 'file' argument
        return client.post("attachments", files={"file": (path.name, f, mime_type)})

def download_attachment(attachment_id: str, file_name: str, **kwargs):
    # Depending on exactly what v1 required, it might just be the direct path or stream
    return client.get(f"attachments/{attachment_id}")
