import httpx
from devin_cli.config import config
from rich.console import Console
import sys
from typing import Optional, Any, Dict

console = Console()

class APIError(Exception):
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code

class APIClient:
    def __init__(self):
        self._token: Optional[str] = None
        self._headers: Dict[str, str] = {}

    @property
    def token(self) -> Optional[str]:
        if not self._token:
            self._token = config.api_token
        return self._token

    @property
    def headers(self) -> Dict[str, str]:
        if not self._headers:
            t = self.token
            if t:
                 self._headers = {
                    "Authorization": f"Bearer {t}",
                    "Content-Type": "application/json",
                }
        return self._headers

    @property
    def BASE_URL(self) -> str:
        return config.base_url.rstrip("/")

    def _ensure_token(self):
        if not self.token:
            # Only raise error if meaningful operation is attempted
            raise APIError("API token not found. Run 'devin configure' to set your API token.")

    def _handle_response(self, response: httpx.Response) -> Any:
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            status = e.response.status_code
            if status == 401:
                raise APIError("Invalid or expired API token (401). Run 'devin configure'.", status)
            elif status == 403:
                raise APIError("Insufficient permissions (403).", status)
            elif status == 404:
                raise APIError("Resource not found (404).", status)
            elif status == 429:
                raise APIError("Rate limit exceeded (429). Please try again later.", status)
            elif status >= 500:
                raise APIError(f"Server error ({status}).", status)
            else:
                raise APIError(f"HTTP Error {status}: {e}", status)
        
        if response.status_code == 204:
            return None

        try:
            return response.json()
        except ValueError:
            return response.text

    def request(self, method: str, endpoint: str, **kwargs) -> Any:
        self._ensure_token()
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        
        # Merge headers if needed, but usually self.headers is enough
        headers = self.headers.copy()
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))

        # Handle file uploads (remove Content-Type)
        if "files" in kwargs:
            headers.pop("Content-Type", None)

        try:
            with httpx.Client() as client:
                response = client.request(method, url, headers=headers, **kwargs)
                return self._handle_response(response)
        except httpx.RequestError as e:
            raise APIError(f"Network error: {e}")

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        return self.request("GET", endpoint, params=params)

    def post(self, endpoint: str, data: Optional[Dict] = None, files: Optional[Dict] = None) -> Any:
        return self.request("POST", endpoint, json=data, files=files)

    def put(self, endpoint: str, data: Optional[Dict] = None) -> Any:
        return self.request("PUT", endpoint, json=data)

    def delete(self, endpoint: str) -> Any:
        return self.request("DELETE", endpoint)

client = APIClient()
