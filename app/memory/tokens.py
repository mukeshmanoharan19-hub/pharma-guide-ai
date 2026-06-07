"""Lightweight token estimation.

Uses ``tiktoken`` when available for accuracy, otherwise falls back to a
~4-characters-per-token heuristic. Kept dependency-free by design so the memory
layer works even without tiktoken installed.
"""

from typing import Optional

_encoder = None
_encoder_loaded = False


def _get_encoder():
    global _encoder, _encoder_loaded
    if _encoder_loaded:
        return _encoder
    _encoder_loaded = True
    try:  # pragma: no cover - optional dependency
        import tiktoken

        _encoder = tiktoken.get_encoding("cl100k_base")
    except Exception:
        _encoder = None
    return _encoder


def estimate_tokens(text: Optional[str]) -> int:
    """Estimate the number of tokens in a piece of text."""
    if not text:
        return 0

    encoder = _get_encoder()
    if encoder is not None:
        try:
            return len(encoder.encode(text))
        except Exception:
            pass

    # Heuristic fallback: average English token ~= 4 characters.
    return max(1, len(text) // 4)
