"""Shared infrastructure for agent tools.

Provides standardized error types, a retry/logging decorator for tool core
functions, and a safe envelope used when exposing tools to LLM agents.
"""

from __future__ import annotations

from functools import wraps
from typing import Any, Callable, Dict

from loguru import logger
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

MAX_TOOL_ATTEMPTS = 3


class ToolException(Exception):
    """A non-retryable tool failure (validation, not found, business rule)."""


class RetryableToolError(Exception):
    """A transient failure worth retrying (e.g. a flaky DB/network call)."""


def with_tool_handling(name: str) -> Callable:
    """Wrap a tool core function with logging and retry-on-transient-error.

    Retries only ``RetryableToolError``. ``ToolException`` propagates
    immediately; any other unexpected exception is converted to a
    ``ToolException`` after logging.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        @retry(
            reraise=True,
            stop=stop_after_attempt(MAX_TOOL_ATTEMPTS),
            wait=wait_exponential(multiplier=0.2, max=2),
            retry=retry_if_exception_type(RetryableToolError),
        )
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            logger.info(f"[tool:{name}] invoked")
            try:
                result = func(*args, **kwargs)
                logger.success(f"[tool:{name}] completed")
                return result
            except (ToolException, RetryableToolError):
                raise
            except Exception as e:  # pragma: no cover - defensive
                logger.exception(f"[tool:{name}] unexpected error: {e}")
                raise ToolException(str(e))

        return wrapper

    return decorator


def ok(data: Any) -> Dict[str, Any]:
    """Build a success envelope for agent-facing tool calls."""
    if hasattr(data, "model_dump"):
        data = data.model_dump(mode="json")
    return {"success": True, "data": data}


def err(message: str) -> Dict[str, Any]:
    """Build an error envelope for agent-facing tool calls."""
    return {"success": False, "error": message}


def safe_call(func: Callable, **kwargs: Any) -> Dict[str, Any]:
    """Invoke a tool core function and convert the outcome to an envelope.

    Used by the StructuredTool wrappers so agents always receive a
    JSON-serializable result rather than a raised exception.
    """
    try:
        return ok(func(**kwargs))
    except ToolException as e:
        return err(str(e))
    except Exception as e:  # pragma: no cover - defensive
        logger.exception(f"Unhandled tool error: {e}")
        return err("An unexpected error occurred while running the tool.")
