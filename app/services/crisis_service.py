"""
Crisis detection service.

Uses a multi-layer keyword approach:
  Layer 1 – hard-trigger phrases  → immediate CRITICAL flag
  Layer 2 – soft contextual terms → scored risk assessment

Keeps false-positive rate low while catching edge cases.
"""
import json
import re
from dataclasses import dataclass, field
from typing import List, Tuple

# ── Keyword lists ─────────────────────────────────────────────────────────────

_CRITICAL_PATTERNS: List[str] = [
    r"\bsuicid\w*\b",
    r"\bkill\s+(my)?self\b",
    r"\bend\s+(my\s+)?life\b",
    r"\bwant\s+to\s+die\b",
    r"\bself[- ]harm\b",
    r"\bcut\s+(my)?self\b",
    r"\boverdos\w*\b",
    r"\bhang\s+(my)?self\b",
    r"\bjump\s+off\b",
    r"\bno\s+(reason|point)\s+to\s+(live|go\s+on)\b",
    r"\bcan'?t\s+go\s+on\b",
    r"\bdon'?t\s+want\s+to\s+(live|exist)\b",
]

_SOFT_PATTERNS: List[str] = [
    r"\bhopeless\b",
    r"\bworthless\b",
    r"\bburden\b",
    r"\bno\s+way\s+out\b",
    r"\bgive\s+up\b",
    r"\bcan'?t\s+take\s+(it|this)\s+anymore\b",
    r"\bfeel\s+(so\s+)?empty\b",
    r"\bnothing\s+(matters|left)\b",
]

_COMPILED_CRITICAL = [
    re.compile(p, re.IGNORECASE) for p in _CRITICAL_PATTERNS
]
_COMPILED_SOFT = [
    re.compile(p, re.IGNORECASE) for p in _SOFT_PATTERNS
]


@dataclass
class CrisisAssessment:
    is_crisis: bool
    severity: str  # "none" | "moderate" | "critical"
    matched_keywords: List[str] = field(default_factory=list)
    soft_score: int = 0


def assess_crisis(text: str) -> CrisisAssessment:
    """
    Analyse user text for crisis signals.

    Returns a CrisisAssessment:
      - is_crisis=True if ANY critical pattern OR ≥2 soft patterns match.
      - severity="critical" for hard triggers, "moderate" for soft-only.
    """
    matched: List[str] = []

    # Hard triggers
    for pattern in _COMPILED_CRITICAL:
        m = pattern.search(text)
        if m:
            matched.append(m.group(0).lower())

    if matched:
        return CrisisAssessment(
            is_crisis=True,
            severity="critical",
            matched_keywords=matched,
        )

    # Soft / contextual triggers
    soft_matches: List[str] = []
    for pattern in _COMPILED_SOFT:
        m = pattern.search(text)
        if m:
            soft_matches.append(m.group(0).lower())

    if len(soft_matches) >= 2:
        return CrisisAssessment(
            is_crisis=True,
            severity="moderate",
            matched_keywords=soft_matches,
            soft_score=len(soft_matches),
        )

    return CrisisAssessment(
        is_crisis=False,
        severity="none",
        matched_keywords=soft_matches,
        soft_score=len(soft_matches),
    )


CRISIS_RESPONSE_MESSAGE = (
    "I'm really concerned about what you've shared. "
    "Your life has value and there are people who want to help you right now.\n\n"
    "🆘 **Please reach out immediately:**\n"
    "- **988 Suicide & Crisis Lifeline**: Call or text **988** (US)\n"
    "- **Crisis Text Line**: Text HOME to **741741**\n"
    "- **International Association for Suicide Prevention**: "
    "https://www.iasp.info/resources/Crisis_Centres/\n"
    "- **Emergency services**: Call **911** or go to your nearest emergency room\n\n"
    "You don't have to face this alone. Please contact one of these resources now."
)
