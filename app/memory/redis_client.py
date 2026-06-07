"""Redis-backed hot cache for recent conversation messages.

All operations degrade gracefully: if Redis is unavailable, reads return
``None`` (treated as a cache miss) and writes are silently skipped so the
application keeps working off PostgreSQL alone.
"""

from __future__ import annotations

import json
from typing import List, Optional

import redis
from loguru import logger

from app.core.config import settings

# How many recent messages to retain in the Redis hot cache per session.
RECENT_CACHE_SIZE = 50
# Expire idle session caches after 7 days.
SESSION_TTL_SECONDS = 60 * 60 * 24 * 7

_client: Optional[redis.Redis] = None


def get_redis() -> Optional[redis.Redis]:
    """Return a lazily-created Redis client, or ``None`` if it cannot connect."""
    global _client
    if _client is None:
        try:
            _client = redis.from_url(
                settings.REDIS_URL, decode_responses=True
            )
        except Exception as e:  # pragma: no cover - defensive
            logger.warning(f"Could not create Redis client: {e}")
            return None
    return _client


def _messages_key(session_id: str) -> str:
    return f"session:{session_id}:messages"


def push_message(session_id: str, message: dict) -> None:
    """Append a message to the session's hot cache and trim/expire it."""
    client = get_redis()
    if client is None:
        return
    try:
        key = _messages_key(session_id)
        pipe = client.pipeline()
        pipe.rpush(key, json.dumps(message))
        pipe.ltrim(key, -RECENT_CACHE_SIZE, -1)
        pipe.expire(key, SESSION_TTL_SECONDS)
        pipe.execute()
    except Exception as e:
        logger.warning(f"Redis push_message failed (continuing): {e}")


def hydrate(session_id: str, messages: List[dict]) -> None:
    """Replace the cache contents with the provided messages."""
    client = get_redis()
    if client is None or not messages:
        return
    try:
        key = _messages_key(session_id)
        pipe = client.pipeline()
        pipe.delete(key)
        for message in messages[-RECENT_CACHE_SIZE:]:
            pipe.rpush(key, json.dumps(message))
        pipe.expire(key, SESSION_TTL_SECONDS)
        pipe.execute()
    except Exception as e:
        logger.warning(f"Redis hydrate failed (continuing): {e}")


def get_recent_messages(session_id: str, limit: int) -> Optional[List[dict]]:
    """Return the last ``limit`` cached messages, or ``None`` on a cache miss."""
    client = get_redis()
    if client is None:
        return None
    try:
        raw = client.lrange(_messages_key(session_id), -limit, -1)
        if not raw:
            return None
        return [json.loads(item) for item in raw]
    except Exception as e:
        logger.warning(f"Redis get_recent_messages failed (continuing): {e}")
        return None


def clear_session(session_id: str) -> None:
    client = get_redis()
    if client is None:
        return
    try:
        client.delete(_messages_key(session_id))
    except Exception as e:
        logger.warning(f"Redis clear_session failed (continuing): {e}")
