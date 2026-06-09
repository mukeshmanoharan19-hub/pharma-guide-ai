"""Medical safety layer (Phase 8).

Combines rule-based risk detection, prompt-injection / restricted-advice
guardrails, and escalation messaging into a single :func:`assess_safety` entry
point used as the first node of the agent graph.

The assessment is deterministic and dependency-light (pure regex), so it adds no
latency or LLM cost and is easy to unit-test.
"""

from __future__ import annotations

from app.safety.escalation import (
    DOCTOR_CONSULT_DISCLAIMER,
    EMERGENCY_MESSAGE,
    PROMPT_INJECTION_MESSAGE,
    SafetyAssessment,
    SafetyLevel,
)
from app.safety.guardrails import detect_prompt_injection, detect_restricted_advice
from app.safety.risk_detector import detect_risks

# Risk flags that warrant an emergency short-circuit.
_EMERGENCY_FLAGS = {"emergency_symptom", "severe_adverse_reaction"}
# Risk flags that only warrant an appended doctor-consult disclaimer.
_CAUTION_FLAGS = {"pregnancy", "pediatric"}


def assess_safety(query: str) -> SafetyAssessment:
    """Evaluate a user message and return a structured safety verdict.

    Precedence (highest first):
      1. Prompt injection  -> hard block, refuse.
      2. Emergency / severe -> hard block, urge immediate medical care.
      3. Caution (pregnancy/pediatric/restricted advice) -> allow + disclaimer.
      4. Otherwise          -> info, no action.
    """
    text = query or ""
    flags: list[str] = []

    if detect_prompt_injection(text):
        return SafetyAssessment(
            level=SafetyLevel.WARNING,
            flags=["prompt_injection"],
            blocked=True,
            message=PROMPT_INJECTION_MESSAGE,
        )

    risk_flags = detect_risks(text)
    flags.extend(risk_flags)

    if _EMERGENCY_FLAGS.intersection(flags):
        return SafetyAssessment(
            level=SafetyLevel.EMERGENCY,
            flags=flags,
            blocked=True,
            message=EMERGENCY_MESSAGE,
            block_commerce=True,
        )

    if detect_restricted_advice(text):
        flags.append("restricted_advice")

    if _CAUTION_FLAGS.intersection(flags) or "restricted_advice" in flags:
        return SafetyAssessment(
            level=SafetyLevel.WARNING,
            flags=flags,
            disclaimer=DOCTOR_CONSULT_DISCLAIMER,
        )

    return SafetyAssessment(level=SafetyLevel.INFO, flags=flags)


__all__ = [
    "assess_safety",
    "SafetyAssessment",
    "SafetyLevel",
    "detect_risks",
    "detect_prompt_injection",
    "detect_restricted_advice",
    "EMERGENCY_MESSAGE",
    "PROMPT_INJECTION_MESSAGE",
    "DOCTOR_CONSULT_DISCLAIMER",
]
