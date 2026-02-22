"""
Unit tests for the crisis detection service.
These tests are pure-Python — no DB, no HTTP, no OpenAI calls.
"""
import pytest

from app.services.crisis_service import assess_crisis


class TestCrisisDetection:
    """Hard trigger patterns should always set is_crisis=True, severity='critical'."""

    @pytest.mark.parametrize("text", [
        "I want to kill myself",
        "I am thinking about suicide",
        "I'm going to end my life tonight",
        "I've been cutting myself",
        "I want to overdose on pills",
        "I can't go on living like this",
        "I don't want to exist anymore",
        "thinking about hanging myself",
    ])
    def test_critical_triggers(self, text: str):
        result = assess_crisis(text)
        assert result.is_crisis is True
        assert result.severity == "critical"
        assert len(result.matched_keywords) > 0

    def test_safe_message(self):
        result = assess_crisis("I had a really tough day at work but I'm feeling better now.")
        assert result.is_crisis is False
        assert result.severity == "none"

    def test_single_soft_keyword_not_crisis(self):
        result = assess_crisis("I feel hopeless about my career.")
        assert result.is_crisis is False

    def test_multiple_soft_keywords_triggers_moderate(self):
        result = assess_crisis("I feel worthless and hopeless. There's no way out.")
        assert result.is_crisis is True
        assert result.severity == "moderate"

    def test_case_insensitive(self):
        result = assess_crisis("SUICIDE is all I think about")
        assert result.is_crisis is True

    def test_matched_keywords_populated(self):
        result = assess_crisis("I want to end my life and I've been self-harming.")
        assert len(result.matched_keywords) >= 1
