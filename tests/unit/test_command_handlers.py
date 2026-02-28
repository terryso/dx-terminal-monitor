"""
Unit tests for Telegram bot command handlers (P0 priority).

Tests for: cmd_balance, cmd_positions, cmd_pnl
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch


# =============================================================================
# Tests for cmd_balance
# =============================================================================

class TestCmdBalance:
    """Tests for /balance command."""

    @pytest.mark.asyncio
    async def test_balance_success(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /balance returns formatted balance info."""
        # Given
        mock_api_response = {
            "ethBalance": "2000000000000000000",  # 2 ETH
            "overallValueUsd": "7000.00",
            "overallPnlUsd": "300.00",
            "overallPnlPercent": "4.5",
        }

        with patch("main.authorized", return_value=True), \
             patch("main.api") as mock_api:
            mock_api.get_positions = AsyncMock(return_value=mock_api_response)
            from main import cmd_balance

            # When
            await cmd_balance(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "2.000000" in call_args  # ETH balance
        assert "$7000.00" in call_args  # Total value
        assert "$300.00" in call_args  # PnL
        assert "+4.50%" in call_args  # PnL percent

    @pytest.mark.asyncio
    async def test_balance_with_negative_pnl(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /balance shows negative PnL correctly."""
        # Given
        mock_api_response = {
            "ethBalance": "1000000000000000000",
            "overallValueUsd": "3000.00",
            "overallPnlUsd": "-150.00",
            "overallPnlPercent": "-5.0",
        }

        with patch("main.authorized", return_value=True), \
             patch("main.api") as mock_api:
            mock_api.get_positions = AsyncMock(return_value=mock_api_response)
            from main import cmd_balance

            # When
            await cmd_balance(mock_telegram_update, mock_telegram_context)

        # Then
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "$-150.00" in call_args
        assert "-5.00%" in call_args

    @pytest.mark.asyncio
    async def test_balance_api_error(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /balance handles API errors."""
        # Given
        mock_api_response = {"error": "Connection timeout"}

        with patch("main.authorized", return_value=True), \
             patch("main.api") as mock_api:
            mock_api.get_positions = AsyncMock(return_value=mock_api_response)
            from main import cmd_balance

            # When
            await cmd_balance(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once_with(
            "Error: Connection timeout"
        )

    @pytest.mark.asyncio
    async def test_balance_unauthorized(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /balance rejects unauthorized users."""
        with patch("main.authorized", return_value=False):
            from main import cmd_balance

            # When
            await cmd_balance(mock_telegram_update, mock_telegram_context)

        # Then - should not call reply_text (returns silently)
        mock_telegram_update.message.reply_text.assert_not_called()

    @pytest.mark.asyncio
    async def test_balance_zero_balance(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /balance with zero balance."""
        # Given
        mock_api_response = {
            "ethBalance": "0",
            "overallValueUsd": "0",
            "overallPnlUsd": "0",
            "overallPnlPercent": "0",
        }

        with patch("main.authorized", return_value=True), \
             patch("main.api") as mock_api:
            mock_api.get_positions = AsyncMock(return_value=mock_api_response)
            from main import cmd_balance

            # When
            await cmd_balance(mock_telegram_update, mock_telegram_context)

        # Then
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "0.000000" in call_args
        assert "$0.00" in call_args


# =============================================================================
# Tests for cmd_positions
# =============================================================================

class TestCmdPositions:
    """Tests for /positions command."""

    @pytest.mark.asyncio
    async def test_positions_success(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /positions returns list of positions."""
        # Given
        mock_api_response = {
            "positions": [
                {
                    "tokenSymbol": "ETH",
                    "currentValueUsd": "3500.00",
                    "totalPnlUsd": "150.00",
                    "totalPnlPercent": "4.5",
                },
                {
                    "tokenSymbol": "USDC",
                    "currentValueUsd": "1000.00",
                    "totalPnlUsd": "-50.00",
                    "totalPnlPercent": "-5.0",
                },
            ]
        }

        with patch("main.authorized", return_value=True), \
             patch("main.api") as mock_api:
            mock_api.get_positions = AsyncMock(return_value=mock_api_response)
            from main import cmd_positions

            # When
            await cmd_positions(mock_telegram_update, mock_telegram_context)

        # Then
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "ETH" in call_args
        assert "USDC" in call_args
        assert "$3500.00" in call_args
        assert "$1000.00" in call_args

    @pytest.mark.asyncio
    async def test_positions_empty(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /positions with no positions."""
        # Given
        mock_api_response = {"positions": []}

        with patch("main.authorized", return_value=True), \
             patch("main.api") as mock_api:
            mock_api.get_positions = AsyncMock(return_value=mock_api_response)
            from main import cmd_positions

            # When
            await cmd_positions(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once_with(
            "No positions"
        )

    @pytest.mark.asyncio
    async def test_positions_api_error(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /positions handles API errors."""
        # Given
        mock_api_response = {"error": "Rate limit exceeded"}

        with patch("main.authorized", return_value=True), \
             patch("main.api") as mock_api:
            mock_api.get_positions = AsyncMock(return_value=mock_api_response)
            from main import cmd_positions

            # When
            await cmd_positions(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once_with(
            "Error: Rate limit exceeded"
        )

    @pytest.mark.asyncio
    async def test_positions_unauthorized(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /positions rejects unauthorized users."""
        with patch("main.authorized", return_value=False):
            from main import cmd_positions

            # When
            await cmd_positions(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_not_called()

    @pytest.mark.asyncio
    async def test_positions_single_position(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
        position_factory,
    ) -> None:
        """Test /positions with single position."""
        # Given
        position = position_factory.create(token_symbol="WBTC")
        mock_api_response = {"positions": [position]}

        with patch("main.authorized", return_value=True), \
             patch("main.api") as mock_api:
            mock_api.get_positions = AsyncMock(return_value=mock_api_response)
            from main import cmd_positions

            # When
            await cmd_positions(mock_telegram_update, mock_telegram_context)

        # Then
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "WBTC" in call_args
        assert "$1000.00" in call_args


# =============================================================================
# Tests for cmd_pnl
# =============================================================================

class TestCmdPnl:
    """Tests for /pnl command."""

    @pytest.mark.asyncio
    async def test_pnl_success(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /pnl returns detailed PnL breakdown."""
        # Given
        mock_api_response = {
            "overallPnlUsd": "500.00",
            "overallPnlPercent": "15.0",
            "overallPnlEth": "150000000000000000",  # 0.15 ETH
            "positions": [
                {
                    "tokenSymbol": "ETH",
                    "totalPnlUsd": "300.00",
                    "totalPnlPercent": "10.0",
                    "realizedPnlUsd": "200.00",
                    "unrealizedPnlUsd": "100.00",
                },
                {
                    "tokenSymbol": "USDC",
                    "totalPnlUsd": "200.00",
                    "totalPnlPercent": "5.0",
                    "realizedPnlUsd": "50.00",
                    "unrealizedPnlUsd": "150.00",
                },
            ],
        }

        with patch("main.authorized", return_value=True), \
             patch("main.api") as mock_api:
            mock_api.get_positions = AsyncMock(return_value=mock_api_response)
            from main import cmd_pnl

            # When
            await cmd_pnl(mock_telegram_update, mock_telegram_context)

        # Then
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "$500.00" in call_args  # Total PnL
        assert "+15.00%" in call_args  # Total percent
        assert "0.150000" in call_args  # ETH PnL
        assert "ETH" in call_args
        assert "USDC" in call_args
        assert "Realized" in call_args
        assert "Unrealized" in call_args

    @pytest.mark.asyncio
    async def test_pnl_with_losses(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /pnl with negative PnL."""
        # Given
        mock_api_response = {
            "overallPnlUsd": "-200.00",
            "overallPnlPercent": "-8.0",
            "overallPnlEth": "-80000000000000000",  # -0.08 ETH
            "positions": [
                {
                    "tokenSymbol": "ETH",
                    "totalPnlUsd": "-200.00",
                    "totalPnlPercent": "-8.0",
                    "realizedPnlUsd": "0.00",
                    "unrealizedPnlUsd": "-200.00",
                },
            ],
        }

        with patch("main.authorized", return_value=True), \
             patch("main.api") as mock_api:
            mock_api.get_positions = AsyncMock(return_value=mock_api_response)
            from main import cmd_pnl

            # When
            await cmd_pnl(mock_telegram_update, mock_telegram_context)

        # Then
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "$-200.00" in call_args
        assert "-8.00%" in call_args

    @pytest.mark.asyncio
    async def test_pnl_api_error(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /pnl handles API errors."""
        # Given
        mock_api_response = {"error": "Service unavailable"}

        with patch("main.authorized", return_value=True), \
             patch("main.api") as mock_api:
            mock_api.get_positions = AsyncMock(return_value=mock_api_response)
            from main import cmd_pnl

            # When
            await cmd_pnl(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once_with(
            "Error: Service unavailable"
        )

    @pytest.mark.asyncio
    async def test_pnl_unauthorized(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /pnl rejects unauthorized users."""
        with patch("main.authorized", return_value=False):
            from main import cmd_pnl

            # When
            await cmd_pnl(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_not_called()

    @pytest.mark.asyncio
    async def test_pnl_no_positions(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /pnl with empty positions."""
        # Given
        mock_api_response = {
            "overallPnlUsd": "0",
            "overallPnlPercent": "0",
            "overallPnlEth": "0",
            "positions": [],
        }

        with patch("main.authorized", return_value=True), \
             patch("main.api") as mock_api:
            mock_api.get_positions = AsyncMock(return_value=mock_api_response)
            from main import cmd_pnl

            # When
            await cmd_pnl(mock_telegram_update, mock_telegram_context)

        # Then
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "$0.00" in call_args
        assert "0.00%" in call_args
