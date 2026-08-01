from typing import List
from devin_cli.api.client import client

def get_ip_access_list():
    """Get enterprise IP access allowlist."""
    return client.get("enterprise/ip-access-list")

def replace_ip_access_list(cidr_blocks: List[str]):
    """Replace entire IP access allowlist."""
    return client.put("enterprise/ip-access-list", json={"ip_ranges": cidr_blocks})

def add_ip_access_list(cidr_blocks: List[str]):
    """Append IP ranges to the enterprise IP access allowlist."""
    return client.post("enterprise/ip-access-list", json={"ip_ranges": cidr_blocks})

def clear_ip_access_list():
    """Clear enterprise IP access allowlist."""
    return client.delete("enterprise/ip-access-list")
