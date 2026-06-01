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

class BaseClient:
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
            path = str(e.request.url.path)
            
            error_detail = ""
            try:
                error_body = e.response.json()
                error_detail = error_body.get("detail") or error_body.get("message") or error_body.get("error") or str(error_body)
            except Exception:
                error_detail = e.response.text.strip()
                
            msg_suffix = f"\n  Path:   {path}"
            if error_detail:
                msg_suffix += f"\n  Detail: {error_detail}"

            if status == 401:
                raise APIError(f"Invalid or expired API token (401).{msg_suffix}", status)
            elif status == 403:
                raise APIError(f"Insufficient permissions (403).{msg_suffix}", status)
            elif status == 404:
                raise APIError(f"Resource not found (404).{msg_suffix}", status)
            elif status == 422:
                raise APIError(f"Validation Error (422).{msg_suffix}", status)
            elif status == 429:
                raise APIError(f"Rate limit exceeded (429). Please try again later.", status)
            elif status >= 500:
                raise APIError(f"Server error ({status}).{msg_suffix}", status)
            else:
                raise APIError(f"HTTP Error {status}.{msg_suffix}", status)
        if response.status_code == 204:
            return None

        content_type = response.headers.get("Content-Type", "")
        if "application/json" in content_type:
            try:
                return response.json()
            except ValueError:
                return response.text
        
        if any(t in content_type for t in ["image/", "application/octet-stream", "application/pdf"]):
            return response.content
            
        return response.text

    def _format_url(self, endpoint: str) -> str:
        raise NotImplementedError()

    def request(self, method: str, endpoint: str, **kwargs) -> Any:
        self._ensure_token()
        url = self._format_url(endpoint)
        
        headers = self.headers.copy()
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))

        if "files" in kwargs:
            headers.pop("Content-Type", None)

        import os
        verify_tls = True
        if os.environ.get("DEVIN_INSECURE_TLS") == "1":
            verify_tls = False
        elif os.environ.get("DEVIN_CA_BUNDLE"):
            verify_tls = os.environ.get("DEVIN_CA_BUNDLE")

        try:
            with httpx.Client(follow_redirects=True, verify=verify_tls, timeout=httpx.Timeout(120.0)) as client_httpx:
                try:
                    response = client_httpx.request(method, url, headers=headers, **kwargs)
                except httpx.RequestError as req_err:
                    if verify_tls is not False and ("SSL" in str(type(req_err).__name__) or "certificate" in str(req_err).lower() or isinstance(req_err, httpx.ConnectError)):
                        console.print(f"[bold yellow]Warning:[/bold yellow] TLS verification or connection failed ({req_err}). Retrying with verify=False... Set DEVIN_INSECURE_TLS=1 to suppress this warning.")
                        with httpx.Client(follow_redirects=True, verify=False, timeout=httpx.Timeout(120.0)) as insecure_client:
                            response = insecure_client.request(method, url, headers=headers, **kwargs)
                    else:
                        raise req_err
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

class V3Client(BaseClient):
    def _format_url(self, endpoint: str) -> str:
        endpoint = endpoint.lstrip("/")
        if endpoint.startswith("v3beta1/"):
            base = config.base_url.replace("/v3", "").replace("/v2", "").replace("/v1", "").rstrip("/")
            url = f"{base}/{endpoint}"
            if config.org_id and "/organizations/" not in url:
                url = url.replace("v3beta1/", f"v3beta1/organizations/{config.org_id}/")
            return url
        elif endpoint.startswith("enterprise/"):
            return f"{self.BASE_URL}/{endpoint}"
        else:
            if config.org_id and not endpoint.startswith("organizations/"):
                endpoint = f"organizations/{config.org_id}/{endpoint}"
            return f"{self.BASE_URL}/{endpoint}"

class V1Client(BaseClient):
    def _format_url(self, endpoint: str) -> str:
        return f"{self.BASE_URL}/{endpoint.lstrip('/')}"

class ClientProxy:
    def __init__(self):
        self._v1 = V1Client()
        self._v3 = V3Client()
        
    @property
    def _client(self) -> BaseClient:
        return self._v1 if config.api_version == "v1" else self._v3

    def get(self, endpoint: str, **kwargs) -> Any:
        return self._client.get(endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs) -> Any:
        return self._client.post(endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs) -> Any:
        return self._client.put(endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> Any:
        return self._client.delete(endpoint, **kwargs)

client = ClientProxy()
