"""Safety levels, the structured assessment result, and escalation messaging."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


class SafetyLevel:
    """Severity of a safety assessment."""

    INFO = "info"
    WARNING = "warning"
    EMERGENCY = "emergency"


EMERGENCY_MESSAGE = (
    "⚠️ This sounds like it could be a medical emergency. I'm an informational "
    "assistant and can't provide emergency care.\n\n"
    "Please seek immediate medical attention now — call your local emergency "
    "number (for example 112/911/108) or go to the nearest emergency room. If "
    "someone is unconscious, not breathing, or severely bleeding, call emergency "
    "services right away.\n\n"
    "I can help with medicine information, store policies, and orders once you're safe."
)

PROMPT_INJECTION_MESSAGE = (
    "I can't help with that request. I'm here to assist with medicine "
    "information, store policies, and your orders — feel free to ask me about "
    "any of those."
)

DOCTOR_CONSULT_DISCLAIMER = (
    "This is general information, not medical advice. Please consult a doctor or "
    "pharmacist before starting, stopping, or changing any medication — "
    "especially for children, during pregnancy or breastfeeding, or if you have "
    "existing conditions."
)


@dataclass
class SafetyAssessment:
    """Structured verdict produced by :func:`app.safety.assess_safety`."""

    level: str = SafetyLevel.INFO
    flags: List[str] = field(default_factory=list)
    # When True the graph short-circuits and returns ``message`` directly.
    blocked: bool = False
    # User-facing replacement response (only when ``blocked``).
    message: Optional[str] = None
    # Appended to a normally-generated answer (non-blocking caution).
    disclaimer: Optional[str] = None
    # Hint to disable commerce actions for this turn.
    block_commerce: bool = False

    def as_dict(self) -> dict:
        return {
            "level": self.level,
            "flags": list(self.flags),
            "blocked": self.blocked,
            "block_commerce": self.block_commerce,
        }
