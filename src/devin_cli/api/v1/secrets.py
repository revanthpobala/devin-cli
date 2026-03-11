from devin_cli.api.client import client

def list_secrets():
    return client.get("secrets")

def delete_secret(secret_id: str):
    return client.delete(f"secrets/{secret_id}")
