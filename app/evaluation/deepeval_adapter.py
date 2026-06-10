from __future__ import annotations

from loguru import logger


def deepeval_available() -> bool:
    try:
        import deepeval  # noqa: F401

        return True
    except Exception:
        return False


def compute_deepeval_metrics(*, samples: list[dict]) -> dict:
    """Optional DeepEval bridge (kept non-blocking for CI smoke)."""
    if not deepeval_available():
        return {"enabled": False, "reason": "deepeval_not_installed"}
    logger.info(
        "DeepEval installed; using placeholder adapter (custom assertions active)."
    )
    return {"enabled": True, "reason": "adapter_placeholder", "samples": len(samples)}

