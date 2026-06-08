"""Checkpointer factory for LangGraph state persistence.

Prefers a Postgres-backed saver (durable across process restarts) and falls
back to an in-memory saver when Postgres / psycopg are unavailable (e.g. local
dev or test environments). The checkpointer is created lazily and cached as a
module-level singleton so the connection pool and checkpoint tables are set up
only once per process.
"""

from __future__ import annotations

from typing import Optional

from loguru import logger

from app.core.config import settings

_checkpointer = None


def get_checkpointer():
    """Return the process-wide checkpointer, building it on first use."""
    global _checkpointer
    if _checkpointer is None:
        _checkpointer = _build_checkpointer()
    return _checkpointer


def _build_checkpointer():
    saver = _try_postgres_saver()
    if saver is not None:
        return saver

    from langgraph.checkpoint.memory import MemorySaver

    logger.warning(
        "Using in-memory LangGraph checkpointer; conversation state will not "
        "survive process restarts. Install langgraph-checkpoint-postgres + "
        "psycopg and ensure DATABASE_URL is reachable for durable checkpoints."
    )
    return MemorySaver()


def _try_postgres_saver():
    try:
        from langgraph.checkpoint.postgres import PostgresSaver
        from psycopg_pool import ConnectionPool
    except Exception as exc:  # pragma: no cover - depends on optional deps
        logger.info(f"Postgres checkpointer deps not available: {exc}")
        return None

    try:
        pool = ConnectionPool(
            conninfo=settings.DATABASE_URL,
            max_size=settings.CHECKPOINT_POOL_SIZE,
            open=True,
            kwargs={"autocommit": True, "prepare_threshold": 0},
        )
        saver = PostgresSaver(pool)
        saver.setup()
        logger.success("LangGraph using PostgresSaver for durable checkpoints")
        return saver
    except Exception as exc:  # pragma: no cover - depends on live DB
        logger.warning(f"Failed to initialise PostgresSaver: {exc}")
        return None
