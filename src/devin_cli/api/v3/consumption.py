from typing import Optional
from devin_cli.api.client import client

def get_session_consumption(session_id: str):
    """Get daily ACU consumption for a specific session"""
    return client.get(f"enterprise/consumption/daily/sessions/{session_id}")

def get_service_user_consumption(service_user_id: str):
    """Get daily ACU consumption for sessions initiated by a service user"""
    return client.get(f"enterprise/consumption/daily/service-users/{service_user_id}")

def list_consumption_cycles():
    """List consumption cycles (Enterprise key required)"""
    return client.get("enterprise/consumption/cycles")

def get_daily_consumption_breakdown():
    """Get overall daily ACU consumption breakdown"""
    return client.get("enterprise/consumption/daily")

def get_acu_limits():
    """Get ACU limits for the organization/enterprise"""
    return client.get("enterprise/consumption/limits")
