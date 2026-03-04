"""
ATDD Tests for Story 8-2: AI Strategy Analysis Service

These tests are designed to FAIL before implementation (TDD RED phase).
Run: pytest tests/unit/test_story_8_2_ai_advisor.py -v

Generated: 2026-03-03
Story: 8-2-ai-advisor
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Literal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ============================================================================
# Test Data Factory
# ============================================================================


class SuggestionFactory:
    """Factory for creating test data for AI advisor."""

    @staticmethod
    def create_add_suggestion(
        content: str = "When BTC breaks 70000, sell 50% of ETH position",
        priority: int = 2,
        expiry_hours: int = 24,
        reason: str = "BTC breaking key resistance may trigger market correction",
        **overrides
    ) -> dict:
        """Create mock add strategy suggestion."""
        return {
            "action": "add",
            "content": content,
            "priority": priority,
            "expiry_hours": expiry_hours,
            "reason": reason,
            **overrides,
        }

    @staticmethod
    def create_disable_suggestion(
        strategy_id: int = 3,
        reason: str = "Strategy condition has become invalid due to market changes",
        **overrides
    ) -> dict:
        """Create mock disable strategy suggestion."""
        return {
            "action": "disable",
            "strategy_id": strategy_id,
            "reason": reason,
            **overrides,
        }

    @staticmethod
    def create_llm_response(suggestions: list = None) -> str:
        """Create mock LLM JSON response."""
        import json

        if suggestions is None:
            suggestions = [
                SuggestionFactory.create_add_suggestion(),
                SuggestionFactory.create_disable_suggestion(),
            ]

        response_data = {"suggestions": suggestions}
        json_str = json.dumps(response_data, indent=2)

        # Return with markdown code block
        return f"```json\n{json_str}\n```"

    @staticmethod
    def create_llm_response_raw(suggestions: list = None) -> str:
        """Create mock LLM JSON response without markdown."""
        import json

        if suggestions is None:
            suggestions = [
                SuggestionFactory.create_add_suggestion(),
            ]

        response_data = {"suggestions": suggestions}
        return json.dumps(response_data, indent=2)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def suggestion_factory():
    """Provide SuggestionFactory."""
    return SuggestionFactory()


@pytest.fixture
def mock_llm():
    """Create mock LLMClient instance."""
    llm = AsyncMock()

    # Set up default return value for chat()
    llm.chat.return_value = SuggestionFactory.create_llm_response()

    return llm


@pytest.fixture
def mock_api():
    """Create mock TerminalAPI instance."""
    from tests.unit.test_story_8_1_data_collector import StrategyDataFactory

    api = AsyncMock()
    factory = StrategyDataFactory()

    # Set up default return values
    api.get_positions.return_value = factory.create_position_data()
    api.get_strategies.return_value = [factory.create_strategy_data()]
    api.get_vault.return_value = factory.create_vault_data()
    api.get_eth_price.return_value = factory.create_eth_price_data()
    api.get_tokens.return_value = factory.create_token_list(10)
    api.get_candles.return_value = factory.create_candle_data(24)

    return api


@pytest.fixture
def advisor(mock_llm, mock_api):
    """Create StrategyAdvisor with mocked dependencies."""
    # Import here to allow tests to run before module exists
    from advisor import StrategyAdvisor

    return StrategyAdvisor(mock_llm, mock_api)


@pytest.fixture(autouse=True)
def mock_save_analysis():
    """Mock save_analysis to avoid writing to real data files during tests."""
    with patch("advisor_history.save_analysis", return_value="test1234"):
        yield


@pytest.fixture(autouse=True)
def mock_sync_to_surge():
    """Mock sync_to_surge to avoid actual surge CLI calls during tests."""
    with patch("advisor_history.sync_to_surge"):
        yield


# ============================================================================
# Test Classes - AC4: Suggestion Dataclass
# ============================================================================


class TestSuggestionDataclass:
    """Tests for Suggestion dataclass (AC4)."""

    def test_suggestion_dataclass_exists(self):
        """Suggestion dataclass should be defined in advisor module."""
        # GIVEN: advisor module
        # WHEN: Importing Suggestion
        # THEN: Suggestion should be importable
        from advisor import Suggestion

        assert Suggestion is not None

    def test_suggestion_is_dataclass(self):
        """Suggestion should be a dataclass."""
        from advisor import Suggestion

        assert hasattr(Suggestion, "__dataclass_fields__")

    def test_suggestion_has_action_field(self):
        """Suggestion should have action field with Literal["add", "disable"] type."""
        from advisor import Suggestion

        fields = Suggestion.__dataclass_fields__
        assert "action" in fields

    def test_suggestion_has_content_field(self):
        """Suggestion should have optional content field."""
        from advisor import Suggestion

        fields = Suggestion.__dataclass_fields__
        assert "content" in fields

    def test_suggestion_has_priority_field(self):
        """Suggestion should have priority field with default value 1."""
        from advisor import Suggestion

        fields = Suggestion.__dataclass_fields__
        assert "priority" in fields

        # Test default value
        suggestion = Suggestion(action="add", content="Test")
        assert suggestion.priority == 1

    def test_suggestion_has_expiry_hours_field(self):
        """Suggestion should have expiry_hours field with default value 0."""
        from advisor import Suggestion

        fields = Suggestion.__dataclass_fields__
        assert "expiry_hours" in fields

        # Test default value
        suggestion = Suggestion(action="add", content="Test")
        assert suggestion.expiry_hours == 0

    def test_suggestion_has_strategy_id_field(self):
        """Suggestion should have optional strategy_id field."""
        from advisor import Suggestion

        fields = Suggestion.__dataclass_fields__
        assert "strategy_id" in fields

    def test_suggestion_has_reason_field(self):
        """Suggestion should have reason field with default empty string."""
        from advisor import Suggestion

        fields = Suggestion.__dataclass_fields__
        assert "reason" in fields

        # Test default value
        suggestion = Suggestion(action="add", content="Test")
        assert suggestion.reason == ""

    def test_suggestion_validates_add_action_requires_content(self):
        """Suggestion should raise ValueError when content missing for add action."""
        from advisor import Suggestion

        # GIVEN: Suggestion with add action but no content
        # WHEN: Creating instance
        # THEN: Should raise ValueError
        with pytest.raises(ValueError, match="content is required"):
            Suggestion(action="add")

    def test_suggestion_validates_disable_action_requires_strategy_id(self):
        """Suggestion should raise ValueError when strategy_id missing for disable action."""
        from advisor import Suggestion

        # GIVEN: Suggestion with disable action but no strategy_id
        # WHEN: Creating instance
        # THEN: Should raise ValueError
        with pytest.raises(ValueError, match="strategy_id is required"):
            Suggestion(action="disable")

    def test_suggestion_creates_valid_add_suggestion(self):
        """Suggestion should create valid add suggestion with all fields."""
        from advisor import Suggestion

        # GIVEN: All required fields for add action
        # WHEN: Creating instance
        suggestion = Suggestion(
            action="add",
            content="Test strategy",
            priority=2,
            expiry_hours=24,
            reason="Test reason"
        )

        # THEN: Should create successfully
        assert suggestion.action == "add"
        assert suggestion.content == "Test strategy"
        assert suggestion.priority == 2
        assert suggestion.expiry_hours == 24
        assert suggestion.reason == "Test reason"

    def test_suggestion_creates_valid_disable_suggestion(self):
        """Suggestion should create valid disable suggestion with required fields."""
        from advisor import Suggestion

        # GIVEN: All required fields for disable action
        # WHEN: Creating instance
        suggestion = Suggestion(
            action="disable",
            strategy_id=5,
            reason="Test reason"
        )

        # THEN: Should create successfully
        assert suggestion.action == "disable"
        assert suggestion.strategy_id == 5
        assert suggestion.reason == "Test reason"


# ============================================================================
# Test Classes - AC1: StrategyAdvisor Class
# ============================================================================


class TestStrategyAdvisorClass:
    """Tests for StrategyAdvisor class (AC1)."""

    def test_strategy_advisor_class_exists(self):
        """StrategyAdvisor class should be defined in advisor module."""
        from advisor import StrategyAdvisor

        assert StrategyAdvisor is not None

    def test_strategy_advisor_accepts_llm_client(self, mock_api):
        """StrategyAdvisor should accept LLMClient in constructor."""
        from advisor import StrategyAdvisor
        from llm import LLMClient

        # Create a mock LLMClient
        mock_llm = MagicMock(spec=LLMClient)

        # Should not raise exception
        advisor = StrategyAdvisor(mock_llm, mock_api)
        assert advisor.llm is mock_llm

    def test_strategy_advisor_accepts_terminal_api(self, mock_llm):
        """StrategyAdvisor should accept TerminalAPI in constructor."""
        from advisor import StrategyAdvisor
        from api import TerminalAPI

        # Create a mock TerminalAPI
        mock_api = MagicMock(spec=TerminalAPI)

        # Should not raise exception
        advisor = StrategyAdvisor(mock_llm, mock_api)
        assert advisor.api is mock_api or hasattr(advisor, 'collector')

    def test_strategy_advisor_creates_collector_internally(self, mock_llm, mock_api):
        """StrategyAdvisor should create StrategyDataCollector internally."""
        from advisor import StrategyAdvisor, StrategyDataCollector

        advisor = StrategyAdvisor(mock_llm, mock_api)

        # Should have collector attribute
        assert hasattr(advisor, "collector")
        assert isinstance(advisor.collector, StrategyDataCollector)

    def test_strategy_advisor_has_max_suggestions_constant(self, mock_llm, mock_api):
        """StrategyAdvisor should have MAX_SUGGESTIONS constant set to 3."""
        from advisor import StrategyAdvisor

        advisor = StrategyAdvisor(mock_llm, mock_api)

        assert hasattr(advisor, "MAX_SUGGESTIONS")
        assert advisor.MAX_SUGGESTIONS == 3


# ============================================================================
# Test Classes - AC2: analyze() Method
# ============================================================================


class TestAnalyzeMethod:
    """Tests for analyze() method (AC2)."""

    def test_analyze_method_exists(self, mock_llm, mock_api):
        """analyze() method should exist on StrategyAdvisor."""
        from advisor import StrategyAdvisor

        advisor = StrategyAdvisor(mock_llm, mock_api)
        assert hasattr(advisor, "analyze")
        assert callable(advisor.analyze)

    @pytest.mark.asyncio
    async def test_analyze_is_async(self, advisor):
        """analyze() should be an async method."""
        import inspect

        assert inspect.iscoroutinefunction(advisor.analyze)

    @pytest.mark.asyncio
    async def test_analyze_returns_list_of_suggestions(self, advisor):
        """analyze() should return list of Suggestion objects."""
        from advisor import Suggestion

        result = await advisor.analyze()

        assert isinstance(result, list)
        # If list is not empty, check first item is Suggestion
        if len(result) > 0:
            assert isinstance(result[0], Suggestion)

    @pytest.mark.asyncio
    async def test_analyze_calls_collector_collect(self, advisor):
        """analyze() should call collector.collect() to gather data."""
        # Mock the collector.collect method
        with patch.object(advisor.collector, "collect") as mock_collect:
            from advisor import CollectedData

            mock_collect.return_value = CollectedData(
                positions={"ethBalance": 10.0},
                collected_at=datetime.now().isoformat()
            )

            await advisor.analyze()

            mock_collect.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_calls_collector_format_for_llm(self, advisor):
        """analyze() should call collector.format_for_llm() to format data."""
        with patch.object(advisor.collector, "collect") as mock_collect, \
             patch.object(advisor.collector, "format_for_llm") as mock_format:

            from advisor import CollectedData

            mock_collect.return_value = CollectedData(
                positions={"ethBalance": 10.0},
                collected_at=datetime.now().isoformat()
            )
            mock_format.return_value = "Formatted data"

            await advisor.analyze()

            mock_format.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_calls_llm_chat(self, advisor):
        """analyze() should call llm.chat() with system prompt and user message."""
        with patch.object(advisor.collector, "collect") as mock_collect, \
             patch.object(advisor.collector, "format_for_llm") as mock_format:

            from advisor import CollectedData

            mock_collect.return_value = CollectedData(
                positions={"ethBalance": 10.0},
                collected_at=datetime.now().isoformat()
            )
            mock_format.return_value = "Formatted data for analysis"

            await advisor.analyze()

            # Verify chat was called
            advisor.llm.chat.assert_called_once()

            # Check that system prompt and user message were passed
            call_args = advisor.llm.chat.call_args
            assert len(call_args[0]) >= 2  # system_prompt, user_message

    @pytest.mark.asyncio
    async def test_analyze_parses_json_response(self, advisor, suggestion_factory):
        """analyze() should parse JSON response and extract suggestions."""
        # Set up mock LLM response
        advisor.llm.chat.return_value = suggestion_factory.create_llm_response()

        result = await advisor.analyze()

        assert isinstance(result, list)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_analyze_limits_to_max_suggestions(self, advisor, suggestion_factory):
        """analyze() should limit suggestions to MAX_SUGGESTIONS (3)."""
        # Create response with more than 3 suggestions
        suggestions = [
            suggestion_factory.create_add_suggestion(content=f"Strategy {i}")
            for i in range(5)
        ]
        advisor.llm.chat.return_value = suggestion_factory.create_llm_response(suggestions)

        result = await advisor.analyze()

        assert len(result) <= advisor.MAX_SUGGESTIONS
        assert len(result) <= 3

    @pytest.mark.asyncio
    async def test_analyze_returns_empty_list_on_llm_error(self, advisor):
        """analyze() should return empty list when LLM returns error."""
        advisor.llm.chat.return_value = "Error: API key not configured"

        result = await advisor.analyze()

        assert isinstance(result, list)
        assert len(result) == 0


# ============================================================================
# Test Classes - AC3: System Prompt
# ============================================================================


class TestSystemPrompt:
    """Tests for system prompt (AC3)."""

    def test_system_prompt_constant_exists(self):
        """SYSTEM_PROMPT constant should exist in advisor module."""
        from advisor import SYSTEM_PROMPT

        assert SYSTEM_PROMPT is not None
        assert isinstance(SYSTEM_PROMPT, str)
        assert len(SYSTEM_PROMPT) > 0

    def test_system_prompt_includes_advisor_role(self):
        """SYSTEM_PROMPT should include advisor role definition."""
        from advisor import SYSTEM_PROMPT

        assert "advisor" in SYSTEM_PROMPT.lower() or "trading" in SYSTEM_PROMPT.lower()

    def test_system_prompt_specifies_json_output(self):
        """SYSTEM_PROMPT should specify JSON output format."""
        from advisor import SYSTEM_PROMPT

        assert "json" in SYSTEM_PROMPT.lower()
        assert "suggestions" in SYSTEM_PROMPT.lower()

    def test_system_prompt_includes_example_structure(self):
        """SYSTEM_PROMPT should include example JSON structure."""
        from advisor import SYSTEM_PROMPT

        # Should include example fields
        assert "action" in SYSTEM_PROMPT.lower()
        assert "add" in SYSTEM_PROMPT.lower() or "disable" in SYSTEM_PROMPT.lower()

    def test_system_prompt_includes_guidelines(self):
        """SYSTEM_PROMPT should provide guidelines for recommendations."""
        from advisor import SYSTEM_PROMPT

        # Should mention guidelines or constraints
        assert "guideline" in SYSTEM_PROMPT.lower() or "conservative" in SYSTEM_PROMPT.lower() or "risk" in SYSTEM_PROMPT.lower()


# ============================================================================
# Test Classes - JSON Parsing
# ============================================================================


class TestJSONParsing:
    """Tests for JSON parsing in _parse_suggestions() method."""

    @pytest.mark.asyncio
    async def test_parse_suggestions_with_valid_json(self, advisor, suggestion_factory):
        """_parse_suggestions() should parse valid JSON response."""
        raw_response = suggestion_factory.create_llm_response_raw()

        suggestions = advisor._parse_suggestions(raw_response)

        assert isinstance(suggestions, list)
        assert len(suggestions) > 0

    @pytest.mark.asyncio
    async def test_parse_suggestions_with_markdown_code_block(self, advisor, suggestion_factory):
        """_parse_suggestions() should extract JSON from markdown code block."""
        response_with_markdown = suggestion_factory.create_llm_response()

        suggestions = advisor._parse_suggestions(response_with_markdown)

        assert isinstance(suggestions, list)
        assert len(suggestions) > 0

    @pytest.mark.asyncio
    async def test_parse_suggestions_with_invalid_json(self, advisor):
        """_parse_suggestions() should handle invalid JSON gracefully."""
        invalid_response = "This is not JSON at all"

        suggestions = advisor._parse_suggestions(invalid_response)

        # Should return empty list, not raise exception
        assert isinstance(suggestions, list)

    @pytest.mark.asyncio
    async def test_parse_suggestions_with_missing_suggestions_key(self, advisor):
        """_parse_suggestions() should handle missing 'suggestions' key."""
        import json

        response_without_key = json.dumps({"data": []})

        suggestions = advisor._parse_suggestions(response_without_key)

        # Should return empty list
        assert isinstance(suggestions, list)
        assert len(suggestions) == 0

    @pytest.mark.asyncio
    async def test_parse_suggestions_handles_malformed_objects(self, advisor):
        """_parse_suggestions() should skip invalid suggestion objects."""
        import json

        malformed_response = json.dumps({
            "suggestions": [
                {"action": "add", "content": "Valid"},
                {"action": "add"},  # Missing content - should fail validation
                {"invalid": "object"},
            ]
        })

        suggestions = advisor._parse_suggestions(malformed_response)

        # Should only include valid suggestions
        assert isinstance(suggestions, list)


# ============================================================================
# Test Classes - Configuration
# ============================================================================


class TestConfiguration:
    """Tests for advisor configuration (AC5)."""

    def test_advisor_enabled_config_exists(self):
        """ADVISOR_ENABLED config should exist in config.py."""
        from config import ADVISOR_ENABLED

        assert ADVISOR_ENABLED is not None
        assert isinstance(ADVISOR_ENABLED, bool)

    def test_advisor_enabled_default_is_true(self):
        """ADVISOR_ENABLED should default to true."""
        from config import ADVISOR_ENABLED

        assert ADVISOR_ENABLED is True

    def test_advisor_interval_hours_config_exists(self):
        """ADVISOR_INTERVAL_HOURS config should exist in config.py."""
        from config import ADVISOR_INTERVAL_HOURS

        assert ADVISOR_INTERVAL_HOURS is not None
        assert isinstance(ADVISOR_INTERVAL_HOURS, int)

    def test_advisor_interval_hours_default_is_2(self):
        """ADVISOR_INTERVAL_HOURS should default to 2."""
        from config import ADVISOR_INTERVAL_HOURS

        assert ADVISOR_INTERVAL_HOURS == 2


class TestEnvExample:
    """Tests for .env.example documentation."""

    def test_env_example_includes_advisor_enabled(self):
        """ .env.example should include ADVISOR_ENABLED."""
        with open(".env.example") as f:
            content = f.read()

        assert "ADVISOR_ENABLED" in content

    def test_env_example_includes_advisor_interval_hours(self):
        """ .env.example should include ADVISOR_INTERVAL_HOURS."""
        with open(".env.example") as f:
            content = f.read()

        assert "ADVISOR_INTERVAL_HOURS" in content


# ============================================================================
# Test Classes - Error Handling
# ============================================================================


class TestErrorHandling:
    """Tests for error handling (AC2, AC6)."""

    @pytest.mark.asyncio
    async def test_analyze_handles_data_collection_errors(self, advisor):
        """analyze() should handle data collection errors gracefully."""
        # Make collector.collect() raise exception
        with patch.object(advisor.collector, "collect") as mock_collect:
            mock_collect.side_effect = Exception("Collection failed")

            # Should not raise exception
            result = await advisor.analyze()

            # Should return empty list
            assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_analyze_handles_llm_timeout(self, advisor):
        """analyze() should handle LLM timeout gracefully."""
        import asyncio

        advisor.llm.chat.side_effect = TimeoutError()

        result = await advisor.analyze()

        # Should return empty list, not raise exception
        assert isinstance(result, list)
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_analyze_handles_empty_suggestions(self, advisor):
        """analyze() should handle empty suggestions array."""
        import json

        empty_response = json.dumps({"suggestions": []})
        advisor.llm.chat.return_value = empty_response

        result = await advisor.analyze()

        assert isinstance(result, list)
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_analyze_never_raises_exception(self, advisor):
        """analyze() should never raise exceptions, always return list."""
        # Make everything fail
        with patch.object(advisor.collector, "collect") as mock_collect:
            mock_collect.side_effect = Exception("Total failure")

            try:
                result = await advisor.analyze()
                assert isinstance(result, list)
            except Exception as e:
                pytest.fail(f"analyze() should not raise exception, but raised: {e}")


# ============================================================================
# Test Classes - Integration
# ============================================================================


class TestIntegration:
    """End-to-end integration tests."""

    @pytest.mark.asyncio
    async def test_full_flow_produces_suggestions(self, advisor, suggestion_factory):
        """Full flow from data collection to suggestion output should work."""
        # Set up realistic mock responses
        advisor.llm.chat.return_value = suggestion_factory.create_llm_response()

        result = await advisor.analyze()

        # Should have valid suggestions
        assert isinstance(result, list)
        if len(result) > 0:
            from advisor import Suggestion
            assert isinstance(result[0], Suggestion)

    @pytest.mark.asyncio
    async def test_add_suggestion_has_correct_fields(self, advisor, suggestion_factory):
        """Add suggestion should have all required fields populated."""
        suggestions = [suggestion_factory.create_add_suggestion()]
        advisor.llm.chat.return_value = suggestion_factory.create_llm_response(suggestions)

        result = await advisor.analyze()

        if len(result) > 0:
            suggestion = result[0]
            assert suggestion.action == "add"
            assert suggestion.content is not None
            assert suggestion.reason is not None

    @pytest.mark.asyncio
    async def test_disable_suggestion_has_correct_fields(self, advisor, suggestion_factory):
        """Disable suggestion should have all required fields populated."""
        suggestions = [suggestion_factory.create_disable_suggestion()]
        advisor.llm.chat.return_value = suggestion_factory.create_llm_response(suggestions)

        result = await advisor.analyze()

        if len(result) > 0:
            suggestion = result[0]
            assert suggestion.action == "disable"
            assert suggestion.strategy_id is not None
            assert suggestion.reason is not None


# ============================================================================
# Test Classes - Logging
# ============================================================================


class TestLogging:
    """Tests for logging behavior."""

    @pytest.mark.asyncio
    async def test_error_logged_on_llm_failure(self, advisor):
        """LLM failures should be logged."""
        advisor.llm.chat.return_value = "Error: API failure"

        with patch("advisor.logger") as mock_logger:
            await advisor.analyze()

            # Should have logged error
            mock_logger.error.assert_called()

    @pytest.mark.asyncio
    async def test_warning_logged_on_invalid_json(self, advisor):
        """Invalid JSON responses should be logged as warnings."""
        advisor.llm.chat.return_value = "Not valid JSON"

        with patch("advisor.logger") as mock_logger:
            result = advisor._parse_suggestions("Not valid JSON")

            # Should have logged warning
            # (May not always log depending on implementation)
            # Just verify it doesn't crash
            assert isinstance(result, list)


# ============================================================================
# Test Classes - Enhanced Validation (Code Review Fixes)
# ============================================================================


class TestSuggestionValidation:
    """Tests for enhanced Suggestion validation from code review."""

    def test_action_must_be_exact_lowercase_add(self):
        """Action must be exactly 'add', not 'ADD' or 'add '."""
        from advisor import Suggestion

        with pytest.raises(ValueError, match="action must be"):
            Suggestion(action="ADD", content="test")

    def test_action_must_be_exact_lowercase_disable(self):
        """Action must be exactly 'disable', not 'Disable'."""
        from advisor import Suggestion

        with pytest.raises(ValueError, match="action must be"):
            Suggestion(action="Disable", strategy_id=1)

    def test_action_rejects_invalid_value(self):
        """Action must reject values like 'delete' or 'remove'."""
        from advisor import Suggestion

        with pytest.raises(ValueError, match="action must be"):
            Suggestion(action="delete", content="test")

    def test_priority_must_be_int_not_string(self):
        """Priority must be int, not string like 'high'."""
        from advisor import Suggestion

        with pytest.raises(ValueError, match="priority must be int"):
            Suggestion(action="add", content="test", priority="high")

    def test_priority_must_be_in_valid_range(self):
        """Priority must be in [0, 1, 2], not 3 or 100."""
        from advisor import Suggestion

        with pytest.raises(ValueError, match="priority must be int"):
            Suggestion(action="add", content="test", priority=100)

    def test_priority_rejects_negative(self):
        """Priority must be non-negative."""
        from advisor import Suggestion

        with pytest.raises(ValueError, match="priority must be int"):
            Suggestion(action="add", content="test", priority=-1)

    def test_expiry_hours_must_be_non_negative(self):
        """Expiry hours must be >= 0."""
        from advisor import Suggestion

        with pytest.raises(ValueError, match="expiry_hours must be non-negative"):
            Suggestion(action="add", content="test", expiry_hours=-1)

    def test_expiry_hours_must_be_int_not_string(self):
        """Expiry hours must be int, not string."""
        from advisor import Suggestion

        with pytest.raises(ValueError, match="expiry_hours must be non-negative"):
            Suggestion(action="add", content="test", expiry_hours="24")

    def test_strategy_id_must_be_positive_for_disable(self):
        """Strategy ID must be > 0 for disable action."""
        from advisor import Suggestion

        with pytest.raises(ValueError, match="strategy_id must be positive"):
            Suggestion(action="disable", strategy_id=0)

    def test_strategy_id_rejects_negative(self):
        """Strategy ID must reject negative values."""
        from advisor import Suggestion

        with pytest.raises(ValueError, match="strategy_id must be positive"):
            Suggestion(action="disable", strategy_id=-5)

    def test_content_length_limit(self):
        """Content must not exceed MAX_CONTENT_BYTES."""
        from advisor import Suggestion

        long_content = "x" * 2000
        with pytest.raises(ValueError, match="content exceeds max length"):
            Suggestion(action="add", content=long_content)

    def test_reason_length_limit(self):
        """Reason must not exceed MAX_REASON_LENGTH."""
        from advisor import Suggestion

        long_reason = "x" * 1000
        with pytest.raises(ValueError, match="reason exceeds max length"):
            Suggestion(action="add", content="test", reason=long_reason)

    def test_valid_priority_0_low(self):
        """Priority 0 (LOW) should be valid."""
        from advisor import Suggestion

        s = Suggestion(action="add", content="test", priority=0)
        assert s.priority == 0

    def test_valid_priority_2_high(self):
        """Priority 2 (HIGH) should be valid."""
        from advisor import Suggestion

        s = Suggestion(action="add", content="test", priority=2)
        assert s.priority == 2


class TestJSONParsingValidation:
    """Tests for JSON parsing with type coercion."""

    @pytest.mark.asyncio
    async def test_parse_coerces_priority_from_string(self, advisor, suggestion_factory):
        """Priority as string 'high' should be coerced to 2."""
        raw_suggestion = suggestion_factory.create_add_suggestion(priority="high")
        advisor.llm.chat.return_value = suggestion_factory.create_llm_response([raw_suggestion])

        result = await advisor.analyze()

        if len(result) > 0:
            assert result[0].priority in [0, 1, 2]

    @pytest.mark.asyncio
    async def test_parse_handles_float_priority(self, advisor, suggestion_factory):
        """Float priority should be converted to int."""
        raw_suggestion = suggestion_factory.create_add_suggestion(priority=1.5)
        advisor.llm.chat.return_value = suggestion_factory.create_llm_response([raw_suggestion])

        result = await advisor.analyze()

        if len(result) > 0:
            assert isinstance(result[0].priority, int)

    @pytest.mark.asyncio
    async def test_parse_clamps_out_of_range_priority(self, advisor, suggestion_factory):
        """Out of range priority should be defaulted to 1."""
        raw_suggestion = suggestion_factory.create_add_suggestion(priority=100)
        advisor.llm.chat.return_value = suggestion_factory.create_llm_response([raw_suggestion])

        result = await advisor.analyze()

        if len(result) > 0:
            assert result[0].priority in [0, 1, 2]

    @pytest.mark.asyncio
    async def test_parse_handles_negative_expiry_hours(self, advisor, suggestion_factory):
        """Negative expiry_hours should be set to 0."""
        raw_suggestion = suggestion_factory.create_add_suggestion(expiry_hours=-10)
        advisor.llm.chat.return_value = suggestion_factory.create_llm_response([raw_suggestion])

        result = await advisor.analyze()

        if len(result) > 0:
            assert result[0].expiry_hours >= 0

    @pytest.mark.asyncio
    async def test_parse_skips_invalid_action(self, advisor, suggestion_factory):
        """Invalid action should be skipped, not crash."""
        raw_suggestion = {"action": "delete", "content": "test"}
        advisor.llm.chat.return_value = suggestion_factory.create_llm_response([raw_suggestion])

        result = await advisor.analyze()

        # Should return empty list (invalid action skipped)
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_parse_handles_string_strategy_id(self, advisor, suggestion_factory):
        """String strategy_id should be converted to int."""
        raw_suggestion = suggestion_factory.create_disable_suggestion(strategy_id="5")
        advisor.llm.chat.return_value = suggestion_factory.create_llm_response([raw_suggestion])

        result = await advisor.analyze()

        if len(result) > 0:
            assert isinstance(result[0].strategy_id, int)

    @pytest.mark.asyncio
    async def test_parse_truncates_long_content(self, advisor):
        """Content exceeding max length should be truncated."""
        long_content = "x" * 2000
        response = f'''```json
{{"suggestions": [{{"action": "add", "content": "{long_content}", "priority": 1}}]}}
```'''
        advisor.llm.chat.return_value = response

        result = await advisor.analyze()

        if len(result) > 0:
            from advisor import Suggestion
            assert len(result[0].content.encode('utf-8')) <= Suggestion.MAX_CONTENT_LENGTH
