from __future__ import annotations

from loguru import logger


def ragas_available() -> bool:
    try:
        import ragas  # noqa: F401

        return True
    except Exception:
        return False


def compute_ragas_metrics(*, samples: list[dict]) -> dict:
    """Best-effort placeholder integration.

    We keep this optional so CI smoke runs can execute without external eval
    dependencies/API spend. When `ragas` is installed, this hook can be expanded
    to call `ragas.evaluate(...)`.
    """
    if not ragas_available():
        return {"enabled": False, "reason": "ragas_not_installed"}
    logger.info("RAGAS installed; using placeholder adapter (custom metrics active).")
    return {"enabled": True, "reason": "adapter_placeholder", "samples": len(samples)}

