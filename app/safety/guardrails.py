"""Input guardrails: prompt-injection and restricted-advice detection."""

from __future__ import annotations

from app.safety import patterns


def detect_prompt_injection(text: str) -> bool:
    """Detect attempts to override instructions, jailbreak, or exfiltrate prompts."""
    return patterns.matches_any(text, patterns.PROMPT_INJECTION_PATTERNS)


def detect_restricted_advice(text: str) -> bool:
    """Detect requests for diagnosis or personalised dosage (informational-only)."""
    return patterns.matches_any(text, patterns.RESTRICTED_ADVICE_PATTERNS)
