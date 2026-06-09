"""Rule-based clinical risk detection over the raw user message.

Returns a list of risk flags (possibly empty). The orchestration in
:func:`app.safety.assess_safety` decides how each flag escalates.
"""

from __future__ import annotations

from typing import List

from app.safety import patterns


def detect_emergency(text: str) -> bool:
    return patterns.matches_any(text, patterns.EMERGENCY_PATTERNS)


def detect_severe_adverse(text: str) -> bool:
    return patterns.matches_any(text, patterns.SEVERE_ADVERSE_PATTERNS)


def detect_pregnancy(text: str) -> bool:
    return patterns.matches_any(text, patterns.PREGNANCY_PATTERNS)


def detect_pediatric(text: str) -> bool:
    return patterns.matches_any(text, patterns.PEDIATRIC_PATTERNS)


def detect_risks(text: str) -> List[str]:
    """Collect all clinical risk flags present in ``text``."""
    flags: List[str] = []
    if detect_emergency(text):
        flags.append("emergency_symptom")
    if detect_severe_adverse(text):
        flags.append("severe_adverse_reaction")
    if detect_pregnancy(text):
        flags.append("pregnancy")
    if detect_pediatric(text):
        flags.append("pediatric")
    return flags
