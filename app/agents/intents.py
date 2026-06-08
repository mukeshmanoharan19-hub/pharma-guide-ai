"""Intent taxonomy and intent -> agent routing map for the supervisor.

Phase 4 defines the six intents from the roadmap and maps each to the graph
node that should handle it. The specialist nodes themselves are fleshed out in
Phase 5 (tool-bound agents); for now several of them are thin wrappers.
"""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field

# --- Intent ids ---
MEDICINE_SEARCH = "medicine_search"
SYMPTOM_ANALYSIS = "symptom_analysis"
CART = "cart"
CHECKOUT = "checkout"
ORDER_TRACKING = "order_tracking"
GENERAL = "general"

VALID_INTENTS = {
    MEDICINE_SEARCH,
    SYMPTOM_ANALYSIS,
    CART,
    CHECKOUT,
    ORDER_TRACKING,
    GENERAL,
}

# --- Graph node names that handle each intent ---
MEDICINE_AGENT = "medicine_agent"
SYMPTOM_AGENT = "symptom_agent"
COMMERCE_AGENT = "commerce_agent"
SUPPORT_AGENT = "support_agent"
GENERAL_CHAT = "general_chat"

# Intent -> handling node. Multiple intents can map to the same agent.
INTENT_ROUTE_MAP = {
    MEDICINE_SEARCH: MEDICINE_AGENT,
    SYMPTOM_ANALYSIS: SYMPTOM_AGENT,
    CART: COMMERCE_AGENT,
    CHECKOUT: COMMERCE_AGENT,
    ORDER_TRACKING: SUPPORT_AGENT,
    GENERAL: GENERAL_CHAT,
}

# The node used whenever the supervisor is unsure / intent is unrecognised.
FALLBACK_ROUTE = GENERAL_CHAT

# All possible routing targets (used to validate conditional-edge maps).
ALL_ROUTES = sorted(set(INTENT_ROUTE_MAP.values()))


class IntentClassification(BaseModel):
    """Structured output produced by the supervisor LLM."""

    primary_intent: str = Field(
        ...,
        description="Single best-fit intent id from the allowed list.",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Certainty in primary_intent, 0.0-1.0.",
    )
    secondary_intents: List[str] = Field(
        default_factory=list,
        description="Other intent ids that also apply (may be empty).",
    )
    reasoning: str = Field(
        default="",
        description="One short sentence explaining the classification.",
    )
