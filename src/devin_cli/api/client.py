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
        pass

    @property
    def token(self) -> Optional[str]:
        return config.api_token

    @property
    def headers(self) -> Dict[str, str]:
        t = self.token
        headers = {
            "Content-Type": "application/json",
        }
        if t:
            headers["Authorization"] = f"Bearer {t}"
        return headers

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

        content_type = response.headers.get("Content-Type", "")
        if "application/json" in content_type:
            try:
                return response.json()
            except ValueError:
                return response.text
        
        # If it's not JSON, it might be an attachment or raw text
        if any(t in content_type for t in ["image/", "application/octet-stream", "application/pdf"]):
            return response.content
            
        return response.text

    def request(self, method: str, endpoint: str, **kwargs) -> Any:
        self._ensure_token()
        
        endpoint = endpoint.lstrip("/")
        
        # Determine the base URL and whether to inject organization
        if endpoint.startswith("v3beta1/"):
            base = config.base_url.replace("/v3", "").replace("/v2", "").replace("/v1", "").rstrip("/")
            url = f"{base}/{endpoint}"
            # Inject organization for v3beta1 if not present
            if config.org_id and "/organizations/" not in url:
                url = url.replace("v3beta1/", f"v3beta1/organizations/{config.org_id}/")
        elif endpoint.startswith("enterprise/"):
            url = f"{self.BASE_URL}/{endpoint}"
        else:
            # Standard path, inject organization if configured
            if config.org_id and not endpoint.startswith("organizations/"):
                endpoint = f"organizations/{config.org_id}/{endpoint}"
            url = f"{self.BASE_URL}/{endpoint}"
        
        # Merge headers if needed, but usually self.headers is enough
        headers = self.headers.copy()
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))

        # Handle file uploads (remove Content-Type)
        if "files" in kwargs:
            headers.pop("Content-Type", None)

        try:
            with httpx.Client(follow_redirects=True) as client:
                response = client.request(method, url, headers=headers, **kwargs)
                return self._handle_response(response)
        except httpx.RequestError as e:
            raise APIError(f"Network error: {e}")

    def get(self, endpoint: str, **kwargs) -> Any:
        return self.request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs) -> Any:
        return self.request("POST", endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs) -> Any:
        return self.request("PUT", endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> Any:
        return self.request("DELETE", endpoint, **kwargs)

client = APIClient()
