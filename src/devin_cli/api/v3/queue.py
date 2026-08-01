from devin_cli.api.client import client

def get_queue_status():
    """Get the queue status for an enterprise."""
    return client.get("enterprise/queue")
