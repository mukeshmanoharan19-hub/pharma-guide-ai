"""Specialist agent specs: which tools and system prompt each agent uses.

Keeps the agent → (tools, prompt) wiring declarative so the graph can build
each specialist's bound tool set from the Phase 2 registry.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from app.agents import intents
from app.core import prompts


@dataclass(frozen=True)
class AgentSpec:
    node: str
    tool_names: List[str]
    system_prompt: str


# Tool subsets are aligned with the roadmap's per-agent tool lists, with a few
# closely-related catalog tools added where an agent's stated responsibilities
# require them (e.g. the Medicine agent needs product_details to answer about
# side effects / dosage).
MEDICINE_AGENT_SPEC = AgentSpec(
    node=intents.MEDICINE_AGENT,
    tool_names=[
        "search_medicine",
        "alternative_medicine",
        "product_details",
        "stock_availability",
    ],
    system_prompt=prompts.MEDICINE_AGENT_PROMPT,
)

SYMPTOM_AGENT_SPEC = AgentSpec(
    node=intents.SYMPTOM_AGENT,
    tool_names=["search_medicine", "product_details"],
    system_prompt=prompts.SYMPTOM_AGENT_PROMPT,
)

COMMERCE_AGENT_SPEC = AgentSpec(
    node=intents.COMMERCE_AGENT,
    tool_names=[
        "add_to_cart",
        "remove_from_cart",
        "update_cart",
        "view_cart",
        "prepare_order",
        "confirm_order",
    ],
    system_prompt=prompts.COMMERCE_AGENT_PROMPT,
)

SUPPORT_AGENT_SPEC = AgentSpec(
    node=intents.SUPPORT_AGENT,
    tool_names=["order_status", "purchase_history", "user_profile"],
    system_prompt=prompts.SUPPORT_AGENT_PROMPT,
)

SPECIALIST_SPECS = [
    MEDICINE_AGENT_SPEC,
    SYMPTOM_AGENT_SPEC,
    COMMERCE_AGENT_SPEC,
    SUPPORT_AGENT_SPEC,
]
