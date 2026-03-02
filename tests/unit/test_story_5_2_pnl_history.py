"""
Unit tests for Story 5.2: PnL History Command

Tests for:
- cmd_pnl_history_success: Normal query with default 7 records
- cmd_pnl_history_with_limit: Custom limit parameter
- cmd_pnl_history_empty: No records available
- cmd_pnl_history_api_error: API error handling
- cmd_pnl_history_unauthorized: Unauthorized user rejection

ATDD Checklist (Story 5.2: PnL History):
[x] AC1: cmd_pnl_history command handler exists in commands/query.py
[x] AC2: Calls api.get_pnl_history() method
[x] AC3: Formats output with timestamp, PnL USD, PnL ETH, change percentage
[x] AC4: Default display shows last 7 records of data
[x] AC5: Supports optional limit parameter: /pnl_history 30
[x] AC6: Unit tests cover all scenarios (success, custom limit, empty, error, unauthorized)
[x] Exported in commands/__init__.py
[x] Registered in register_handlers()
[x] Added to BotCommand list in main.py post_init()
[x] Help text updated in cmd_start
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# =============================================================================
# Tests for cmd_pnl_history
# =============================================================================


class TestCmdPnlHistory:
    """Tests for /pnl_history command."""

    @pytest.mark.asyncio
    async def test_pnl_history_success(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test normal query - cmd_pnl_history returns formatted PnL trend history.

        AC1, AC2, AC3: Command exists, calls API, formats output correctly.
        """
        # Given - API returns PnL history list with records on different days
        mock_api_response = [
            {
                "timestamp": 1709251200,  # 2024-03-01
                "pnlUsd": "100.00",
                "pnlEth": "40000000000000000",
            },
            {
                "timestamp": 1709164800,  # 2024-02-29
                "pnlUsd": "120.50",
                "pnlEth": "50000000000000000",
            },
        ]

        with (
            patch("commands.query.authorized", return_value=True),
            patch("commands.query._get_api") as mock_get_api,
        ):
            mock_api = MagicMock()
            mock_api.get_pnl_history = AsyncMock(return_value=mock_api_response)
            mock_get_api.return_value = mock_api
            from commands.query import cmd_pnl_history

            # When
            await cmd_pnl_history(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "PnL Trend" in call_args
        assert "100.00" in call_args or "120.50" in call_args  # PnL USD
        assert "Latest:" in call_args  # Summary line

    @pytest.mark.asyncio
    async def test_pnl_history_with_limit(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test custom days parameter - cmd_pnl_history limits output to specified days.

        AC5: Supports /pnl_history 30 to show 30 days.
        """
        # Given
        mock_telegram_context.args = ["30"]

        # Create 35 mock records on different days
        mock_api_response = [
            {
                "timestamp": 1709251200 + i * 86400,  # Each record on a different day
                "pnlUsd": f"{i * 10}.00",
                "pnlEth": f"{i * 10000000000000000}",
            }
            for i in range(35)
        ]

        with (
            patch("commands.query.authorized", return_value=True),
            patch("commands.query._get_api") as mock_get_api,
        ):
            mock_api = MagicMock()
            mock_api.get_pnl_history = AsyncMock(return_value=mock_api_response)
            mock_get_api.return_value = mock_api
            from commands.query import cmd_pnl_history

            # When
            await cmd_pnl_history(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        # Should show 30 days
        assert "30 days" in call_args

    @pytest.mark.asyncio
    async def test_pnl_history_default_limit(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test default 7 days - cmd_pnl_history limits output to 7 days by default.

        AC4: Default display shows last 7 days.
        """
        # Given - no args, should default to 7 days
        mock_telegram_context.args = []

        # Create 10 mock records on different days
        mock_api_response = [
            {
                "timestamp": 1709251200 + i * 86400,  # Each record on a different day
                "pnlUsd": f"{i * 10}.00",
                "pnlEth": f"{i * 10000000000000000}",
            }
            for i in range(10)
        ]

        with (
            patch("commands.query.authorized", return_value=True),
            patch("commands.query._get_api") as mock_get_api,
        ):
            mock_api = MagicMock()
            mock_api.get_pnl_history = AsyncMock(return_value=mock_api_response)
            mock_get_api.return_value = mock_api
            from commands.query import cmd_pnl_history

            # When
            await cmd_pnl_history(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        # Should show 7 days
        assert "7 days" in call_args

    @pytest.mark.asyncio
    async def test_pnl_history_empty(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test empty results - cmd_pnl_history returns friendly message when no data.

        AC3: Handles no records case gracefully.
        """
        # Given
        mock_api_response = []

        with (
            patch("commands.query.authorized", return_value=True),
            patch("commands.query._get_api") as mock_get_api,
        ):
            mock_api = MagicMock()
            mock_api.get_pnl_history = AsyncMock(return_value=mock_api_response)
            mock_get_api.return_value = mock_api
            from commands.query import cmd_pnl_history

            # When
            await cmd_pnl_history(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "No PnL history" in call_args

    @pytest.mark.asyncio
    async def test_pnl_history_api_error(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test API error handling - cmd_pnl_history displays error message.

        AC3: Handles API errors gracefully.
        """
        # Given
        mock_api_response = {"error": "HTTP 500: Internal Server Error"}

        with (
            patch("commands.query.authorized", return_value=True),
            patch("commands.query._get_api") as mock_get_api,
        ):
            mock_api = MagicMock()
            mock_api.get_pnl_history = AsyncMock(return_value=mock_api_response)
            mock_get_api.return_value = mock_api
            from commands.query import cmd_pnl_history

            # When
            await cmd_pnl_history(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "Error:" in call_args
        assert "HTTP 500" in call_args

    @pytest.mark.asyncio
    async def test_pnl_history_unauthorized(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test unauthorized user - cmd_pnl_history rejects access.

        AC: Only authorized users can access the command.
        """
        # Given
        with patch("commands.query.authorized", return_value=False):
            from commands.query import cmd_pnl_history

            # When
            await cmd_pnl_history(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_not_called()


# =============================================================================
# Tests for command registration
# =============================================================================


class TestPnlHistoryRegistration:
    """Tests for command registration and exports."""

    def test_cmd_pnl_history_exported(self) -> None:
        """Test that cmd_pnl_history is exported from commands module.

        AC: Command is exported in commands/__init__.py.
        """
        # When
        from commands import cmd_pnl_history

        # Then - should not raise ImportError
        assert callable(cmd_pnl_history)

    def test_cmd_pnl_history_in_all(self) -> None:
        """Test that cmd_pnl_history is in __all__ list.

        AC: Command is included in module's __all__ export list.
        """
        # When
        import commands

        # Then
        assert "cmd_pnl_history" in commands.__all__
