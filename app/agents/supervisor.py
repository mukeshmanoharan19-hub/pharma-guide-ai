"""Supervisor agent: LLM-based intent detection + routing resolution.

``classify_intent`` asks the LLM to label the latest user message; it always
returns a valid :class:`IntentClassification`, degrading to a low-confidence
``general`` result on any error. ``resolve_route`` applies the fallback policy
(unknown intent or low confidence -> general chat) and returns the graph node
that should handle the turn.
"""

from __future__ import annotations

from typing import Tuple

from loguru import logger

from app.agents.intents import (
    FALLBACK_ROUTE,
    GENERAL,
    INTENT_ROUTE_MAP,
    VALID_INTENTS,
    IntentClassification,
)
from app.core.config import settings
from app.core.prompts import INTENT_CLASSIFICATION_PROMPT


def classify_intent(
    query: str,
    history_text: str | None = None,
    summary_text: str | None = None,
) -> IntentClassification:
    """Classify the user's latest message into an intent (never raises)."""
    # Imported lazily so importing this module doesn't require the LLM/env.
    from app.services.rag_service import llm

    prompt = INTENT_CLASSIFICATION_PROMPT.format(
        summary=summary_text or "None.",
        history=history_text or "None.",
        question=query,
    )

    try:
        classifier = llm.with_structured_output(IntentClassification)
        result: IntentClassification = classifier.invoke(prompt)
    except Exception as exc:
        logger.warning(f"Intent classification failed, defaulting to general: {exc}")
        return IntentClassification(
            primary_intent=GENERAL,
            confidence=0.0,
            secondary_intents=[],
            reasoning="fallback: classifier error",
        )

    # Normalise unrecognised labels to a low-confidence general result.
    if result.primary_intent not in VALID_INTENTS:
        logger.warning(
            f"Classifier returned unknown intent '{result.primary_intent}'; "
            "treating as general."
        )
        result.primary_intent = GENERAL
        result.confidence = min(result.confidence, 0.3)

    result.secondary_intents = [
        i for i in result.secondary_intents if i in VALID_INTENTS
    ]
    return result


def resolve_route(
    classification: IntentClassification,
    threshold: float | None = None,
) -> Tuple[str, str]:
    """Return ``(route_node, effective_intent)`` applying the fallback policy."""
    threshold = (
        settings.INTENT_CONFIDENCE_THRESHOLD if threshold is None else threshold
    )

    intent = classification.primary_intent
    if intent not in VALID_INTENTS or classification.confidence < threshold:
        return FALLBACK_ROUTE, GENERAL

    return INTENT_ROUTE_MAP[intent], intent
