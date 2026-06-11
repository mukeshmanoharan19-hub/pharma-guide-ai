"""LangSmith tracing helpers (Phase 10).

This module is intentionally lightweight: it only shapes RunnableConfig
(`run_name`, `tags`, `metadata`) and checks whether tracing is enabled.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, Optional

from app.core.config import settings


def langsmith_enabled() -> bool:
    return bool(
        settings.LANGCHAIN_TRACING_V2
        and settings.LANGSMITH_API_KEY
        and settings.LANGSMITH_PROJECT
    )


def runnable_config(
    *,
    run_name: str,
    tags: Optional[Iterable[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    base: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Return a merged RunnableConfig with stable tracing attributes."""
    cfg: Dict[str, Any] = dict(base or {})
    cfg["run_name"] = run_name
    merged_tags = list(cfg.get("tags") or [])
    if tags:
        merged_tags.extend(list(tags))
    # Deduplicate while preserving order.
    seen = set()
    cfg["tags"] = [t for t in merged_tags if not (t in seen or seen.add(t))]
    if metadata:
        merged_meta = dict(cfg.get("metadata") or {})
        merged_meta.update(metadata)
        cfg["metadata"] = merged_meta
    return cfg

