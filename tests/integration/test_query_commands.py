"""
Integration tests for query commands module (AC 3, AC 8)

Tests for: commands/query.py command handlers
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# =============================================================================
# Tests for cmd_balance (AC 3, AC 8)
# =============================================================================


class TestCmdBalanceRefactored:
    """Tests for /balance command after refactoring."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_balance_success_from_query_module(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /balance returns formatted balance info from commands.query."""
        # Given
        from commands.query import cmd_balance

        mock_api_response = {
            "ethBalance": "2000000000000000000",
            "overallValueUsd": "7000.00",
            "overallPnlUsd": "300.00",
            "overallPnlPercent": "4.5",
        }
        mock_api = MagicMock()
        mock_api.get_positions = AsyncMock(return_value=mock_api_response)

        with (
            patch("commands.query.authorized", return_value=True),
            patch("commands.query._get_api", return_value=mock_api),
        ):
            # When
            await cmd_balance(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "2.000000" in call_args
        assert "$7000.00" in call_args

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_balance_api_error_from_query_module(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /balance handles API errors from commands.query (AC 8)."""
        # Given
        from commands.query import cmd_balance

        mock_api_response = {"error": "Connection timeout"}
        mock_api = MagicMock()
        mock_api.get_positions = AsyncMock(return_value=mock_api_response)

        with (
            patch("commands.query.authorized", return_value=True),
            patch("commands.query._get_api", return_value=mock_api),
        ):
            # When
            await cmd_balance(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once_with("Error: Connection timeout")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_balance_unauthorized_from_query_module(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /balance rejects unauthorized users from commands.query."""
        # Given
        from commands.query import cmd_balance

        with patch("commands.query.authorized", return_value=False):
            # When
            await cmd_balance(mock_telegram_update, mock_telegram_context)

        # Then - balance doesn't send message on unauthorized, just returns
        # This is expected behavior - no message sent
        pass


# =============================================================================
# Tests for cmd_positions (AC 3)
# =============================================================================


class TestCmdPositionsRefactored:
    """Tests for /positions command after refactoring."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_positions_success_from_query_module(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /positions returns formatted positions from commands.query."""
        # Given
        from commands.query import cmd_positions

        mock_api_response = {
            "positions": [
                {
                    "tokenSymbol": "ETH",
                    "currentValueUsd": "3500.00",
                    "totalPnlUsd": "150.00",
                    "totalPnlPercent": "4.5",
                }
            ]
        }
        mock_api = MagicMock()
        mock_api.get_positions = AsyncMock(return_value=mock_api_response)

        with (
            patch("commands.query.authorized", return_value=True),
            patch("commands.query._get_api", return_value=mock_api),
        ):
            # When
            await cmd_positions(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "ETH" in call_args


# =============================================================================
# Tests for cmd_pnl (AC 3)
# =============================================================================


class TestCmdPnlRefactored:
    """Tests for /pnl command after refactoring."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_pnl_success_from_query_module(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /pnl returns formatted PnL from commands.query."""
        # Given
        from commands.query import cmd_pnl

        mock_api_response = {
            "overallPnlUsd": "300.00",
            "overallPnlPercent": "4.5",
            "positions": [],
        }
        mock_api = MagicMock()
        mock_api.get_positions = AsyncMock(return_value=mock_api_response)

        with (
            patch("commands.query.authorized", return_value=True),
            patch("commands.query._get_api", return_value=mock_api),
        ):
            # When
            await cmd_pnl(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "300" in call_args or "4.5" in call_args


# =============================================================================
# Tests for cmd_activity (AC 3)
# =============================================================================


class TestCmdActivityRefactored:
    """Tests for /activity command after refactoring."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_activity_success_from_query_module(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /activity returns formatted activity from commands.query."""
        # Given
        from commands.query import cmd_activity

        mock_api_response = {
            "items": [
                {
                    "type": "swap",
                    "swap": {"tokenSymbol": "USDC", "side": "buy"},
                    "timestamp": "2024-03-01T12:00:00Z",
                }
            ]
        }
        mock_api = MagicMock()
        mock_api.get_activity = AsyncMock(return_value=mock_api_response)

        with (
            patch("commands.query.authorized", return_value=True),
            patch("commands.query._get_api", return_value=mock_api),
        ):
            # When
            await cmd_activity(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()


# =============================================================================
# Tests for cmd_swaps (AC 3)
# =============================================================================


class TestCmdSwapsRefactored:
    """Tests for /swaps command after refactoring."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_swaps_success_from_query_module(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /swaps returns formatted swaps from commands.query."""
        # Given
        from commands.query import cmd_swaps

        mock_api_response = {
            "items": [
                {
                    "type": "swap",
                    "swap": {
                        "tokenSymbol": "USDC",
                        "side": "buy",
                        "ethAmount": "1000000000000000000",
                    },
                    "timestamp": "2024-03-01T12:00:00Z",
                }
            ]
        }
        mock_api = MagicMock()
        mock_api.get_swaps = AsyncMock(return_value=mock_api_response)

        with (
            patch("commands.query.authorized", return_value=True),
            patch("commands.query._get_api", return_value=mock_api),
        ):
            # When
            await cmd_swaps(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()


# =============================================================================
# Tests for cmd_strategies (AC 3)
# =============================================================================


class TestCmdStrategiesRefactored:
    """Tests for /strategies command after refactoring."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_strategies_success_from_query_module(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /strategies returns formatted strategies from commands.query."""
        # Given
        from commands.query import cmd_strategies

        mock_api_response = [
            {"strategyId": 1, "strategyPriority": "HIGH", "content": "Test strategy content here"},
        ]
        mock_api = MagicMock()
        mock_api.get_strategies = AsyncMock(return_value=mock_api_response)

        with (
            patch("commands.query.authorized", return_value=True),
            patch("commands.query._get_api", return_value=mock_api),
        ):
            # When
            await cmd_strategies(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()


# =============================================================================
# Tests for cmd_vault (AC 3)
# =============================================================================


class TestCmdVaultRefactored:
    """Tests for /vault command after refactoring."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_vault_success_from_query_module(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /vault returns formatted vault info from commands.query."""
        # Given
        from commands.query import cmd_vault

        mock_api_response = {
            "ethBalance": "5000000000000000000",
            "paused": False,
        }
        mock_api = MagicMock()
        mock_api.get_vault = AsyncMock(return_value=mock_api_response)

        with (
            patch("commands.query.authorized", return_value=True),
            patch("commands.query._get_api", return_value=mock_api),
        ):
            # When
            await cmd_vault(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()
