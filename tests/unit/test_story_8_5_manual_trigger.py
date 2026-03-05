"""
ATDD Tests for Story 8-5: Manual Trigger Analysis Command

These tests are designed to FAIL before implementation (TDD RED phase).
Run: pytest tests/unit/test_story_8_5_manual_trigger.py -v

Generated: 2026-03-04
Story: 8-5-manual-trigger
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from advisor import CollectedData
from commands.advisor import (
    MANUAL_ANALYSIS_COOLDOWN,
    _last_manual_analysis,
    cmd_advisor_analyze,
)

# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def mock_admin_update() -> MagicMock:
    """Create a mock Telegram Update object for admin user."""
    update = MagicMock()
    update.effective_user = MagicMock()
    update.effective_user.id = 123456789  # Admin user ID
    update.effective_chat = MagicMock()
    update.effective_chat.id = 123456789
    update.message = AsyncMock()
    return update


@pytest.fixture
def mock_non_admin_update() -> MagicMock:
    """Create a mock Telegram Update object for non-admin user."""
    update = MagicMock()
    update.effective_user = MagicMock()
    update.effective_user.id = 999888777  # Non-admin user ID
    update.effective_chat = MagicMock()
    update.effective_chat.id = 999888777
    update.message = AsyncMock()
    return update


@pytest.fixture
def mock_context() -> MagicMock:
    """Create a mock Telegram Context object."""
    context = MagicMock()
    context.bot = AsyncMock()
    return context


@pytest.fixture
def mock_suggestion_add() -> dict:
    """Create a mock add strategy suggestion."""
    return {
        "action": "add",
        "content": "When BTC breaks 70000, sell 50% of ETH position",
        "priority": 2,
        "expiry_hours": 24,
        "reason": "BTC breaking key resistance may trigger market correction",
    }


@pytest.fixture
def mock_collected_data() -> CollectedData:
    """Create mock CollectedData for analysis."""
    return CollectedData(
        positions={
            "ethBalance": "1.5000",
            "tokens": [{"symbol": "ETH"}, {"symbol": "USDC"}, {"symbol": "BTC"}],
            "totalPnlUsd": "+$150.00",
        },
        strategies=[
            {"id": 1, "content": "Strategy 1"},
            {"id": 2, "content": "Strategy 2"},
        ],
        vault={"paused": False},
        eth_price={"price": 3000, "change24h": 2.5},
        tokens={},
        candles={},
        collected_at="2026-03-04T12:00:00",
        errors=[],
    )


# ============================================================================
# Test: Permission Check - Non-Admin Rejected
# ============================================================================


@pytest.mark.asyncio
async def test_non_admin_rejected(mock_non_admin_update, mock_context):
    """Test that non-admin users are rejected with Unauthorized message."""
    with patch("commands.advisor.is_admin", return_value=False):
        await cmd_advisor_analyze(mock_non_admin_update, mock_context)

    mock_non_admin_update.message.reply_text.assert_called_once_with("Unauthorized: Admin only")


# ============================================================================
# Test: Cooldown - 5 Minute Rate Limit
# ============================================================================


@pytest.mark.asyncio
async def test_cooldown_rejects_repeated_calls(mock_admin_update, mock_context):
    """Test that repeated calls within 5 minutes are rejected."""
    user_id = mock_admin_update.effective_user.id

    # Set last analysis time to 2 minutes ago
    _last_manual_analysis[user_id] = datetime.now() - timedelta(minutes=2)

    with patch("commands.advisor.is_admin", return_value=True):
        await cmd_advisor_analyze(mock_admin_update, mock_context)

    # Should show cooldown message with remaining time
    call_args = mock_admin_update.message.reply_text.call_args[0][0]
    assert "Please wait" in call_args
    assert "min before next analysis" in call_args


@pytest.mark.asyncio
async def test_cooldown_allows_after_5_minutes(
    mock_admin_update, mock_context, mock_suggestion_add, mock_collected_data
):
    """Test that calls are allowed after 5 minute cooldown expires."""
    user_id = mock_admin_update.effective_user.id

    # Set last analysis time to 6 minutes ago (beyond cooldown)
    _last_manual_analysis[user_id] = datetime.now() - timedelta(minutes=6)

    # Mock the advisor monitor
    mock_advisor = MagicMock()
    mock_advisor.analyze = AsyncMock(return_value=[mock_suggestion_add])
    mock_advisor.collector.collect = AsyncMock(return_value=mock_collected_data)

    mock_monitor = MagicMock()
    mock_monitor.advisor = mock_advisor

    # Create a mock status message
    mock_status_msg = AsyncMock()
    mock_admin_update.message.reply_text.return_value = mock_status_msg

    with patch("commands.advisor.is_admin", return_value=True):
        with patch("commands.advisor._advisor_monitor", mock_monitor):
            with patch("advisor_monitor.push_suggestions", AsyncMock(return_value="abc123")):
                await cmd_advisor_analyze(mock_admin_update, mock_context)

    # Should have called reply_text for status message
    assert mock_admin_update.message.reply_text.called

    # Verify cooldown was updated (new timestamp)
    assert user_id in _last_manual_analysis
    new_time = _last_manual_analysis[user_id]
    # New time should be recent (not the old 6 minutes ago time)
    time_diff = abs((datetime.now() - new_time).total_seconds())
    assert time_diff < 1.0, f"Cooldown should be updated to current time, but diff was {time_diff}s"


# ============================================================================
# Test: Successful Analysis Flow
# ============================================================================


@pytest.mark.asyncio
async def test_successful_analysis_flow(
    mock_admin_update, mock_context, mock_suggestion_add, mock_collected_data
):
    """Test complete successful analysis flow with suggestions returned."""
    user_id = mock_admin_update.effective_user.id

    # Clear any previous cooldown
    if user_id in _last_manual_analysis:
        del _last_manual_analysis[user_id]

    # Mock the advisor monitor
    mock_advisor = MagicMock()
    mock_advisor.analyze = AsyncMock(return_value=[mock_suggestion_add])
    mock_advisor.collector.collect = AsyncMock(return_value=mock_collected_data)

    mock_monitor = MagicMock()
    mock_monitor.advisor = mock_advisor

    with patch("commands.advisor.is_admin", return_value=True):
        with patch("commands.advisor._advisor_monitor", mock_monitor):
            with patch("advisor_monitor.push_suggestions", AsyncMock(return_value="abc123")):
                await cmd_advisor_analyze(mock_admin_update, mock_context)

    # Verify status message was sent
    assert mock_admin_update.message.reply_text.called

    # Verify last analysis time was recorded
    assert user_id in _last_manual_analysis


@pytest.mark.asyncio
async def test_analysis_shows_status_message(
    mock_admin_update, mock_context, mock_suggestion_add, mock_collected_data
):
    """Test that 'Analyzing your portfolio...' status message is shown."""
    user_id = mock_admin_update.effective_user.id
    if user_id in _last_manual_analysis:
        del _last_manual_analysis[user_id]

    mock_advisor = MagicMock()
    mock_advisor.analyze = AsyncMock(return_value=[mock_suggestion_add])
    mock_advisor.collector.collect = AsyncMock(return_value=mock_collected_data)

    mock_monitor = MagicMock()
    mock_monitor.advisor = mock_advisor

    # Create a mock status message that can be edited
    mock_status_msg = AsyncMock()
    mock_admin_update.message.reply_text.return_value = mock_status_msg

    with patch("commands.advisor.is_admin", return_value=True):
        with patch("commands.advisor._advisor_monitor", mock_monitor):
            with patch("advisor_monitor.push_suggestions", AsyncMock(return_value="abc123")):
                await cmd_advisor_analyze(mock_admin_update, mock_context)

    # Verify initial status message content - MUST start with "Analyzing your portfolio..."
    initial_call = mock_admin_update.message.reply_text.call_args_list[0]
    initial_message = initial_call[0][0]
    assert initial_message == "Analyzing your portfolio...", (
        f"Expected 'Analyzing your portfolio...' but got '{initial_message}'"
    )

    # Verify final status message shows completion with count
    final_call = mock_status_msg.edit_text.call_args[0][0]
    assert "Analysis complete!" in final_call, (
        f"Expected 'Analysis complete!' in final message but got '{final_call}'"
    )
    assert "1 suggestion" in final_call, (
        f"Expected '1 suggestion' count in final message but got '{final_call}'"
    )


# ============================================================================
# Test: No Suggestions Case
# ============================================================================


@pytest.mark.asyncio
async def test_no_suggestions_returns_friendly_message(mock_admin_update, mock_context):
    """Test that empty suggestions list returns friendly 'No suggestions' message."""
    user_id = mock_admin_update.effective_user.id
    if user_id in _last_manual_analysis:
        del _last_manual_analysis[user_id]

    # Mock the advisor monitor returning empty suggestions
    mock_advisor = MagicMock()
    mock_advisor.analyze = AsyncMock(return_value=[])

    mock_monitor = MagicMock()
    mock_monitor.advisor = mock_advisor

    # Create a mock status message that can be edited
    mock_status_msg = AsyncMock()
    mock_admin_update.message.reply_text.return_value = mock_status_msg

    with patch("commands.advisor.is_admin", return_value=True):
        with patch("commands.advisor._advisor_monitor", mock_monitor):
            await cmd_advisor_analyze(mock_admin_update, mock_context)

    # Verify edit_text was called with "No suggestions" message
    mock_status_msg.edit_text.assert_called()
    call_args = mock_status_msg.edit_text.call_args[0][0]
    assert "No suggestions" in call_args


# ============================================================================
# Test: Error Handling
# ============================================================================


@pytest.mark.asyncio
async def test_error_returns_friendly_message(mock_admin_update, mock_context):
    """Test that errors during analysis return friendly error message."""
    user_id = mock_admin_update.effective_user.id
    if user_id in _last_manual_analysis:
        del _last_manual_analysis[user_id]

    # Mock the advisor monitor that throws an error
    mock_advisor = MagicMock()
    mock_advisor.analyze = AsyncMock(side_effect=Exception("API connection failed"))

    mock_monitor = MagicMock()
    mock_monitor.advisor = mock_advisor

    # Create a mock status message that can be edited
    mock_status_msg = AsyncMock()
    mock_admin_update.message.reply_text.return_value = mock_status_msg

    with patch("commands.advisor.is_admin", return_value=True):
        with patch("commands.advisor._advisor_monitor", mock_monitor):
            await cmd_advisor_analyze(mock_admin_update, mock_context)

    # Verify edit_text was called with error message
    mock_status_msg.edit_text.assert_called()
    call_args = mock_status_msg.edit_text.call_args[0][0]
    assert "failed" in call_args.lower() or "error" in call_args.lower()


@pytest.mark.asyncio
async def test_monitor_not_initialized_error(mock_admin_update, mock_context):
    """Test that uninitialized monitor returns friendly error and records cooldown."""
    user_id = mock_admin_update.effective_user.id
    if user_id in _last_manual_analysis:
        del _last_manual_analysis[user_id]

    with patch("commands.advisor.is_admin", return_value=True):
        with patch("commands.advisor._advisor_monitor", None):
            await cmd_advisor_analyze(mock_admin_update, mock_context)

    # Verify error message
    mock_admin_update.message.reply_text.assert_called_once_with("Advisor monitor not initialized")

    # MEDIUM fix: Cooldown should be recorded even on monitor init failure
    # to prevent spam while system is recovering
    assert user_id in _last_manual_analysis, (
        "Cooldown should be recorded even when monitor not initialized"
    )

    # Cleanup
    del _last_manual_analysis[user_id]


# ============================================================================
# Test: Cooldown Constant
# ============================================================================


def test_cooldown_is_5_minutes():
    """Test that cooldown period is set to 5 minutes."""
    assert MANUAL_ANALYSIS_COOLDOWN == timedelta(minutes=5)


# ============================================================================
# Test: Multiple Suggestions
# ============================================================================


@pytest.mark.asyncio
async def test_multiple_suggestions_count(mock_admin_update, mock_context, mock_collected_data):
    """Test that analysis with multiple suggestions shows correct count."""
    user_id = mock_admin_update.effective_user.id
    if user_id in _last_manual_analysis:
        del _last_manual_analysis[user_id]

    # Create multiple suggestions
    suggestions = [
        {"action": "add", "content": f"Strategy {i}", "priority": 1, "reason": f"Reason {i}"}
        for i in range(3)
    ]

    mock_advisor = MagicMock()
    mock_advisor.analyze = AsyncMock(return_value=suggestions)
    mock_advisor.collector.collect = AsyncMock(return_value=mock_collected_data)

    mock_monitor = MagicMock()
    mock_monitor.advisor = mock_advisor

    # Create a mock status message that can be edited
    mock_status_msg = AsyncMock()
    mock_admin_update.message.reply_text.return_value = mock_status_msg

    with patch("commands.advisor.is_admin", return_value=True):
        with patch("commands.advisor._advisor_monitor", mock_monitor):
            with patch("advisor_monitor.push_suggestions", AsyncMock(return_value="abc123")):
                await cmd_advisor_analyze(mock_admin_update, mock_context)

    # Verify final status shows 3 suggestions
    final_edit_call = mock_status_msg.edit_text.call_args[0][0]
    assert "3 suggestion" in final_edit_call


# ============================================================================
# Integration Test: End-to-End Flow
# ============================================================================


@pytest.mark.asyncio
async def test_integration_end_to_end_flow(mock_admin_update, mock_context):
    """
    Integration test: Complete end-to-end flow from command to result.

    This test verifies the entire flow works correctly:
    1. Admin permission check passes
    2. Cooldown check passes
    3. Monitor initialized check passes
    4. Status message is sent
    5. Analysis is executed
    6. Suggestions are pushed with proper parameters
    7. Status message is updated with count
    8. Cooldown is recorded
    """
    user_id = mock_admin_update.effective_user.id

    # Clear any previous cooldown
    if user_id in _last_manual_analysis:
        del _last_manual_analysis[user_id]

    # Create realistic test data
    suggestions = [
        {
            "action": "add",
            "content": "When ETH drops below 2800, buy 0.5 ETH",
            "priority": 2,
            "expiry_hours": 48,
            "reason": "ETH at key support level",
        },
        {
            "action": "disable",
            "strategy_id": 3,
            "reason": "Strategy condition no longer valid",
        },
    ]

    # Create CollectedData object (as expected by actual code)
    # ethBalance should be in wei (2.5 ETH = 2.5 * 10^18)
    collected_data = CollectedData(
        positions={
            "ethBalance": "2500000000000000000",  # 2.5 ETH in wei
            "tokens": [{"symbol": "ETH"}, {"symbol": "USDC"}, {"symbol": "BTC"}],
            "totalPnlUsd": "+$350.00",
        },
        strategies=[
            {"id": 1, "content": "Strategy 1"},
            {"id": 2, "content": "Strategy 2"},
            {"id": 3, "content": "Strategy 3"},
        ],
        vault={"paused": False},
        eth_price={"price": 3000, "change24h": 2.5},
        tokens={},
        candles={},
        collected_at="2026-03-04T12:00:00",
        errors=[],
    )

    # Mock the advisor monitor with realistic behavior
    mock_advisor = MagicMock()
    mock_advisor.analyze = AsyncMock(return_value=suggestions)
    mock_advisor.collector = MagicMock()
    mock_advisor.collector.collect = AsyncMock(return_value=collected_data)

    mock_monitor = MagicMock()
    mock_monitor.advisor = mock_advisor

    # Create a trackable mock status message
    mock_status_msg = AsyncMock()
    mock_admin_update.message.reply_text.return_value = mock_status_msg

    # Track push_suggestions call
    push_suggestions_calls = []

    async def track_push_suggestions(**kwargs):
        push_suggestions_calls.append(kwargs)
        return "test-request-id-123"

    with patch("commands.advisor.is_admin", return_value=True):
        with patch("commands.advisor._advisor_monitor", mock_monitor):
            with patch("advisor_monitor.push_suggestions", side_effect=track_push_suggestions):
                await cmd_advisor_analyze(mock_admin_update, mock_context)

    # === VERIFICATION ===

    # 1. Status message was sent with correct initial text
    mock_admin_update.message.reply_text.assert_called_once_with("Analyzing your portfolio...")

    # 2. push_suggestions was called with correct parameters
    assert len(push_suggestions_calls) == 1, "push_suggestions should be called exactly once"
    push_call = push_suggestions_calls[0]
    assert push_call["chat_id"] == mock_admin_update.effective_chat.id
    assert push_call["suggestions"] == suggestions
    # context is built from CollectedData, verify expected keys
    assert push_call["context"]["balance"] == "2.500000 ETH"
    assert push_call["context"]["positions"] == 3
    assert push_call["context"]["strategies"] == 3
    assert push_call["context"]["pnl"] == "+$350.00"
    assert push_call["bot"] == mock_context.bot

    # 3. Final status message shows correct count
    final_message = mock_status_msg.edit_text.call_args[0][0]
    assert "Analysis complete!" in final_message
    assert "2 suggestion" in final_message

    # 4. Cooldown was recorded for the user
    assert user_id in _last_manual_analysis
    recorded_time = _last_manual_analysis[user_id]
    assert isinstance(recorded_time, datetime)
    # Should be very recent (within 1 second)
    time_diff = abs((datetime.now() - recorded_time).total_seconds())
    assert time_diff < 1.0, f"Recorded time should be recent, but diff was {time_diff}s"

    # Cleanup
    del _last_manual_analysis[user_id]
