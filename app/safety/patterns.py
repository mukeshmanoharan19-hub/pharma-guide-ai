"""Compiled regex patterns for the medical safety layer.

Patterns are intentionally broad (high recall) because the cost of a false
positive is low — an extra disclaimer or an "seek medical care" nudge — while a
missed emergency is costly. All matching is case-insensitive.
"""

from __future__ import annotations

import re

_FLAGS = re.IGNORECASE


def _compile(patterns: list[str]) -> list[re.Pattern]:
    return [re.compile(p, _FLAGS) for p in patterns]


# --------------------------------------------------------------------------- #
# Emergency / red-flag symptoms -> hard block + "seek immediate care"
# --------------------------------------------------------------------------- #
EMERGENCY_PATTERNS = _compile([
    r"\bchest pain\b",
    r"\bpain in (?:my |the )?chest\b",
    r"\bchest tightness\b",
    r"\bheart attack\b",
    r"\bcardiac arrest\b",
    r"\b(?:can'?t|cannot|unable to|struggling to|hard to|difficulty) (?:breathe|breathing)\b",
    r"\b(?:shortness of breath|short of breath|trouble breathing)\b",
    r"\bnot breathing\b",
    r"\bsevere(?:ly)? bleed(?:ing)?\b",
    r"\bbleeding (?:heavily|a lot|badly|won'?t stop|that won'?t stop)\b",
    r"\bwon'?t stop bleeding\b",
    r"\b(?:unconscious|passed out|fainted|collapsed|not waking up|unresponsive)\b",
    r"\bstroke\b",
    r"\bface (?:drooping|droop)\b",
    r"\bslurred speech\b",
    r"\bnumbness on one side\b",
    r"\bsuicid(?:e|al)\b",
    r"\b(?:kill myself|end my life|want to die|take my own life)\b",
    r"\boverdose(?:d|ing)?\b",
    r"\btook too many (?:pills|tablets|medicines)\b",
    r"\b(?:anaphylaxis|anaphylactic)\b",
    r"\b(?:throat (?:closing|swelling)|can'?t swallow|tongue swelling)\b",
    r"\bseizure\b",
    r"\bconvulsion(?:s)?\b",
    r"\bvomiting blood\b",
    r"\bcoughing up blood\b",
    r"\bpoison(?:ing|ed)\b",
])

# Severe adverse drug reactions -> hard block + "seek immediate care"
SEVERE_ADVERSE_PATTERNS = _compile([
    r"\bsevere(?:ly)? allergic reaction\b",
    r"\bsevere(?:ly)? (?:rash|reaction|swelling)\b",
    r"\b(?:swelling of (?:the )?(?:face|lips|throat|tongue))\b",
    r"\b(?:hives all over|rash all over|spreading rash)\b",
    r"\bdifficulty (?:swallowing|speaking) after (?:taking|the medicine)\b",
    r"\bblister(?:ing|s) (?:skin|all over)\b",
])

# --------------------------------------------------------------------------- #
# Caution flags -> append doctor-consult disclaimer (non-blocking)
# --------------------------------------------------------------------------- #
PREGNANCY_PATTERNS = _compile([
    r"\bpregnan(?:t|cy)\b",
    r"\bexpecting a baby\b",
    r"\bbreast[\s-]?feed(?:ing)?\b",
    r"\blactating\b",
    r"\bnursing (?:mother|mom|baby)\b",
    r"\b(?:first|second|third) trimester\b",
])

PEDIATRIC_PATTERNS = _compile([
    r"\b(?:my )?(?:baby|infant|newborn|toddler)\b",
    r"\bmy (?:child|kid|son|daughter)\b",
    r"\bfor (?:a |my )?(?:child|kid|baby|infant|toddler)\b",
    r"\b\d+\s*(?:month|week|year)s?\s*old\b",
    r"\b(?:children|kids|paediatric|pediatric)\b",
])

# --------------------------------------------------------------------------- #
# Prompt injection / jailbreak attempts -> refuse
# --------------------------------------------------------------------------- #
PROMPT_INJECTION_PATTERNS = _compile([
    r"\bignore (?:all|the|your|any|previous|prior|above)[\w\s]*?instructions?\b",
    r"\bdisregard (?:all|the|your|any|previous|prior)[\w\s]*?(?:instructions?|rules?)\b",
    r"\bforget (?:all|your|the|everything|previous|prior)[\w\s]*?(?:instructions?|rules?)?\b",
    r"\b(?:reveal|show|print|repeat|tell me)[\w\s]*?(?:system prompt|your prompt|your instructions|the prompt)\b",
    r"\bsystem prompt\b",
    r"\byou are now\b",
    r"\bact as (?:a|an|if)\b",
    r"\bpretend (?:to be|you are)\b",
    r"\bdeveloper mode\b",
    r"\bjailbreak\b",
    r"\b(?:override|bypass|disable|turn off)[\w\s]*?(?:rules?|safety|guard(?:rails?)?|filters?|restrictions?)\b",
    r"\bdo anything now\b",
    r"\bDAN mode\b",
])

# --------------------------------------------------------------------------- #
# Restricted advice (diagnosis / personalised dosage) -> disclaimer
# --------------------------------------------------------------------------- #
RESTRICTED_ADVICE_PATTERNS = _compile([
    r"\bhow (?:much|many)[\w\s]*?(?:should|do|can) i (?:take|use)\b",
    r"\bwhat (?:dose|dosage)[\w\s]*?(?:should|do|can) i\b",
    r"\bwhat'?s the (?:right|correct|safe) (?:dose|dosage)\b",
    r"\bcan i (?:take|use|combine)[\w\s]*?(?:with|along with|together with)\b",
    r"\bis it safe (?:for me )?to (?:take|use|mix)\b",
    r"\bdiagnos(?:e|is)\b",
    r"\bdo i have (?:cancer|covid|diabetes|a tumou?r|an infection)\b",
    r"\bwhat (?:disease|illness|condition) do i have\b",
])


def matches_any(text: str, patterns: list[re.Pattern]) -> bool:
    return any(p.search(text) for p in patterns)
