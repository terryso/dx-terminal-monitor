"""
ATDD Tests for Story 8-3: Suggestion Push & Interaction

These tests are designed to FAIL before implementation (TDD RED phase).
Run: pytest tests/unit/test_story_8_3_suggestion_push.py -v

Generated: 2026-03-04
Story: 8-3-suggestion-push
"""
import uuid
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ============================================================================
# Test Data Factory
# ============================================================================


class SuggestionPushFactory:
    """Factory for creating test data for suggestion push."""

    @staticmethod
    def create_suggestion_add(
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
    def create_suggestion_disable(
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
    def create_context(
        balance: str = "1.5 ETH ($4,500)",
        positions: int = 3,
        strategies: int = 2,
        pnl: str = "+$120.50 (+2.1%)",
        **overrides
    ) -> dict:
        """Create mock context for message formatting."""
        return {
            "balance": balance,
            "positions": positions,
            "strategies": strategies,
            "pnl": pnl,
            **overrides,
        }


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def push_factory():
    """Provide SuggestionPushFactory."""
    return SuggestionPushFactory()


@pytest.fixture
def mock_bot():
    """Create mock Telegram Bot instance."""
    bot = AsyncMock()
    bot.send_message = AsyncMock(return_value=MagicMock(message_id=123))
    bot.edit_message_reply_markup = AsyncMock()
    return bot


@pytest.fixture
def mock_llm():
    """Create mock LLMClient instance."""
    llm = AsyncMock()
    llm.chat = AsyncMock(return_value='{"suggestions": []}')
    return llm


@pytest.fixture
def mock_api():
    """Create mock TerminalAPI instance."""
    api = AsyncMock()
    api.get_positions = AsyncMock(return_value={"ethBalance": "1.5"})
    api.get_strategies = AsyncMock(return_value=[])
    api.get_vault = AsyncMock(return_value={"paused": False})
    api.get_eth_price = AsyncMock(return_value={"price": 3000})
    api.get_tokens = AsyncMock(return_value=[])
    api.get_candles = AsyncMock(return_value=[])
    return api


@pytest.fixture
def mock_contract():
    """Create mock contract instance."""
    contract = AsyncMock()
    contract.add_strategy = AsyncMock(return_value={
        "success": True,
        "transactionHash": "0xabc123def456",
        "strategyId": 1
    })
    contract.disable_strategy = AsyncMock(return_value={
        "success": True,
        "transactionHash": "0xdef456abc123"
    })
    return contract


# ============================================================================
# Test Classes - AC1: format_suggestions_message()
# ============================================================================


class TestFormatSuggestionsMessage:
    """Tests for format_suggestions_message() function (AC1, AC5)."""

    def test_format_function_exists(self):
        """format_suggestions_message() should exist in advisor_monitor module."""
        # GIVEN: advisor_monitor module
        # WHEN: Importing format_suggestions_message
        # THEN: Function should be importable
        from advisor_monitor import format_suggestions_message

        assert format_suggestions_message is not None
        assert callable(format_suggestions_message)

    def test_format_accepts_suggestions_and_context(self, push_factory):
        """format_suggestions_message() should accept suggestions list and context dict."""
        from advisor_monitor import format_suggestions_message

        # Should not raise exception
        suggestions = [
            push_factory.create_suggestion_add(),
        ]
        context = push_factory.create_context()

        result = format_suggestions_message(suggestions, context)
        assert isinstance(result, str)

    def test_format_includes_analysis_time(self, push_factory):
        """Message should include analysis time in YYYY-MM-DD HH:MM format."""
        from advisor_monitor import format_suggestions_message

        suggestions = [push_factory.create_suggestion_add()]
        context = push_factory.create_context()

        result = format_suggestions_message(suggestions, context)

        assert "Analysis Time:" in result

    def test_format_includes_current_status(self, push_factory):
        """Message should include current status section with balance, positions, strategies, PnL."""
        from advisor_monitor import format_suggestions_message

        suggestions = [push_factory.create_suggestion_add()]
        context = push_factory.create_context(
            balance="1.5 ETH ($4,500)",
            positions=3,
            strategies=2,
            pnl="+$120.50 (+2.1%)",
        )

        result = format_suggestions_message(suggestions, context)

        assert "Current Status:" in result
        assert "Balance:" in result
        assert "Positions:" in result
        assert "Active Strategies:" in result
        assert "Total PnL:" in result

    def test_format_includes_balance_value(self, push_factory):
        """Message should display balance value from context."""
        from advisor_monitor import format_suggestions_message

        suggestions = [push_factory.create_suggestion_add()]
        context = push_factory.create_context(balance="2.5 ETH ($7,500)")

        result = format_suggestions_message(suggestions, context)

        assert "2.5 ETH" in result

    def test_format_includes_positions_count(self, push_factory):
        """Message should display positions count from context."""
        from advisor_monitor import format_suggestions_message

        suggestions = [push_factory.create_suggestion_add()]
        context = push_factory.create_context(positions=5)

        result = format_suggestions_message(suggestions, context)

        assert "5 tokens" in result

    def test_format_includes_strategies_count(self, push_factory):
        """Message should display active strategies count from context."""
        from advisor_monitor import format_suggestions_message

        suggestions = [push_factory.create_suggestion_add()]
        context = push_factory.create_context(strategies=3)

        result = format_suggestions_message(suggestions, context)

        assert "3" in result

    def test_format_includes_pnl_value(self, push_factory):
        """Message should display PnL value from context."""
        from advisor_monitor import format_suggestions_message

        suggestions = [push_factory.create_suggestion_add()]
        context = push_factory.create_context(pnl="+$200.00 (+5.0%)")

        result = format_suggestions_message(suggestions, context)

        assert "+$200.00" in result

    def test_format_add_suggestion(self, push_factory):
        """Message should format add suggestion with icon, content, priority, validity, reason."""
        from advisor_monitor import format_suggestions_message

        suggestions = [push_factory.create_suggestion_add(
            content="When BTC breaks 70000, sell 50% of ETH position",
            priority=2,
            expiry_hours=24,
            reason="BTC breaking key resistance may trigger market correction",
        )]
        context = push_factory.create_context()

        result = format_suggestions_message(suggestions, context)

        assert "ADD" in result or "[ADD]" in result
        assert "STRATEGY" in result
        assert "When BTC breaks 70000" in result
        assert "HIGH" in result or "Priority:" in result
        assert "24" in result or "24h" in result
        assert "BTC breaking key resistance" in result

    def test_format_disable_suggestion(self, push_factory):
        """Message should format disable suggestion with icon and reason."""
        from advisor_monitor import format_suggestions_message

        suggestions = [push_factory.create_suggestion_disable(
            strategy_id=3,
            reason="Strategy condition has become invalid",
        )]
        context = push_factory.create_context()

        result = format_suggestions_message(suggestions, context)

        assert "DISABLE" in result or "[DISABLE]" in result
        assert "STRATEGY" in result
        assert "#3" in result or "3" in result
        assert "Strategy condition has become invalid" in result

    def test_format_multiple_suggestions(self, push_factory):
        """Message should format multiple suggestions with numbered indices."""
        from advisor_monitor import format_suggestions_message

        suggestions = [
            push_factory.create_suggestion_add(content="Add strategy 1"),
            push_factory.create_suggestion_disable(strategy_id=2),
        ]
        context = push_factory.create_context()

        result = format_suggestions_message(suggestions, context)

        assert "[1]" in result or "1" in result
        assert "[2]" in result or "2" in result
        assert "Add strategy 1" in result

    def test_format_uses_html_for_formatting(self, push_factory):
        """Message should use HTML tags for formatting (bold, etc.)."""
        from advisor_monitor import format_suggestions_message

        suggestions = [push_factory.create_suggestion_add()]
        context = push_factory.create_context()

        result = format_suggestions_message(suggestions, context)

        # Should contain HTML tags
        assert "<b>" in result or "<i>" in result


# ============================================================================
# Test Classes - AC2: build_suggestion_keyboard()
# ============================================================================


class TestBuildSuggestionKeyboard:
    """Tests for build_suggestion_keyboard() function (AC2, AC4)."""

    def test_build_keyboard_function_exists(self):
        """build_suggestion_keyboard() should exist in advisor_monitor module."""
        from advisor_monitor import build_suggestion_keyboard

        assert build_suggestion_keyboard is not None
        assert callable(build_suggestion_keyboard)

    def test_build_keyboard_accepts_suggestions_and_request_id(self, push_factory):
        """build_suggestion_keyboard() should accept suggestions list and request_id string."""
        from advisor_monitor import build_suggestion_keyboard

        suggestions = [push_factory.create_suggestion_add()]
        request_id = "a3f2b1cd"

        result = build_suggestion_keyboard(suggestions, request_id)
        assert result is not None

    def test_build_keyboard_returns_inline_keyboard_markup(self, push_factory):
        """build_suggestion_keyboard() should return InlineKeyboardMarkup."""
        from telegram import InlineKeyboardMarkup

        from advisor_monitor import build_suggestion_keyboard

        suggestions = [push_factory.create_suggestion_add()]
        request_id = "a3f2b1cd"

        result = build_suggestion_keyboard(suggestions, request_id)

        assert isinstance(result, InlineKeyboardMarkup)

    def test_build_keyboard_creates_individual_execute_buttons(self, push_factory):
        """Keyboard should have individual execute buttons for each suggestion."""
        from advisor_monitor import build_suggestion_keyboard

        suggestions = [
            push_factory.create_suggestion_add(),
            push_factory.create_suggestion_disable(strategy_id=2),
        ]
        request_id = "a3f2b1cd"

        result = build_suggestion_keyboard(suggestions, request_id)

        # First row should have buttons for each suggestion
        assert len(result.inline_keyboard) >= 1
        first_row = result.inline_keyboard[0]
        assert len(first_row) == 2  # Two suggestions = two buttons

    def test_build_keyboard_creates_execute_all_button(self, push_factory):
        """Keyboard should have Execute All button."""
        from advisor_monitor import build_suggestion_keyboard

        suggestions = [push_factory.create_suggestion_add()]
        request_id = "a3f2b1cd"

        result = build_suggestion_keyboard(suggestions, request_id)

        # Find Execute All button
        all_buttons = [btn for row in result.inline_keyboard for btn in row]
        execute_all_found = any("Execute All" in btn.text for btn in all_buttons)
        assert execute_all_found

    def test_build_keyboard_creates_ignore_button(self, push_factory):
        """Keyboard should have Ignore button."""
        from advisor_monitor import build_suggestion_keyboard

        suggestions = [push_factory.create_suggestion_add()]
        request_id = "a3f2b1cd"

        result = build_suggestion_keyboard(suggestions, request_id)

        # Find Ignore button
        all_buttons = [btn for row in result.inline_keyboard for btn in row]
        ignore_found = any("Ignore" in btn.text for btn in all_buttons)
        assert ignore_found

    def test_build_keyboard_callback_data_format(self, push_factory):
        """Callback data should follow adv:{request_id}:{choice} format."""
        from advisor_monitor import build_suggestion_keyboard

        suggestions = [push_factory.create_suggestion_add()]
        request_id = "a3f2b1cd"

        result = build_suggestion_keyboard(suggestions, request_id)

        all_buttons = [btn for row in result.inline_keyboard for btn in row]

        # At least one button should have callback_data starting with "adv:"
        callback_data_found = any(
            btn.callback_data.startswith(f"adv:{request_id}:")
            for btn in all_buttons
        )
        assert callback_data_found

    def test_build_keyboard_single_suggestion_callback(self, push_factory):
        """Single suggestion execute button should have callback adv:{id}:{n}."""
        from advisor_monitor import build_suggestion_keyboard

        suggestions = [push_factory.create_suggestion_add()]
        request_id = "a3f2b1cd"

        result = build_suggestion_keyboard(suggestions, request_id)

        first_row = result.inline_keyboard[0]
        first_button = first_row[0]

        assert first_button.callback_data == f"adv:{request_id}:1"

    def test_build_keyboard_execute_all_callback(self, push_factory):
        """Execute All button should have callback adv:{id}:all."""
        from advisor_monitor import build_suggestion_keyboard

        suggestions = [push_factory.create_suggestion_add()]
        request_id = "a3f2b1cd"

        result = build_suggestion_keyboard(suggestions, request_id)

        all_buttons = [btn for row in result.inline_keyboard for btn in row]
        execute_all_btn = next(btn for btn in all_buttons if "Execute All" in btn.text)

        assert execute_all_btn.callback_data == f"adv:{request_id}:all"

    def test_build_keyboard_ignore_callback(self, push_factory):
        """Ignore button should have callback adv:{id}:ignore."""
        from advisor_monitor import build_suggestion_keyboard

        suggestions = [push_factory.create_suggestion_add()]
        request_id = "a3f2b1cd"

        result = build_suggestion_keyboard(suggestions, request_id)

        all_buttons = [btn for row in result.inline_keyboard for btn in row]
        ignore_btn = next(btn for btn in all_buttons if "Ignore" in btn.text)

        assert ignore_btn.callback_data == f"adv:{request_id}:ignore"


# ============================================================================
# Test Classes - AC3: AdvisorMonitor Class
# ============================================================================


class TestAdvisorMonitorClass:
    """Tests for AdvisorMonitor class (AC3)."""

    def test_advisor_monitor_class_exists(self):
        """AdvisorMonitor class should be defined in advisor_monitor module."""
        from advisor_monitor import AdvisorMonitor

        assert AdvisorMonitor is not None

    def test_advisor_monitor_accepts_advisor_and_api(self, mock_llm, mock_api):
        """AdvisorMonitor should accept StrategyAdvisor, TerminalAPI in constructor."""
        from advisor import StrategyAdvisor
        from advisor_monitor import AdvisorMonitor

        advisor = StrategyAdvisor(mock_llm, mock_api)
        callback = AsyncMock()

        monitor = AdvisorMonitor(advisor, mock_api, callback, admin_chat_id=123456789, bot=MagicMock())
        assert monitor.advisor is advisor
        assert monitor.api is mock_api

    def test_advisor_monitor_accepts_callback(self, mock_llm, mock_api):
        """AdvisorMonitor should accept callback function in constructor."""
        from advisor import StrategyAdvisor
        from advisor_monitor import AdvisorMonitor

        advisor = StrategyAdvisor(mock_llm, mock_api)
        callback = AsyncMock()

        monitor = AdvisorMonitor(advisor, mock_api, callback, admin_chat_id=123456789, bot=MagicMock())
        assert monitor.callback is callback

    def test_advisor_monitor_accepts_admin_chat_id(self, mock_llm, mock_api):
        """AdvisorMonitor should accept admin_chat_id in constructor."""
        from advisor import StrategyAdvisor
        from advisor_monitor import AdvisorMonitor

        advisor = StrategyAdvisor(mock_llm, mock_api)
        callback = AsyncMock()

        monitor = AdvisorMonitor(advisor, mock_api, callback, admin_chat_id=123456789, bot=MagicMock())
        assert monitor.admin_chat_id == 123456789

    def test_advisor_monitor_has_interval_hours_config(self, mock_llm, mock_api):
        """AdvisorMonitor should accept interval_hours parameter."""
        from advisor import StrategyAdvisor
        from advisor_monitor import AdvisorMonitor

        advisor = StrategyAdvisor(mock_llm, mock_api)
        callback = AsyncMock()

        monitor = AdvisorMonitor(
            advisor, mock_api, callback,
            admin_chat_id=123456789,
            bot=MagicMock(),
            interval_hours=4
        )
        assert monitor.interval_seconds == 4 * 3600

    def test_advisor_monitor_default_interval_is_2_hours(self, mock_llm, mock_api):
        """AdvisorMonitor should default to 2 hours interval."""
        from advisor import StrategyAdvisor
        from advisor_monitor import AdvisorMonitor

        advisor = StrategyAdvisor(mock_llm, mock_api)
        callback = AsyncMock()

        monitor = AdvisorMonitor(advisor, mock_api, callback, admin_chat_id=123456789, bot=MagicMock())
        assert monitor.interval_seconds == 2 * 3600

    def test_advisor_monitor_has_start_method(self, mock_llm, mock_api):
        """AdvisorMonitor should have start() method."""
        from advisor import StrategyAdvisor
        from advisor_monitor import AdvisorMonitor

        advisor = StrategyAdvisor(mock_llm, mock_api)
        callback = AsyncMock()

        monitor = AdvisorMonitor(advisor, mock_api, callback, admin_chat_id=123456789, bot=MagicMock())
        assert hasattr(monitor, "start")
        assert callable(monitor.start)

    def test_advisor_monitor_has_stop_method(self, mock_llm, mock_api):
        """AdvisorMonitor should have stop() method."""
        from advisor import StrategyAdvisor
        from advisor_monitor import AdvisorMonitor

        advisor = StrategyAdvisor(mock_llm, mock_api)
        callback = AsyncMock()

        monitor = AdvisorMonitor(advisor, mock_api, callback, admin_chat_id=123456789, bot=MagicMock())
        assert hasattr(monitor, "stop")
        assert callable(monitor.stop)

    def test_advisor_monitor_has_start_background_method(self, mock_llm, mock_api):
        """AdvisorMonitor should have start_background() method."""
        from advisor import StrategyAdvisor
        from advisor_monitor import AdvisorMonitor

        advisor = StrategyAdvisor(mock_llm, mock_api)
        callback = AsyncMock()

        monitor = AdvisorMonitor(advisor, mock_api, callback, admin_chat_id=123456789, bot=MagicMock())
        assert hasattr(monitor, "start_background")
        assert callable(monitor.start_background)

    def test_advisor_monitor_has_running_flag(self, mock_llm, mock_api):
        """AdvisorMonitor should have running flag."""
        from advisor import StrategyAdvisor
        from advisor_monitor import AdvisorMonitor

        advisor = StrategyAdvisor(mock_llm, mock_api)
        callback = AsyncMock()

        monitor = AdvisorMonitor(advisor, mock_api, callback, admin_chat_id=123456789, bot=MagicMock())
        assert hasattr(monitor, "running")
        assert monitor.running is False

    def test_advisor_monitor_has_last_analysis_tracking(self, mock_llm, mock_api):
        """AdvisorMonitor should track last_analysis time."""
        from advisor import StrategyAdvisor
        from advisor_monitor import AdvisorMonitor

        advisor = StrategyAdvisor(mock_llm, mock_api)
        callback = AsyncMock()

        monitor = AdvisorMonitor(advisor, mock_api, callback, admin_chat_id=123456789, bot=MagicMock())
        assert hasattr(monitor, "last_analysis")


class TestAdvisorMonitorAsync:
    """Tests for AdvisorMonitor async methods (AC3)."""

    @pytest.mark.asyncio
    async def test_start_is_async(self, mock_llm, mock_api):
        """start() should be an async method."""
        import inspect

        from advisor import StrategyAdvisor
        from advisor_monitor import AdvisorMonitor

        advisor = StrategyAdvisor(mock_llm, mock_api)
        callback = AsyncMock()

        monitor = AdvisorMonitor(advisor, mock_api, callback, admin_chat_id=123456789, bot=MagicMock())
        assert inspect.iscoroutinefunction(monitor.start)

    @pytest.mark.asyncio
    async def test_start_background_returns_task(self, mock_llm, mock_api):
        """start_background() should return asyncio.Task."""
        import asyncio

        from advisor import StrategyAdvisor
        from advisor_monitor import AdvisorMonitor

        advisor = StrategyAdvisor(mock_llm, mock_api)
        callback = AsyncMock()

        monitor = AdvisorMonitor(advisor, mock_api, callback, admin_chat_id=123456789, bot=MagicMock())

        task = await monitor.start_background()
        assert isinstance(task, asyncio.Task)

        # Clean up
        monitor.stop()
        task.cancel()

    @pytest.mark.asyncio
    async def test_stop_sets_running_to_false(self, mock_llm, mock_api):
        """stop() should set running flag to False."""
        from advisor import StrategyAdvisor
        from advisor_monitor import AdvisorMonitor

        advisor = StrategyAdvisor(mock_llm, mock_api)
        callback = AsyncMock()

        monitor = AdvisorMonitor(advisor, mock_api, callback, admin_chat_id=123456789, bot=MagicMock())
        monitor.running = True

        monitor.stop()
        assert monitor.running is False


# ============================================================================
# Test Classes - AC4: UUID Generation
# ============================================================================


class TestUUIDGeneration:
    """Tests for unique request_id generation (AC4)."""

    def test_uuid_generation_exists(self):
        """push_suggestions() should generate UUID for request_id."""
        from advisor_monitor import push_suggestions

        assert push_suggestions is not None

    @pytest.mark.asyncio
    async def test_push_suggestions_generates_short_uuid(self, mock_bot, push_factory):
        """push_suggestions() should generate 8-character hex UUID."""
        from advisor_monitor import push_suggestions

        suggestions = [push_factory.create_suggestion_add()]
        context = push_factory.create_context()

        request_id = await push_suggestions(123456789, suggestions, context, mock_bot)

        assert request_id is not None
        assert len(request_id) == 8
        # Should be hex characters only
        assert all(c in "0123456789abcdef" for c in request_id)

    @pytest.mark.asyncio
    async def test_push_suggestions_unique_ids(self, mock_bot, push_factory):
        """push_suggestions() should generate unique IDs for each call."""
        from advisor_monitor import push_suggestions

        suggestions = [push_factory.create_suggestion_add()]
        context = push_factory.create_context()

        id1 = await push_suggestions(123456789, suggestions, context, mock_bot)
        id2 = await push_suggestions(123456789, suggestions, context, mock_bot)

        assert id1 != id2


# ============================================================================
# Test Classes - AC5: push_suggestions()
# ============================================================================


class TestPushSuggestions:
    """Tests for push_suggestions() function (AC3, AC5)."""

    @pytest.mark.asyncio
    async def test_push_suggestions_function_exists(self):
        """push_suggestions() should exist in advisor_monitor module."""
        from advisor_monitor import push_suggestions

        assert push_suggestions is not None
        assert callable(push_suggestions)

    @pytest.mark.asyncio
    async def test_push_suggestions_accepts_chat_id(self, mock_bot, push_factory):
        """push_suggestions() should accept chat_id as first parameter."""
        from advisor_monitor import push_suggestions

        suggestions = [push_factory.create_suggestion_add()]
        context = push_factory.create_context()

        # Should not raise exception
        await push_suggestions(123456789, suggestions, context, mock_bot)

    @pytest.mark.asyncio
    async def test_push_suggestions_accepts_suggestions_list(self, mock_bot, push_factory):
        """push_suggestions() should accept suggestions list."""
        from advisor_monitor import push_suggestions

        suggestions = [
            push_factory.create_suggestion_add(),
            push_factory.create_suggestion_disable(strategy_id=2),
        ]
        context = push_factory.create_context()

        await push_suggestions(123456789, suggestions, context, mock_bot)

    @pytest.mark.asyncio
    async def test_push_suggestions_accepts_context_dict(self, mock_bot, push_factory):
        """push_suggestions() should accept context dict."""
        from advisor_monitor import push_suggestions

        suggestions = [push_factory.create_suggestion_add()]
        context = push_factory.create_context(
            balance="2.0 ETH",
            positions=5,
            strategies=3,
            pnl="+$500",
        )

        await push_suggestions(123456789, suggestions, context, mock_bot)

    @pytest.mark.asyncio
    async def test_push_suggestions_accepts_bot_instance(self, mock_bot, push_factory):
        """push_suggestions() should accept Bot instance."""
        from advisor_monitor import push_suggestions

        suggestions = [push_factory.create_suggestion_add()]
        context = push_factory.create_context()

        await push_suggestions(123456789, suggestions, context, mock_bot)

    @pytest.mark.asyncio
    async def test_push_suggestions_calls_bot_send_message(self, mock_bot, push_factory):
        """push_suggestions() should call bot.send_message()."""
        from advisor_monitor import push_suggestions

        suggestions = [push_factory.create_suggestion_add()]
        context = push_factory.create_context()

        await push_suggestions(123456789, suggestions, context, mock_bot)

        mock_bot.send_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_push_suggestions_includes_reply_markup(self, mock_bot, push_factory):
        """push_suggestions() should include reply_markup with inline keyboard."""
        from telegram import InlineKeyboardMarkup

        from advisor_monitor import push_suggestions

        suggestions = [push_factory.create_suggestion_add()]
        context = push_factory.create_context()

        await push_suggestions(123456789, suggestions, context, mock_bot)

        call_kwargs = mock_bot.send_message.call_args[1]
        assert "reply_markup" in call_kwargs
        assert isinstance(call_kwargs["reply_markup"], InlineKeyboardMarkup)

    @pytest.mark.asyncio
    async def test_push_suggestions_uses_html_parse_mode(self, mock_bot, push_factory):
        """push_suggestions() should use HTML parse_mode."""
        from advisor_monitor import push_suggestions

        suggestions = [push_factory.create_suggestion_add()]
        context = push_factory.create_context()

        await push_suggestions(123456789, suggestions, context, mock_bot)

        call_kwargs = mock_bot.send_message.call_args[1]
        assert call_kwargs.get("parse_mode") == "HTML"

    @pytest.mark.asyncio
    async def test_push_suggestions_stores_pending_request(self, mock_bot, push_factory):
        """push_suggestions() should store pending request in pending_requests dict."""
        from advisor_monitor import pending_requests, push_suggestions

        # Clear any existing pending requests
        pending_requests.clear()

        suggestions = [push_factory.create_suggestion_add()]
        context = push_factory.create_context()

        request_id = await push_suggestions(123456789, suggestions, context, mock_bot)

        assert request_id in pending_requests
        assert "suggestions" in pending_requests[request_id]
        assert "created_at" in pending_requests[request_id]
        assert "context" in pending_requests[request_id]


# ============================================================================
# Test Classes - AC6: Callback Query Handler
# ============================================================================


class TestCallbackQueryHandler:
    """Tests for handle_advisor_callback() function (AC6)."""

    def test_callback_handler_exists(self):
        """handle_advisor_callback() should exist in advisor_monitor module."""
        from advisor_monitor import handle_advisor_callback

        assert handle_advisor_callback is not None
        assert callable(handle_advisor_callback)

    @pytest.mark.asyncio
    async def test_callback_handler_parses_callback_data(self, mock_bot, push_factory):
        """handle_advisor_callback() should parse callback_data to extract request_id and choice."""
        from advisor_monitor import handle_advisor_callback, pending_requests

        # Set up pending request
        request_id = "a3f2b1cd"
        pending_requests[request_id] = {
            "suggestions": [push_factory.create_suggestion_add()],
            "created_at": datetime.now(),
            "context": push_factory.create_context(),
            "executed": False,
        }

        # Create mock update with callback query
        update = MagicMock()
        update.callback_query = MagicMock()
        update.callback_query.data = f"adv:{request_id}:1"
        update.callback_query.message = MagicMock()
        update.callback_query.message.chat_id = 123456789
        update.callback_query.message.message_id = 123
        update.callback_query.answer = AsyncMock()
        update.callback_query.edit_message_text = AsyncMock()
        update.callback_query.edit_message_reply_markup = AsyncMock()
        update.effective_user = MagicMock()
        update.effective_user.id = 123456789

        context = MagicMock()
        context.bot = mock_bot

        with patch("advisor_monitor.execute_suggestion") as mock_execute:
            mock_execute.return_value = "Executed successfully"
            await handle_advisor_callback(update, context)

        # Should have processed the callback
        pending_requests.pop(request_id, None)

    @pytest.mark.asyncio
    async def test_callback_handler_validates_request_exists(self, mock_bot):
        """handle_advisor_callback() should validate request exists."""
        from advisor_monitor import handle_advisor_callback

        # Create mock update with non-existent request
        update = MagicMock()
        update.callback_query = MagicMock()
        update.callback_query.data = "adv:nonexist:1"
        update.callback_query.message = MagicMock()
        update.callback_query.answer = AsyncMock()
        update.callback_query.edit_message_text = AsyncMock()
        update.effective_user = MagicMock()
        update.effective_user.id = 123456789

        context = MagicMock()
        context.bot = mock_bot

        await handle_advisor_callback(update, context)

        # Should have answered callback (even if expired)
        update.callback_query.answer.assert_called()

    @pytest.mark.asyncio
    async def test_callback_handler_validates_request_not_expired(self, mock_bot, push_factory):
        """handle_advisor_callback() should reject expired requests (30 min TTL)."""
        from advisor_monitor import SUGGESTION_TTL, handle_advisor_callback, pending_requests

        # Set up expired pending request
        request_id = "expired01"
        pending_requests[request_id] = {
            "suggestions": [push_factory.create_suggestion_add()],
            "created_at": datetime.now() - timedelta(minutes=31),  # Expired
            "context": push_factory.create_context(),
            "executed": False,
        }

        update = MagicMock()
        update.callback_query = MagicMock()
        update.callback_query.data = f"adv:{request_id}:1"
        update.callback_query.message = MagicMock()
        update.callback_query.answer = AsyncMock()
        update.callback_query.edit_message_text = AsyncMock()
        update.callback_query.edit_message_reply_markup = AsyncMock()
        update.effective_user = MagicMock()
        update.effective_user.id = 123456789

        context = MagicMock()
        context.bot = mock_bot

        await handle_advisor_callback(update, context)

        # Should indicate expired
        pending_requests.pop(request_id, None)

    @pytest.mark.asyncio
    async def test_callback_handler_checks_admin_permission(self, mock_bot, push_factory):
        """handle_advisor_callback() should check admin permission via is_admin()."""
        from advisor_monitor import handle_advisor_callback, pending_requests

        # Set up pending request
        request_id = "a3f2b1cd"
        pending_requests[request_id] = {
            "suggestions": [push_factory.create_suggestion_add()],
            "created_at": datetime.now(),
            "context": push_factory.create_context(),
            "executed": False,
        }

        # Create mock update with non-admin user
        update = MagicMock()
        update.callback_query = MagicMock()
        update.callback_query.data = f"adv:{request_id}:1"
        update.callback_query.message = MagicMock()
        update.callback_query.answer = AsyncMock()
        update.callback_query.edit_message_text = AsyncMock()
        update.effective_user = MagicMock()
        update.effective_user.id = 999999999  # Non-admin

        context = MagicMock()
        context.bot = mock_bot

        await handle_advisor_callback(update, context)

        # Should have answered callback (unauthorized)
        update.callback_query.answer.assert_called()
        pending_requests.pop(request_id, None)

    @pytest.mark.asyncio
    async def test_callback_handler_prevents_duplicate_execution(self, mock_bot, push_factory):
        """handle_advisor_callback() should prevent duplicate execution."""
        from advisor_monitor import handle_advisor_callback, pending_requests

        # Set up already executed request
        request_id = "a3f2b1cd"
        pending_requests[request_id] = {
            "suggestions": [push_factory.create_suggestion_add()],
            "created_at": datetime.now(),
            "context": push_factory.create_context(),
            "executed": True,  # Already executed
        }

        update = MagicMock()
        update.callback_query = MagicMock()
        update.callback_query.data = f"adv:{request_id}:1"
        update.callback_query.message = MagicMock()
        update.callback_query.answer = AsyncMock()
        update.callback_query.edit_message_text = AsyncMock()
        update.effective_user = MagicMock()
        update.effective_user.id = 123456789

        context = MagicMock()
        context.bot = mock_bot

        await handle_advisor_callback(update, context)

        # Should have answered callback (already executed)
        update.callback_query.answer.assert_called()
        pending_requests.pop(request_id, None)

    @pytest.mark.asyncio
    async def test_callback_handler_handles_ignore_choice(self, mock_bot, push_factory):
        """handle_advisor_callback() should handle 'ignore' choice."""
        from advisor_monitor import handle_advisor_callback, pending_requests

        request_id = "a3f2b1cd"
        pending_requests[request_id] = {
            "suggestions": [push_factory.create_suggestion_add()],
            "created_at": datetime.now(),
            "context": push_factory.create_context(),
            "executed": False,
        }

        update = MagicMock()
        update.callback_query = MagicMock()
        update.callback_query.data = f"adv:{request_id}:ignore"
        update.callback_query.message = MagicMock()
        update.callback_query.message.chat_id = 123456789
        update.callback_query.message.message_id = 123
        update.callback_query.message.text = "Original message"
        update.callback_query.answer = AsyncMock()
        update.callback_query.edit_message_reply_markup = AsyncMock()
        update.callback_query.edit_message_text = AsyncMock()
        update.effective_user = MagicMock()
        update.effective_user.id = 123456789

        context = MagicMock()
        context.bot = mock_bot

        await handle_advisor_callback(update, context)

        # Should edit message text with "Ignored" (not reply_markup)
        update.callback_query.edit_message_text.assert_called()
        pending_requests.pop(request_id, None)

    @pytest.mark.asyncio
    async def test_callback_handler_handles_all_choice(self, mock_bot, push_factory):
        """handle_advisor_callback() should handle 'all' choice to execute all suggestions."""
        from advisor_monitor import handle_advisor_callback, pending_requests

        request_id = "a3f2b1cd"
        pending_requests[request_id] = {
            "suggestions": [
                push_factory.create_suggestion_add(),
                push_factory.create_suggestion_disable(strategy_id=2),
            ],
            "created_at": datetime.now(),
            "context": push_factory.create_context(),
            "executed": False,
        }

        update = MagicMock()
        update.callback_query = MagicMock()
        update.callback_query.data = f"adv:{request_id}:all"
        update.callback_query.message = MagicMock()
        update.callback_query.message.chat_id = 123456789
        update.callback_query.message.message_id = 123
        update.callback_query.answer = AsyncMock()
        update.callback_query.edit_message_text = AsyncMock()
        update.effective_user = MagicMock()
        update.effective_user.id = 123456789

        context = MagicMock()
        context.bot = mock_bot

        with patch("advisor_monitor.execute_suggestion") as mock_execute:
            mock_execute.return_value = "Executed successfully"

            await handle_advisor_callback(update, context)

        pending_requests.pop(request_id, None)


# ============================================================================
# Test Classes - AC6: execute_suggestion()
# ============================================================================


class TestExecuteSuggestion:
    """Tests for execute_suggestion() function (AC6)."""

    def test_execute_suggestion_exists(self):
        """execute_suggestion() should exist in advisor_monitor module."""
        from advisor_monitor import execute_suggestion

        assert execute_suggestion is not None
        assert callable(execute_suggestion)

    @pytest.mark.asyncio
    async def test_execute_suggestion_is_async(self):
        """execute_suggestion() should be an async function."""
        import inspect

        from advisor_monitor import execute_suggestion

        assert inspect.iscoroutinefunction(execute_suggestion)

    @pytest.mark.asyncio
    async def test_execute_add_suggestion_calls_contract(self, push_factory, mock_contract):
        """execute_suggestion() should call contract.add_strategy() for add action."""
        from advisor import Suggestion
        from advisor_monitor import execute_suggestion

        suggestion = Suggestion(
            action="add",
            content="Test strategy",
            priority=1,
            expiry_hours=24,
            reason="Test reason",
        )

        with patch("main.get_contract", return_value=mock_contract):
            result = await execute_suggestion(suggestion)

        mock_contract.add_strategy.assert_called_once()
        assert "Executed" in result or "Success" in result or "0x" in result or "Strategy" in result

    @pytest.mark.asyncio
    async def test_execute_disable_suggestion_calls_contract(self, push_factory, mock_contract):
        """execute_suggestion() should call contract.disable_strategy() for disable action."""
        from advisor import Suggestion
        from advisor_monitor import execute_suggestion

        suggestion = Suggestion(
            action="disable",
            strategy_id=3,
            reason="Test reason",
        )

        with patch("main.get_contract", return_value=mock_contract):
            result = await execute_suggestion(suggestion)

        mock_contract.disable_strategy.assert_called_once()
        assert "Executed" in result or "Success" in result or "0x" in result or "disabled" in result

    @pytest.mark.asyncio
    async def test_execute_suggestion_returns_result_string(self, push_factory, mock_contract):
        """execute_suggestion() should return formatted result string."""
        from advisor import Suggestion
        from advisor_monitor import execute_suggestion

        suggestion = Suggestion(
            action="add",
            content="Test strategy",
            priority=1,
            expiry_hours=24,
            reason="Test reason",
        )

        with patch("main.get_contract", return_value=mock_contract):
            result = await execute_suggestion(suggestion)

        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_execute_suggestion_handles_errors(self, push_factory, mock_contract):
        """execute_suggestion() should handle errors gracefully."""
        from advisor import Suggestion
        from advisor_monitor import execute_suggestion

        mock_contract.add_strategy.side_effect = Exception("Contract error")

        suggestion = Suggestion(
            action="add",
            content="Test strategy",
            priority=1,
            expiry_hours=24,
            reason="Test reason",
        )

        with patch("main.get_contract", return_value=mock_contract):
            result = await execute_suggestion(suggestion)

        # Should return error message, not raise exception
        assert isinstance(result, str)
        assert "Error" in result or "error" in result or "Failed" in result


# ============================================================================
# Test Classes - AC7: Control Commands
# ============================================================================


class TestControlCommands:
    """Tests for control commands (AC7)."""

    def test_cmd_advisor_on_exists(self):
        """cmd_advisor_on() should exist in commands/advisor module."""
        from commands.advisor import cmd_advisor_on

        assert cmd_advisor_on is not None
        assert callable(cmd_advisor_on)

    def test_cmd_advisor_off_exists(self):
        """cmd_advisor_off() should exist in commands/advisor module."""
        from commands.advisor import cmd_advisor_off

        assert cmd_advisor_off is not None
        assert callable(cmd_advisor_off)

    def test_cmd_advisor_status_exists(self):
        """cmd_advisor_status() should exist in commands/advisor module."""
        from commands.advisor import cmd_advisor_status

        assert cmd_advisor_status is not None
        assert callable(cmd_advisor_status)

    @pytest.mark.asyncio
    async def test_advisor_on_is_async(self):
        """cmd_advisor_on() should be an async function."""
        import inspect

        from commands.advisor import cmd_advisor_on

        assert inspect.iscoroutinefunction(cmd_advisor_on)

    @pytest.mark.asyncio
    async def test_advisor_off_is_async(self):
        """cmd_advisor_off() should be an async function."""
        import inspect

        from commands.advisor import cmd_advisor_off

        assert inspect.iscoroutinefunction(cmd_advisor_off)

    @pytest.mark.asyncio
    async def test_advisor_status_is_async(self):
        """cmd_advisor_status() should be an async function."""
        import inspect

        from commands.advisor import cmd_advisor_status

        assert inspect.iscoroutinefunction(cmd_advisor_status)

    @pytest.mark.asyncio
    async def test_advisor_on_starts_monitor(self, mock_telegram_update, mock_telegram_context):
        """cmd_advisor_on() should start the advisor monitor."""
        import os
        import sys
        # Add project root to path if needed
        if os.getcwd() not in sys.path:
            sys.path.insert(0, os.getcwd())
        from commands import advisor as advisor_module

        # Create mock monitor
        mock_monitor = MagicMock()
        mock_monitor.running = False
        mock_monitor.start_background = AsyncMock(return_value=AsyncMock())

        # Set directly on the module
        advisor_module._advisor_monitor = mock_monitor

        with patch("commands.advisor.is_admin", return_value=True):
            await advisor_module.cmd_advisor_on(mock_telegram_update, mock_telegram_context)

        mock_monitor.start_background.assert_called_once()

    @pytest.mark.asyncio
    async def test_advisor_off_stops_monitor(self, mock_telegram_update, mock_telegram_context):
        """cmd_advisor_off() should stop the advisor monitor."""
        import os
        import sys
        # Add project root to path if needed
        if os.getcwd() not in sys.path:
            sys.path.insert(0, os.getcwd())
        from commands import advisor as advisor_module

        # Create mock monitor
        mock_monitor = MagicMock()
        mock_monitor.running = True
        mock_monitor.stop = MagicMock()

        # Set directly on the module
        advisor_module._advisor_monitor = mock_monitor

        with patch("commands.advisor.is_admin", return_value=True):
            await advisor_module.cmd_advisor_off(mock_telegram_update, mock_telegram_context)

        mock_monitor.stop.assert_called_once()

    @pytest.mark.asyncio
    async def test_advisor_status_reports_status(self, mock_telegram_update, mock_telegram_context):
        """cmd_advisor_status() should report monitor status."""
        from commands.advisor import cmd_advisor_status, set_advisor_monitor

        # Create mock monitor
        mock_monitor = MagicMock()
        mock_monitor.running = True
        mock_monitor.interval_seconds = 7200
        mock_monitor.last_analysis = datetime.now()

        set_advisor_monitor(mock_monitor)

        await cmd_advisor_status(mock_telegram_update, mock_telegram_context)

        mock_telegram_update.message.reply_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_advisor_on_checks_admin_permission(self):
        """cmd_advisor_on() should check admin permission."""
        from commands.advisor import cmd_advisor_on

        # Create mock update with non-admin user
        update = MagicMock()
        update.effective_user = MagicMock()
        update.effective_user.id = 999999999  # Non-admin
        update.message = AsyncMock()

        context = MagicMock()

        await cmd_advisor_on(update, context)

        update.message.reply_text.assert_called()
        # Should mention unauthorized
        call_args = update.message.reply_text.call_args[0][0]
        assert "Unauthorized" in call_args or "unauthorized" in call_args

    @pytest.mark.asyncio
    async def test_advisor_off_checks_admin_permission(self):
        """cmd_advisor_off() should check admin permission."""
        from commands.advisor import cmd_advisor_off

        # Create mock update with non-admin user
        update = MagicMock()
        update.effective_user = MagicMock()
        update.effective_user.id = 999999999
        update.message = AsyncMock()

        context = MagicMock()

        await cmd_advisor_off(update, context)

        update.message.reply_text.assert_called()
        call_args = update.message.reply_text.call_args[0][0]
        assert "Unauthorized" in call_args or "unauthorized" in call_args

    @pytest.mark.asyncio
    async def test_advisor_status_checks_admin_permission(self):
        """cmd_advisor_status() should check admin permission."""
        from commands.advisor import cmd_advisor_status

        # Create mock update with non-admin user
        update = MagicMock()
        update.effective_user = MagicMock()
        update.effective_user.id = 999999999
        update.message = AsyncMock()

        context = MagicMock()

        await cmd_advisor_status(update, context)

        update.message.reply_text.assert_called()
        call_args = update.message.reply_text.call_args[0][0]
        assert "Unauthorized" in call_args or "unauthorized" in call_args


# ============================================================================
# Test Classes - AC8: Configuration
# ============================================================================


class TestConfiguration:
    """Tests for advisor configuration (AC8)."""

    def test_advisor_enabled_config_exists(self):
        """ADVISOR_ENABLED config should exist in config.py."""
        from config import ADVISOR_ENABLED

        assert ADVISOR_ENABLED is not None
        assert isinstance(ADVISOR_ENABLED, bool)

    def test_advisor_interval_hours_config_exists(self):
        """ADVISOR_INTERVAL_HOURS config should exist in config.py."""
        from config import ADVISOR_INTERVAL_HOURS

        assert ADVISOR_INTERVAL_HOURS is not None
        assert isinstance(ADVISOR_INTERVAL_HOURS, int)

    def test_advisor_interval_hours_default_is_2(self):
        """ADVISOR_INTERVAL_HOURS should default to 2."""
        from config import ADVISOR_INTERVAL_HOURS

        assert ADVISOR_INTERVAL_HOURS == 2

    def test_suggestion_ttl_minutes_config_exists(self):
        """SUGGESTION_TTL_MINUTES config should exist in config.py."""
        from config import SUGGESTION_TTL_MINUTES

        assert SUGGESTION_TTL_MINUTES is not None
        assert isinstance(SUGGESTION_TTL_MINUTES, int)

    def test_suggestion_ttl_minutes_default_is_30(self):
        """SUGGESTION_TTL_MINUTES should default to 30."""
        from config import SUGGESTION_TTL_MINUTES

        assert SUGGESTION_TTL_MINUTES == 30


class TestEnvExample:
    """Tests for .env.example documentation."""

    def test_env_example_includes_advisor_enabled(self):
        """.env.example should include ADVISOR_ENABLED."""
        with open(".env.example") as f:
            content = f.read()

        assert "ADVISOR_ENABLED" in content

    def test_env_example_includes_advisor_interval_hours(self):
        """.env.example should include ADVISOR_INTERVAL_HOURS."""
        with open(".env.example") as f:
            content = f.read()

        assert "ADVISOR_INTERVAL_HOURS" in content

    def test_env_example_includes_suggestion_ttl_minutes(self):
        """.env.example should include SUGGESTION_TTL_MINUTES."""
        with open(".env.example") as f:
            content = f.read()

        assert "SUGGESTION_TTL_MINUTES" in content


# ============================================================================
# Test Classes - Integration
# ============================================================================


class TestIntegration:
    """End-to-end integration tests."""

    @pytest.mark.asyncio
    async def test_full_flow_suggestion_push(self, mock_bot, push_factory):
        """Full flow from suggestion creation to message push should work."""
        from advisor_monitor import pending_requests, push_suggestions

        suggestions = [
            push_factory.create_suggestion_add(),
            push_factory.create_suggestion_disable(strategy_id=2),
        ]
        context = push_factory.create_context()

        request_id = await push_suggestions(123456789, suggestions, context, mock_bot)

        # Verify request was stored
        assert request_id in pending_requests
        assert len(pending_requests[request_id]["suggestions"]) == 2

        # Verify bot was called
        mock_bot.send_message.assert_called_once()

        # Clean up
        pending_requests.pop(request_id, None)

    @pytest.mark.asyncio
    async def test_monitor_analysis_cycle(self, mock_llm, mock_api, mock_bot, push_factory):
        """AdvisorMonitor should analyze and push suggestions periodically."""
        from advisor import StrategyAdvisor
        from advisor_monitor import AdvisorMonitor, push_suggestions

        # Set up advisor with mock LLM response
        advisor = StrategyAdvisor(mock_llm, mock_api)
        mock_llm.chat.return_value = '{"suggestions": [{"action": "add", "content": "Test", "priority": 1, "reason": "Test"}]}'

        # Create monitor with short interval
        monitor = AdvisorMonitor(
            advisor, mock_api,
            callback=push_suggestions,
            admin_chat_id=123456789,
            bot=mock_bot,
            interval_hours=0.001  # Very short for testing
        )

        # Verify monitor is set up correctly
        assert monitor.advisor is advisor
        assert monitor.admin_chat_id == 123456789

    @pytest.mark.asyncio
    async def test_callback_execution_flow(self, mock_bot, push_factory, mock_contract):
        """Callback button execution should trigger strategy actions."""
        from advisor import Suggestion
        from advisor_monitor import execute_suggestion, handle_advisor_callback, pending_requests

        # Set up pending request with real Suggestion objects
        request_id = "test1234"
        suggestions = [
            Suggestion(action="add", content="Test strategy", priority=1, reason="Test"),
        ]
        pending_requests[request_id] = {
            "suggestions": suggestions,
            "created_at": datetime.now(),
            "context": push_factory.create_context(),
            "executed": False,
        }

        # Create callback for executing suggestion 1
        update = MagicMock()
        update.callback_query = MagicMock()
        update.callback_query.data = f"adv:{request_id}:1"
        update.callback_query.message = MagicMock()
        update.callback_query.message.chat_id = 123456789
        update.callback_query.message.message_id = 123
        update.callback_query.edit_message_text = AsyncMock()
        update.callback_query.answer = AsyncMock()
        update.effective_user = MagicMock()
        update.effective_user.id = 123456789

        context = MagicMock()
        context.bot = mock_bot

        with patch("main.get_contract", return_value=mock_contract):
            await handle_advisor_callback(update, context)

        # Should have updated the message
        update.callback_query.edit_message_text.assert_called()

        # Clean up
        pending_requests.pop(request_id, None)
