"""
Unit tests for Telegram bot command handlers (P1 priority).

Tests for: cmd_activity, cmd_swaps, cmd_strategies, cmd_vault
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch


# =============================================================================
# Tests for cmd_activity
# =============================================================================

class TestCmdActivity:
    """Tests for /activity command."""

    @pytest.mark.asyncio
    async def test_activity_with_swap(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /activity shows swap transactions."""
        # Given
        mock_api_response = {
            "items": [
                {
                    "type": "swap",
                    "swap": {
                        "tokenSymbol": "USDC",
                        "side": "buy",
                        "ethAmount": "500000000000000000",  # 0.5 ETH
                    },
                },
            ]
        }

        with patch("main.authorized", return_value=True), \
             patch("main.api") as mock_api:
            mock_api.get_activity = AsyncMock(return_value=mock_api_response)
            from main import cmd_activity

            # When
            await cmd_activity(mock_telegram_update, mock_telegram_context)

        # Then
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "[Swap]" in call_args
        assert "BUY" in call_args
        assert "USDC" in call_args
        assert "0.500000" in call_args

    @pytest.mark.asyncio
    async def test_activity_with_deposit(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /activity shows deposits."""
        # Given
        mock_api_response = {
            "items": [
                {
                    "type": "deposit",
                    "deposit": {
                        "amountWei": "2000000000000000000",  # 2 ETH
                    },
                },
            ]
        }

        with patch("main.authorized", return_value=True), \
             patch("main.api") as mock_api:
            mock_api.get_activity = AsyncMock(return_value=mock_api_response)
            from main import cmd_activity

            # When
            await cmd_activity(mock_telegram_update, mock_telegram_context)

        # Then
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "[Deposit]" in call_args
        assert "2.000000" in call_args

    @pytest.mark.asyncio
    async def test_activity_with_withdrawal(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /activity shows withdrawals."""
        # Given
        mock_api_response = {
            "items": [
                {
                    "type": "withdrawal",
                    "withdrawal": {
                        "amountWei": "1000000000000000000",  # 1 ETH
                    },
                },
            ]
        }

        with patch("main.authorized", return_value=True), \
             patch("main.api") as mock_api:
            mock_api.get_activity = AsyncMock(return_value=mock_api_response)
            from main import cmd_activity

            # When
            await cmd_activity(mock_telegram_update, mock_telegram_context)

        # Then
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "[Withdraw]" in call_args
        assert "1.000000" in call_args

    @pytest.mark.asyncio
    async def test_activity_mixed_types(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /activity with multiple activity types."""
        # Given
        mock_api_response = {
            "items": [
                {"type": "swap", "swap": {"tokenSymbol": "USDC", "side": "sell", "ethAmount": "100000000000000000"}},
                {"type": "deposit", "deposit": {"amountWei": "500000000000000000"}},
                {"type": "withdrawal", "withdrawal": {"amountWei": "200000000000000000"}},
            ]
        }

        with patch("main.authorized", return_value=True), \
             patch("main.api") as mock_api:
            mock_api.get_activity = AsyncMock(return_value=mock_api_response)
            from main import cmd_activity

            # When
            await cmd_activity(mock_telegram_update, mock_telegram_context)

        # Then
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "[Swap]" in call_args
        assert "[Deposit]" in call_args
        assert "[Withdraw]" in call_args

    @pytest.mark.asyncio
    async def test_activity_empty(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /activity with no recent activity."""
        # Given
        mock_api_response = {"items": []}

        with patch("main.authorized", return_value=True), \
             patch("main.api") as mock_api:
            mock_api.get_activity = AsyncMock(return_value=mock_api_response)
            from main import cmd_activity

            # When
            await cmd_activity(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once_with(
            "No recent activity"
        )

    @pytest.mark.asyncio
    async def test_activity_api_error(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /activity handles API errors."""
        # Given
        mock_api_response = {"error": "Timeout"}

        with patch("main.authorized", return_value=True), \
             patch("main.api") as mock_api:
            mock_api.get_activity = AsyncMock(return_value=mock_api_response)
            from main import cmd_activity

            # When
            await cmd_activity(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once_with(
            "Error: Timeout"
        )

    @pytest.mark.asyncio
    async def test_activity_unauthorized(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /activity rejects unauthorized users."""
        with patch("main.authorized", return_value=False):
            from main import cmd_activity

            # When
            await cmd_activity(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_not_called()


# =============================================================================
# Tests for cmd_swaps
# =============================================================================

class TestCmdSwaps:
    """Tests for /swaps command."""

    @pytest.mark.asyncio
    async def test_swaps_success(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /swaps returns swap history."""
        # Given
        mock_api_response = {
            "items": [
                {
                    "tokenSymbol": "USDC",
                    "side": "buy",
                    "ethAmount": "1000000000000000000",  # 1 ETH
                    "effectivePriceUsd": "3500.00",
                },
                {
                    "tokenSymbol": "WBTC",
                    "side": "sell",
                    "ethAmount": "500000000000000000",  # 0.5 ETH
                    "effectivePriceUsd": "45000.00",
                },
            ]
        }

        with patch("main.authorized", return_value=True), \
             patch("main.api") as mock_api:
            mock_api.get_swaps = AsyncMock(return_value=mock_api_response)
            from main import cmd_swaps

            # When
            await cmd_swaps(mock_telegram_update, mock_telegram_context)

        # Then
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "BUY" in call_args
        assert "SELL" in call_args
        assert "USDC" in call_args
        assert "WBTC" in call_args
        assert "$3500.00" in call_args
        assert "$45000.00" in call_args

    @pytest.mark.asyncio
    async def test_swaps_empty(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /swaps with no swaps."""
        # Given
        mock_api_response = {"items": []}

        with patch("main.authorized", return_value=True), \
             patch("main.api") as mock_api:
            mock_api.get_swaps = AsyncMock(return_value=mock_api_response)
            from main import cmd_swaps

            # When
            await cmd_swaps(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once_with(
            "No swaps"
        )

    @pytest.mark.asyncio
    async def test_swaps_api_error(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /swaps handles API errors."""
        # Given
        mock_api_response = {"error": "Network error"}

        with patch("main.authorized", return_value=True), \
             patch("main.api") as mock_api:
            mock_api.get_swaps = AsyncMock(return_value=mock_api_response)
            from main import cmd_swaps

            # When
            await cmd_swaps(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once_with(
            "Error: Network error"
        )

    @pytest.mark.asyncio
    async def test_swaps_unauthorized(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /swaps rejects unauthorized users."""
        with patch("main.authorized", return_value=False):
            from main import cmd_swaps

            # When
            await cmd_swaps(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_not_called()


# =============================================================================
# Tests for cmd_strategies
# =============================================================================

class TestCmdStrategies:
    """Tests for /strategies command."""

    @pytest.mark.asyncio
    async def test_strategies_success(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /strategies returns active strategies."""
        # Given
        mock_api_response = [
            {
                "strategyId": "1",
                "strategyPriority": "high",
                "content": "Buy ETH when price drops below $3000 and hold for long term gains",
            },
            {
                "strategyId": "2",
                "strategyPriority": "low",
                "content": "Take profit when portfolio value exceeds $10000",
            },
        ]

        with patch("main.authorized", return_value=True), \
             patch("main.api") as mock_api:
            mock_api.get_strategies = AsyncMock(return_value=mock_api_response)
            from main import cmd_strategies

            # When
            await cmd_strategies(mock_telegram_update, mock_telegram_context)

        # Then
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "#1" in call_args
        assert "#2" in call_args
        assert "[HIGH]" in call_args
        assert "[LOW]" in call_args
        assert "Buy ETH" in call_args

    @pytest.mark.asyncio
    async def test_strategies_empty(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /strategies with no active strategies."""
        # Given
        mock_api_response = []

        with patch("main.authorized", return_value=True), \
             patch("main.api") as mock_api:
            mock_api.get_strategies = AsyncMock(return_value=mock_api_response)
            from main import cmd_strategies

            # When
            await cmd_strategies(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once_with(
            "No active strategies"
        )

    @pytest.mark.asyncio
    async def test_strategies_api_error(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /strategies handles API errors."""
        # Given
        mock_api_response = {"error": "Unauthorized access"}

        with patch("main.authorized", return_value=True), \
             patch("main.api") as mock_api:
            mock_api.get_strategies = AsyncMock(return_value=mock_api_response)
            from main import cmd_strategies

            # When
            await cmd_strategies(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once_with(
            "Error: Unauthorized access"
        )

    @pytest.mark.asyncio
    async def test_strategies_unauthorized(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /strategies rejects unauthorized users."""
        with patch("main.authorized", return_value=False):
            from main import cmd_strategies

            # When
            await cmd_strategies(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_not_called()


# =============================================================================
# Tests for cmd_vault
# =============================================================================

class TestCmdVault:
    """Tests for /vault command."""

    @pytest.mark.asyncio
    async def test_vault_success(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /vault returns vault information."""
        # Given
        mock_api_response = {
            "vaultAddress": "0x933aafc9C5B1e0000E1dd77ac52D67b0E4e4997C",
            "nftId": "42",
            "nftName": "My Trading Vault",
            "ownerAddress": "0xOwner123",
            "state": "active",
            "paused": False,
            "maxTradeAmount": "1000",  # 10%
            "slippageBps": "50",  # 0.5%
        }

        with patch("main.authorized", return_value=True), \
             patch("main.api") as mock_api:
            mock_api.get_vault = AsyncMock(return_value=mock_api_response)
            from main import cmd_vault

            # When
            await cmd_vault(mock_telegram_update, mock_telegram_context)

        # Then
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "0x933aafc9C5B1e0000E1dd77ac52D67b0E4e4997C" in call_args
        assert "#42" in call_args
        assert "My Trading Vault" in call_args
        assert "0xOwner123" in call_args
        assert "active" in call_args
        assert "False" in call_args

    @pytest.mark.asyncio
    async def test_vault_paused(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /vault shows paused status."""
        # Given
        mock_api_response = {
            "vaultAddress": "0x933aafc9C5B1e0000E1dd77ac52D67b0E4e4997C",
            "nftId": "1",
            "nftName": "Paused Vault",
            "ownerAddress": "0xOwner",
            "state": "paused",
            "paused": True,
            "maxTradeAmount": "500",
            "slippageBps": "100",
        }

        with patch("main.authorized", return_value=True), \
             patch("main.api") as mock_api:
            mock_api.get_vault = AsyncMock(return_value=mock_api_response)
            from main import cmd_vault

            # When
            await cmd_vault(mock_telegram_update, mock_telegram_context)

        # Then
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "paused" in call_args.lower()
        assert "True" in call_args

    @pytest.mark.asyncio
    async def test_vault_api_error(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /vault handles API errors."""
        # Given
        mock_api_response = {"error": "Vault not found"}

        with patch("main.authorized", return_value=True), \
             patch("main.api") as mock_api:
            mock_api.get_vault = AsyncMock(return_value=mock_api_response)
            from main import cmd_vault

            # When
            await cmd_vault(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once_with(
            "Error: Vault not found"
        )

    @pytest.mark.asyncio
    async def test_vault_unauthorized(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /vault rejects unauthorized users."""
        with patch("main.authorized", return_value=False):
            from main import cmd_vault

            # When
            await cmd_vault(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_not_called()
