from devin_cli.api.client import client

def list_secrets():
    return client.get("secrets")

def create_secret(name: str, value: str):
    return client.post("secrets", json={"name": name, "value": value})

def delete_secret(secret_id: str):
    return client.delete(f"secrets/{secret_id}")
