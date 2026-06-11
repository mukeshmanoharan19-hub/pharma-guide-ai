"""Answer verification (Phase 6): retrieval validation + grounding check.

- ``validate_retrieval`` is a cheap, deterministic gate: do we have enough
  non-empty documents to attempt a grounded answer?
- ``check_grounding`` is an LLM faithfulness judge that flags answers not
  supported by the context. It fails open (assumes grounded) on any error so it
  can never block a response by itself.
"""

from __future__ import annotations

from typing import List, Optional

from loguru import logger
from pydantic import BaseModel, Field

from app.core.config import settings
from app.observability.langsmith import runnable_config
from app.core.prompts import GROUNDING_CHECK_PROMPT


class GroundingResult(BaseModel):
    is_grounded: bool = Field(
        default=True,
        description="True if every product claim is supported by the context.",
    )
    reason: str = Field(default="", description="Short explanation of the verdict.")
    unsupported_claims: List[str] = Field(default_factory=list)


def validate_retrieval(documents: List, min_results: Optional[int] = None) -> bool:
    """Return True if retrieval produced enough usable context."""
    minimum = settings.RETRIEVAL_MIN_RESULTS if min_results is None else min_results
    if not documents:
        return False
    non_empty = [
        d for d in documents if (getattr(d, "page_content", "") or "").strip()
    ]
    return len(non_empty) >= minimum


def check_grounding(answer: str, context: str) -> GroundingResult:
    """LLM faithfulness check; fails open (grounded) on error or when disabled."""
    if not settings.ENABLE_HALLUCINATION_CHECK:
        return GroundingResult(is_grounded=True, reason="check disabled")

    if not answer or not answer.strip():
        return GroundingResult(is_grounded=True, reason="empty answer")

    if not context or not context.strip():
        # No context to verify against; treat as not grounded so callers can
        # surface a caveat rather than present unverifiable product claims.
        return GroundingResult(
            is_grounded=False, reason="no retrieval context available"
        )

    from app.retrieval.query_expansion import llm

    prompt = GROUNDING_CHECK_PROMPT.format(context=context, answer=answer)

    try:
        judge = llm.with_structured_output(GroundingResult)
        result: GroundingResult = judge.invoke(
            prompt,
            config=runnable_config(
                run_name="rag.grounding_check",
                tags=["phase10", "rag", "verification"],
                metadata={"component": "grounding_judge"},
            ),
        )
        if not result.is_grounded:
            logger.warning(
                "Grounding check flagged answer: {} | claims={}",
                result.reason,
                result.unsupported_claims,
            )
        return result
    except Exception as exc:
        logger.warning(f"Grounding check failed, assuming grounded: {exc}")
        return GroundingResult(is_grounded=True, reason=f"check error: {exc}")
