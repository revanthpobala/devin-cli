import logging
import httpx
from devin_cli.api import sessions
from devin_cli.config import config
import json

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("httpx").setLevel(logging.DEBUG)

print("Active Token:", config.api_token[:10] if config.api_token else "None")
print("Base URL:", config.base_url)

try:
    print("Sending request...")
    resp = sessions.create_session(prompt="Testing duplicate bug. Ignore.", title="Duplicate Test")
    print("Response:")
    print(json.dumps(resp, indent=2))
except Exception as e:
    print("Error:", e)
