import json
import urllib.error
import urllib.request
from urllib.parse import urljoin
from pathlib import Path


TOKEN_STORAGE_PATH = Path.home() / ".pharma_guide_ai" / "token.json"


def _ensure_token_dir() -> None:
    """Ensure the token storage directory exists."""
    TOKEN_STORAGE_PATH.parent.mkdir(parents=True, exist_ok=True)


def save_token(token: str, email: str) -> None:
    """Save auth token to local storage."""
    _ensure_token_dir()
    data = {"access_token": token, "email": email}
    TOKEN_STORAGE_PATH.write_text(json.dumps(data))


def load_token() -> dict | None:
    """Load stored auth token if it exists."""
    if TOKEN_STORAGE_PATH.exists():
        try:
            return json.loads(TOKEN_STORAGE_PATH.read_text())
        except Exception:
            return None
    return None


def delete_token() -> None:
    """Delete stored auth token."""
    if TOKEN_STORAGE_PATH.exists():
        TOKEN_STORAGE_PATH.unlink()


def backend_request(path: str, payload: dict, backend_url: str, token: str | None = None) -> dict:
    url = urljoin(backend_url, path)
    data = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(url=url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.load(response)
    except urllib.error.HTTPError as http_error:
        body = http_error.read().decode("utf-8")
        error_detail = None
        try:
            parsed = json.loads(body)
            error_detail = parsed.get("detail") or parsed.get("error") or body
        except Exception:
            error_detail = body
        raise RuntimeError(error_detail or f"HTTP {http_error.code}: {http_error.reason}")
    except urllib.error.URLError as url_error:
        raise RuntimeError(str(url_error.reason))


def login(email: str, password: str, backend_url: str) -> dict:
    return backend_request("/auth/login", {"email": email, "password": password}, backend_url)


def register(full_name: str, email: str, password: str, backend_url: str) -> dict:
    return backend_request(
        "/auth/register",
        {"full_name": full_name, "email": email, "password": password},
        backend_url,
    )


def ask(query: str, backend_url: str, token: str | None = None) -> dict:
    return backend_request(
        "/api/chat/ask",
        {"query": query},
        backend_url,
        token=token,
    )


def ask_stream(query: str, backend_url: str, token: str | None = None):
    """Stream the chat response from the backend."""
    url = urljoin(backend_url, "/api/chat/ask/stream")
    data = json.dumps({"query": query}).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(url=url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            for line in response:
                decoded = line.decode("utf-8").strip()
                if decoded.startswith("data: "):
                    chunk = decoded[6:]  # Remove 'data: ' prefix
                    if chunk and not chunk.startswith("[ERROR]"):
                        yield chunk
                    elif chunk.startswith("[ERROR]"):
                        raise RuntimeError(chunk[7:])  # Remove '[ERROR] ' prefix
    except urllib.error.HTTPError as http_error:
        body = http_error.read().decode("utf-8")
        error_detail = None
        try:
            parsed = json.loads(body)
            error_detail = parsed.get("detail") or parsed.get("error") or body
        except Exception:
            error_detail = body
        raise RuntimeError(error_detail or f"HTTP {http_error.code}: {http_error.reason}")
    except urllib.error.URLError as url_error:
        raise RuntimeError(str(url_error.reason))
