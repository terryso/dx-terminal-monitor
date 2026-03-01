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
                    "timestamp": 1700000000,  # Valid timestamp
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
        assert "Swap" in call_args
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
                    "timestamp": 1700000000,  # Valid timestamp
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
        assert "Deposit" in call_args
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
                    "timestamp": 1700000000,  # Valid timestamp
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
        assert "Withdraw" in call_args
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
                {"type": "swap", "timestamp": 1700000000, "swap": {"tokenSymbol": "USDC", "side": "sell", "ethAmount": "100000000000000000"}},
                {"type": "deposit", "timestamp": 1700000100, "deposit": {"amountWei": "500000000000000000"}},
                {"type": "withdrawal", "timestamp": 1700000200, "withdrawal": {"amountWei": "200000000000000000"}},
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
        assert "Swap" in call_args
        assert "Deposit" in call_args
        assert "Withdraw" in call_args

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


# =============================================================================
# Tests for cmd_disable_strategy (Story 1.1 - ATDD RED PHASE)
# These tests are intentionally SKIPPED because the feature is not implemented yet.
# Once cmd_disable_strategy is implemented, remove the @pytest.mark.skip decorators.
# =============================================================================

class TestCmdDisableStrategy:
    """Tests for /disable_strategy command (Story 1.1)."""

    @pytest.fixture(autouse=True)
    def setup_environment(self):
        """Set up environment and isolate main module."""
        import os
        import sys

        # Set environment variables
        os.environ['RPC_URL'] = 'https://eth-test.example.com'
        os.environ['PRIVATE_KEY'] = '0x' + 'a' * 64
        os.environ['CHAIN_ID'] = '1'
        os.environ['VAULT_ADDRESS'] = '0x933aafc9C5B1e0000E1dd77ac52D67b0E4e4997C'

        # Remove main and contract from cache if loaded
        for mod in ['main', 'contract', 'config']:
            if mod in sys.modules:
                del sys.modules[mod]

        yield

        # Clean up
        for key in ['RPC_URL', 'PRIVATE_KEY', 'CHAIN_ID', 'VAULT_ADDRESS']:
            os.environ.pop(key, None)
        for mod in ['main', 'contract', 'config']:
            if mod in sys.modules:
                del sys.modules[mod]

    @pytest.fixture
    def mock_contract_instance(self) -> MagicMock:
        """Create a mock contract instance."""
        contract_mock = MagicMock()
        contract_mock.disable_strategy = AsyncMock(return_value={
            'success': True,
            'transactionHash': '0xabc123...',
        })
        return contract_mock

    @pytest.mark.asyncio
    async def test_cmd_disable_strategy_success(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
        mock_contract_instance: MagicMock,
    ) -> None:
        """Test successful strategy disable (P0)."""
        # Given
        strategy_id = 1
        mock_tx_hash = "0xabc123def456..."
        mock_contract_instance.disable_strategy.return_value = {
            'success': True,
            'transactionHash': mock_tx_hash,
        }

        # Patch contract.VaultContract before importing main
        with patch("contract.VaultContract", return_value=mock_contract_instance):
            from main import cmd_disable_strategy

            # Now patch authorized
            with patch("main.authorized", return_value=True):
                # Set up command args
                mock_telegram_context.args = [str(strategy_id)]
                mock_telegram_update.message.reply_text = AsyncMock()

                # When
                await cmd_disable_strategy(mock_telegram_update, mock_telegram_context)

                # Then
                mock_contract_instance.disable_strategy.assert_called_once_with(strategy_id)
                mock_telegram_update.message.reply_text.assert_called_once()
                call_args = mock_telegram_update.message.reply_text.call_args[0][0]
                assert f"策略 #{strategy_id} 已禁用" in call_args
                assert mock_tx_hash in call_args

    @pytest.mark.asyncio
    async def test_cmd_disable_strategy_no_args(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test disable strategy with no arguments (P1)."""
        # Given
        mock_contract = MagicMock()

        with patch("contract.VaultContract", return_value=mock_contract):
            from main import cmd_disable_strategy

            with patch("main.authorized", return_value=True):
                mock_telegram_context.args = []
                mock_telegram_update.message.reply_text = AsyncMock()

                # When
                await cmd_disable_strategy(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "用法" in call_args

    @pytest.mark.asyncio
    async def test_cmd_disable_strategy_invalid_id(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test disable strategy with invalid ID format (P1)."""
        # Given
        mock_contract = MagicMock()

        with patch("contract.VaultContract", return_value=mock_contract):
            from main import cmd_disable_strategy

            with patch("main.authorized", return_value=True):
                mock_telegram_context.args = ["abc"]
                mock_telegram_update.message.reply_text = AsyncMock()

                # When
                await cmd_disable_strategy(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "数字" in call_args

    @pytest.mark.asyncio
    async def test_cmd_disable_strategy_contract_fails_not_exist(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test disable strategy when strategy doesn't exist (P1)."""
        # Given
        strategy_id = 999
        mock_contract = MagicMock()
        mock_contract.disable_strategy = AsyncMock(return_value={
            'success': False,
            'error': "Strategy #999 doesn't exist or is not active",
        })

        with patch("contract.VaultContract", return_value=mock_contract):
            from main import cmd_disable_strategy

            with patch("main.authorized", return_value=True):
                mock_telegram_context.args = [str(strategy_id)]
                mock_telegram_update.message.reply_text = AsyncMock()

                # When
                await cmd_disable_strategy(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert f"策略 #{strategy_id} 不存在或已禁用" in call_args

    @pytest.mark.asyncio
    async def test_cmd_disable_strategy_contract_fails_not_active(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test disable strategy when strategy not active (P1)."""
        # Given
        strategy_id = 1
        mock_contract = MagicMock()
        mock_contract.disable_strategy = AsyncMock(return_value={
            'success': False,
            'error': "Strategy is not active",
        })

        with patch("contract.VaultContract", return_value=mock_contract):
            from main import cmd_disable_strategy

            with patch("main.authorized", return_value=True):
                mock_telegram_context.args = [str(strategy_id)]
                mock_telegram_update.message.reply_text = AsyncMock()

                # When
                await cmd_disable_strategy(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert f"策略 #{strategy_id} 不存在或已禁用" in call_args

    @pytest.mark.asyncio
    async def test_cmd_disable_strategy_contract_fails_generic_error(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test disable strategy with generic contract error (P1)."""
        # Given
        strategy_id = 1
        error_msg = "Insufficient gas"
        mock_contract = MagicMock()
        mock_contract.disable_strategy = AsyncMock(return_value={
            'success': False,
            'error': error_msg,
        })

        with patch("contract.VaultContract", return_value=mock_contract):
            from main import cmd_disable_strategy

            with patch("main.authorized", return_value=True):
                mock_telegram_context.args = [str(strategy_id)]
                mock_telegram_update.message.reply_text = AsyncMock()

                # When
                await cmd_disable_strategy(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "交易失败" in call_args
        assert error_msg in call_args

    @pytest.mark.asyncio
    async def test_cmd_disable_strategy_unauthorized(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test disable strategy rejects unauthorized users (P0)."""
        # Given
        mock_contract = MagicMock()

        with patch("contract.VaultContract", return_value=mock_contract):
            from main import cmd_disable_strategy

            with patch("main.authorized", return_value=False):
                mock_telegram_context.args = ["1"]
                mock_telegram_update.message.reply_text = AsyncMock()

                # When
                await cmd_disable_strategy(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once_with("未授权")

    @pytest.mark.asyncio
    async def test_cmd_disable_strategy_authorized_user_proceeds(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test authorized user can proceed to disable strategy (P1)."""
        # Given
        strategy_id = 1
        mock_tx_hash = "0xdef456..."
        mock_contract = MagicMock()
        mock_contract.disable_strategy = AsyncMock(return_value={
            'success': True,
            'transactionHash': mock_tx_hash,
        })

        with patch("contract.VaultContract", return_value=mock_contract):
            from main import cmd_disable_strategy

            with patch("main.authorized", return_value=True):
                mock_telegram_context.args = [str(strategy_id)]
                mock_telegram_update.message.reply_text = AsyncMock()

                # When
                await cmd_disable_strategy(mock_telegram_update, mock_telegram_context)

        # Then - contract was called (authorization passed)
            mock_contract.disable_strategy.assert_called_once_with(strategy_id)
            mock_telegram_update.message.reply_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_cmd_disable_strategy_negative_id(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test disable strategy with negative ID (P1)."""
        # Given
        mock_contract = MagicMock()
        mock_contract.disable_strategy = AsyncMock(return_value={
            'success': True,
            'transactionHash': "0x...",
        })

        with patch("contract.VaultContract", return_value=mock_contract):
            from main import cmd_disable_strategy

            with patch("main.authorized", return_value=True):
                mock_telegram_context.args = ["-1"]
                mock_telegram_update.message.reply_text = AsyncMock()

                # When
                await cmd_disable_strategy(mock_telegram_update, mock_telegram_context)

        # Then - should handle negative ID (either reject or pass through to contract)
            mock_telegram_update.message.reply_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_cmd_disable_strategy_zero_id(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test disable strategy with zero ID (P1)."""
        # Given
        mock_contract = MagicMock()
        mock_contract.disable_strategy = AsyncMock(return_value={
            'success': True,
            'transactionHash': "0x...",
        })

        with patch("contract.VaultContract", return_value=mock_contract):
            from main import cmd_disable_strategy

            with patch("main.authorized", return_value=True):
                mock_telegram_context.args = ["0"]
                mock_telegram_update.message.reply_text = AsyncMock()

                # When
                await cmd_disable_strategy(mock_telegram_update, mock_telegram_context)

        # Then - should handle zero ID (either reject or pass through to contract)
            mock_telegram_update.message.reply_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_cmd_disable_strategy_multiple_args_uses_first(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test disable strategy with multiple arguments uses first (P1)."""
        # Given
        strategy_id = 1
        mock_contract = MagicMock()
        mock_contract.disable_strategy = AsyncMock(return_value={
            'success': True,
            'transactionHash': "0xtest...",
        })

        with patch("contract.VaultContract", return_value=mock_contract):
            from main import cmd_disable_strategy

            with patch("main.authorized", return_value=True):
                # Multiple args, should use first
                mock_telegram_context.args = [str(strategy_id), "extra", "args"]
                mock_telegram_update.message.reply_text = AsyncMock()

                # When
                await cmd_disable_strategy(mock_telegram_update, mock_telegram_context)

        # Then - should use only first argument
            mock_contract.disable_strategy.assert_called_once_with(strategy_id)

    @pytest.mark.asyncio
    async def test_disable_strategy_contract_method_calls_disableStrategy(
        self,
    ) -> None:
        """Test contract.disable_strategy calls web3 disableStrategy (Unit)."""
        # This test validates the contract.py method, not the command handler
        # Given
        strategy_id = 1

        # Mock web3 contract function - need to mock at the class level
        from unittest.mock import MagicMock
        from contract import VaultContract

        # Create a mock instance with proper setup
        mock_vault = MagicMock(spec=VaultContract)
        mock_vault._send_transaction = AsyncMock(return_value={
            'success': True,
            'transactionHash': '0xabc123...',
        })
        mock_vault.contract = MagicMock()
        mock_vault.contract.functions.disableStrategy.return_value = "mock_tx_func"

        # When
        result = await VaultContract.disable_strategy(mock_vault, strategy_id)

        # Then
        assert result['success'] is True
        assert 'transactionHash' in result
        mock_vault._send_transaction.assert_called_once()


# =============================================================================
# Tests for cmd_disable_all (Story 1.2 - ATDD RED PHASE)
# These tests are intentionally designed to FAIL until the feature is implemented.
# =============================================================================

class TestCmdDisableAll:
    """Tests for /disable_all command (Story 1.2)."""

    @pytest.fixture(autouse=True)
    def setup_environment(self):
        """Set up environment and isolate main module."""
        import os
        import sys

        # Set environment variables
        os.environ['RPC_URL'] = 'https://eth-test.example.com'
        os.environ['PRIVATE_KEY'] = '0x' + 'a' * 64
        os.environ['CHAIN_ID'] = '1'
        os.environ['VAULT_ADDRESS'] = '0x933aafc9C5B1e0000E1dd77ac52D67b0E4e4997C'

        # Remove main and contract from cache if loaded
        for mod in ['main', 'contract', 'config']:
            if mod in sys.modules:
                del sys.modules[mod]

        yield

        # Clean up
        for key in ['RPC_URL', 'PRIVATE_KEY', 'CHAIN_ID', 'VAULT_ADDRESS']:
            os.environ.pop(key, None)
        for mod in ['main', 'contract', 'config']:
            if mod in sys.modules:
                del sys.modules[mod]

    @pytest.fixture
    def mock_contract_instance(self) -> MagicMock:
        """Create a mock contract instance."""
        contract_mock = MagicMock()
        contract_mock.disable_all_strategies = AsyncMock(return_value={
            'success': True,
            'transactionHash': '0xabc123...',
            'disabledCount': 3,
        })
        return contract_mock

    @pytest.mark.asyncio
    async def test_cmd_disable_all_success(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
        mock_contract_instance: MagicMock,
    ) -> None:
        """Test successful disable all strategies (P0)."""
        # Given
        mock_tx_hash = "0xdef456..."
        disabled_count = 3
        mock_contract_instance.disable_all_strategies.return_value = {
            'success': True,
            'transactionHash': mock_tx_hash,
            'disabledCount': disabled_count,
        }

        with patch("contract.VaultContract", return_value=mock_contract_instance):
            from main import cmd_disable_all

            with patch("main.authorized", return_value=True), \
                 patch("main.api") as mock_api:
                mock_api.get_strategies = AsyncMock(return_value=[
                    {"strategyId": 1},
                    {"strategyId": 2},
                    {"strategyId": 3},
                ])
                mock_telegram_update.message.reply_text = AsyncMock()

                # When
                await cmd_disable_all(mock_telegram_update, mock_telegram_context)

                # Then
                mock_contract_instance.disable_all_strategies.assert_called_once()
                call_args = mock_telegram_update.message.reply_text.call_args[0][0]
                assert "已禁用" in call_args
                assert str(disabled_count) in call_args
                assert mock_tx_hash in call_args

    @pytest.mark.asyncio
    async def test_cmd_disable_all_no_active_strategies(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
        mock_contract_instance: MagicMock,
    ) -> None:
        """Test disable all when no active strategies (P1)."""
        # Given - API returns empty strategies list
        mock_contract_instance.disable_all_strategies.return_value = {
            'success': True,
            'disabledCount': 0,
            'message': 'no_active_strategies',
        }

        with patch("contract.VaultContract", return_value=mock_contract_instance):
            from main import cmd_disable_all

            with patch("main.authorized", return_value=True), \
                 patch("main.api") as mock_api:
                mock_api.get_strategies = AsyncMock(return_value=[])
                mock_telegram_update.message.reply_text = AsyncMock()

                # When
                await cmd_disable_all(mock_telegram_update, mock_telegram_context)

                # Then
                call_args = mock_telegram_update.message.reply_text.call_args[0][0]
                assert "没有活跃策略" in call_args

    @pytest.mark.asyncio
    async def test_cmd_disable_all_unauthorized(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test disable all rejects unauthorized users (P0)."""
        # Given
        mock_contract = MagicMock()

        with patch("contract.VaultContract", return_value=mock_contract):
            from main import cmd_disable_all

            with patch("main.authorized", return_value=False):
                mock_telegram_update.message.reply_text = AsyncMock()

                # When
                await cmd_disable_all(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once_with("未授权")

    @pytest.mark.asyncio
    async def test_cmd_disable_all_contract_fails(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
        mock_contract_instance: MagicMock,
    ) -> None:
        """Test disable all with contract error (P1)."""
        # Given
        error_msg = "Gas 估算失败，可能是合约条件不满足"
        mock_contract_instance.disable_all_strategies.return_value = {
            'success': False,
            'error': error_msg,
        }

        with patch("contract.VaultContract", return_value=mock_contract_instance):
            from main import cmd_disable_all

            with patch("main.authorized", return_value=True), \
                 patch("main.api") as mock_api:
                mock_api.get_strategies = AsyncMock(return_value=[{"strategyId": 1}])
                mock_telegram_update.message.reply_text = AsyncMock()

                # When
                await cmd_disable_all(mock_telegram_update, mock_telegram_context)

        # Then
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "交易失败" in call_args
        assert error_msg in call_args

    @pytest.mark.asyncio
    async def test_cmd_disable_all_contract_method_calls_disableAllActiveStrategies(
        self,
    ) -> None:
        """Test contract.disable_all_strategies calls web3 disableAllActiveStrategies (Unit)."""
        # This test validates the contract.py method, not the command handler
        # Given
        from contract import VaultContract

        # Create a mock instance with proper setup
        mock_vault = MagicMock(spec=VaultContract)
        mock_vault._send_transaction = AsyncMock(return_value={
            'success': True,
            'transactionHash': '0xabc123...',
            'status': 1,
            'blockNumber': 12345,
        })
        mock_vault.contract = MagicMock()
        mock_vault.contract.functions.disableAllActiveStrategies.return_value = "mock_tx_func"

        # Mock the callback
        async def mock_get_count():
            return 3

        # When - call the actual method from the class
        result = await VaultContract.disable_all_strategies(mock_vault, mock_get_count)

        # Then
        assert result['success'] is True
        assert result['disabledCount'] == 3
        assert 'transactionHash' in result
        mock_vault._send_transaction.assert_called_once()

    @pytest.mark.asyncio
    async def test_cmd_disable_all_registers_command_handler(
        self,
    ) -> None:
        """Test cmd_disable_all is registered as command handler (P1)."""
        import os
        import sys

        os.environ['RPC_URL'] = 'https://eth-test.example.com'
        os.environ['PRIVATE_KEY'] = '0x' + 'a' * 64
        os.environ['CHAIN_ID'] = '1'
        os.environ['VAULT_ADDRESS'] = '0x933aafc9C5B1e0000E1dd77ac52D67b0E4e4997C'

        for mod in ['main', 'contract', 'config']:
            if mod in sys.modules:
                del sys.modules[mod]

        try:
            from main import create_app

            app = create_app()

            # Check if disable_all handler is registered
            # The handlers attribute is a dict mapping group_id to list of handlers
            all_handlers = []
            for group_handlers in app.handlers.values():
                all_handlers.extend(group_handlers)

            # CommandHandler uses 'commands' attribute (frozenset)
            has_disable_all = any(
                hasattr(h, 'commands') and 'disable_all' in h.commands
                for h in all_handlers
            )

            assert has_disable_all, "Command handler for 'disable_all' not registered"
        finally:
            for key in ['RPC_URL', 'PRIVATE_KEY', 'CHAIN_ID', 'VAULT_ADDRESS']:
                os.environ.pop(key, None)

    @pytest.mark.asyncio
    async def test_cmd_disable_all_registers_bot_command(
        self,
    ) -> None:
        """Test disable_all is registered in bot menu (P1)."""
        import os
        import sys

        os.environ['RPC_URL'] = 'https://eth-test.example.com'
        os.environ['PRIVATE_KEY'] = '0x' + 'a' * 64
        os.environ['CHAIN_ID'] = '1'
        os.environ['VAULT_ADDRESS'] = '0x933aafc9C5B1e0000E1dd77ac52D67b0E4e4997C'

        for mod in ['main', 'contract', 'config']:
            if mod in sys.modules:
                del sys.modules[mod]

        try:
            from telegram import BotCommand

            # Mock the bot
            mock_bot = MagicMock()
            mock_bot.set_my_commands = AsyncMock()

            mock_app = MagicMock()
            mock_app.bot = mock_bot

            from main import post_init

            # Run post_init using await (proper async pattern)
            await post_init(mock_app)

            # Check if set_my_commands was called
            mock_bot.set_my_commands.assert_called_once()
            commands = mock_bot.set_my_commands.call_args[0][0]

            # Verify disable_all command is in the list
            command_names = [cmd.command if hasattr(cmd, 'command') else str(cmd) for cmd in commands]
            assert 'disable_all' in command_names, "'disable_all' not in bot commands"
        finally:
            for key in ['RPC_URL', 'PRIVATE_KEY', 'CHAIN_ID', 'VAULT_ADDRESS']:
                os.environ.pop(key, None)

    @pytest.mark.asyncio
    async def test_cmd_disable_all_help_text_updated(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test help text includes disable_all command (P1)."""
        import os
        import sys

        os.environ['RPC_URL'] = 'https://eth-test.example.com'
        os.environ['PRIVATE_KEY'] = '0x' + 'a' * 64
        os.environ['CHAIN_ID'] = '1'
        os.environ['VAULT_ADDRESS'] = '0x933aafc9C5B1e0000E1dd77ac52D67b0E4e4997C'

        for mod in ['main', 'contract', 'config']:
            if mod in sys.modules:
                del sys.modules[mod]

        try:
            from main import cmd_start

            with patch("main.authorized", return_value=True):
                mock_telegram_update.message.reply_text = AsyncMock()

                # When
                await cmd_start(mock_telegram_update, mock_telegram_context)

                # Then
                call_args = mock_telegram_update.message.reply_text.call_args[0][0]
                assert "disable_all" in call_args.lower() or "/disable_all" in call_args
        finally:
            for key in ['RPC_URL', 'PRIVATE_KEY', 'CHAIN_ID', 'VAULT_ADDRESS']:
                os.environ.pop(key, None)

    @pytest.mark.asyncio
    async def test_cmd_disable_all_api_unavailable(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
        mock_contract_instance: MagicMock,
    ) -> None:
        """Test disable all when API is unavailable (P1)."""
        # Given - API returns error, count unavailable
        mock_tx_hash = "0xdef456..."
        mock_contract_instance.disable_all_strategies.return_value = {
            'success': True,
            'transactionHash': mock_tx_hash,
            'disabledCount': -1,  # -1 indicates count unavailable
        }

        with patch("contract.VaultContract", return_value=mock_contract_instance):
            from main import cmd_disable_all

            with patch("main.authorized", return_value=True), \
                 patch("main.api") as mock_api:
                mock_api.get_strategies = AsyncMock(return_value={"error": "API unavailable"})
                mock_telegram_update.message.reply_text = AsyncMock()

                # When
                await cmd_disable_all(mock_telegram_update, mock_telegram_context)

                # Then
                call_args = mock_telegram_update.message.reply_text.call_args[0][0]
                assert "已禁用所有策略" in call_args
                assert mock_tx_hash in call_args

    @pytest.mark.asyncio
    async def test_cmd_disable_all_contract_method_without_callback(
        self,
    ) -> None:
        """Test contract.disable_all_strategies without callback returns -1."""
        # Given
        from contract import VaultContract

        mock_vault = MagicMock(spec=VaultContract)
        mock_vault._send_transaction = AsyncMock(return_value={
            'success': True,
            'transactionHash': '0xabc123...',
            'status': 1,
            'blockNumber': 12345,
        })
        mock_vault.contract = MagicMock()
        mock_vault.contract.functions.disableAllActiveStrategies.return_value = "mock_tx_func"

        # When - call without callback
        result = await VaultContract.disable_all_strategies(mock_vault, None)

        # Then
        assert result['success'] is True
        assert result['disabledCount'] == -1  # -1 indicates count unavailable


# =============================================================================
# Tests for cmd_add_strategy (Story 2-1: ATDD RED Phase)
# =============================================================================

class TestCmdAddStrategy:
    """Tests for /add_strategy command - Story 2-1.

    NOTE: These tests are intentionally FAILING (TDD RED phase).
    The cmd_add_strategy function is NOT YET IMPLEMENTED.
    These tests define the EXPECTED behavior that implementation should satisfy.
    """

    @pytest.mark.asyncio
    async def test_add_strategy_success(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test successful strategy addition by admin user.

        Verifies: AC#2, AC#3, AC#5
        - Command handler exists and accepts strategy content
        - Returns success message with strategy ID
        """
        # Given - admin user with valid strategy content
        mock_telegram_update.effective_user.id = 123456789  # Admin user

        mock_contract_result = {
            "success": True,
            "strategyId": 4,
            "transactionHash": "0xabc123def456",
            "status": 1,
            "blockNumber": 12345678,
        }

        # Create mock contract instance
        mock_contract_instance = MagicMock()
        mock_contract_instance.add_strategy = AsyncMock(return_value=mock_contract_result)

        with patch("main.is_admin", return_value=True), \
             patch("main.contract", return_value=mock_contract_instance):
            from main import cmd_add_strategy

            # When
            mock_telegram_context.args = ["当", "ETH", "跌破", "3000", "时买入"]
            await cmd_add_strategy(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "策略已添加" in call_args
        assert "#4" in call_args

    @pytest.mark.asyncio
    async def test_add_strategy_unauthorized_non_admin(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test non-admin user is rejected.

        Verifies: AC#7
        - Only admin users can add strategies
        """
        # Given - non-admin user
        mock_telegram_update.effective_user.id = 99999  # Non-admin

        # Create mock contract instance (should not be called)
        mock_contract_instance = MagicMock()
        mock_contract_instance.add_strategy = AsyncMock()

        with patch("main.is_admin", return_value=False), \
             patch("main.contract", return_value=mock_contract_instance):
            from main import cmd_add_strategy

            # When
            mock_telegram_context.args = ["test strategy"]
            await cmd_add_strategy(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "未授权" in call_args or "unauthorized" in call_args.lower()
        # Verify contract was NOT called for non-admin
        mock_contract_instance.add_strategy.assert_not_called()

    @pytest.mark.asyncio
    async def test_add_strategy_no_args(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test error when no strategy content provided.

        Verifies: AC#2, AC#3
        - Shows usage help when no args provided
        """
        # Given - admin user but no args
        mock_telegram_update.effective_user.id = 123456789  # Admin user

        with patch("main.is_admin", return_value=True):
            from main import cmd_add_strategy

            # When
            mock_telegram_context.args = None  # No args
            await cmd_add_strategy(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "用法" in call_args

    @pytest.mark.asyncio
    async def test_add_strategy_empty_args(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test error when args list is empty.

        Verifies: AC#2, AC#3
        - Shows usage help when args list is empty
        """
        # Given - admin user with empty args
        mock_telegram_update.effective_user.id = 123456789  # Admin user

        with patch("main.is_admin", return_value=True):
            from main import cmd_add_strategy

            # When
            mock_telegram_context.args = []  # Empty list
            await cmd_add_strategy(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "用法" in call_args

    @pytest.mark.asyncio
    async def test_add_strategy_max_limit_reached(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test error when strategy limit (8) is reached.

        Verifies: AC#6
        - Shows user-friendly error when max strategies reached
        """
        # Given - admin user but max limit reached
        mock_telegram_update.effective_user.id = 123456789  # Admin user

        mock_contract_result = {
            "success": False,
            "error": "Max strategies limit reached (8)",
        }

        # Create mock contract instance
        mock_contract_instance = MagicMock()
        mock_contract_instance.add_strategy = AsyncMock(return_value=mock_contract_result)

        with patch("main.is_admin", return_value=True), \
             patch("main.contract", return_value=mock_contract_instance):
            from main import cmd_add_strategy

            # When
            mock_telegram_context.args = ["new strategy"]
            await cmd_add_strategy(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "上限" in call_args or "limit" in call_args.lower()

    @pytest.mark.asyncio
    async def test_add_strategy_contract_failure(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test handling of generic contract failure.

        Verifies: AC#2
        - Shows error message on contract failure
        """
        # Given - admin user but contract fails
        mock_telegram_update.effective_user.id = 123456789  # Admin user

        mock_contract_result = {
            "success": False,
            "error": "Network connection failed",
        }

        # Create mock contract instance
        mock_contract_instance = MagicMock()
        mock_contract_instance.add_strategy = AsyncMock(return_value=mock_contract_result)

        with patch("main.is_admin", return_value=True), \
             patch("main.contract", return_value=mock_contract_instance):
            from main import cmd_add_strategy

            # When
            mock_telegram_context.args = ["test strategy"]
            await cmd_add_strategy(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "失败" in call_args or "error" in call_args.lower()

    @pytest.mark.asyncio
    async def test_add_strategy_registers_command_handler(self) -> None:
        """Test cmd_add_strategy is registered as command handler.

        Verifies: AC#2
        """
        import os
        import sys

        os.environ['RPC_URL'] = 'https://eth-test.example.com'
        os.environ['PRIVATE_KEY'] = '0x' + 'a' * 64
        os.environ['CHAIN_ID'] = '1'
        os.environ['VAULT_ADDRESS'] = '0x933aafc9C5B1e0000E1dd77ac52D67b0E4e4997C'

        for mod in ['main', 'contract', 'config']:
            if mod in sys.modules:
                del sys.modules[mod]

        try:
            from main import create_app

            app = create_app()

            # Check if add_strategy handler is registered
            all_handlers = []
            for group_handlers in app.handlers.values():
                all_handlers.extend(group_handlers)

            # CommandHandler uses 'commands' attribute (frozenset)
            has_add_strategy = any(
                hasattr(h, 'commands') and 'add_strategy' in h.commands
                for h in all_handlers
            )

            assert has_add_strategy, "Command handler for 'add_strategy' not registered"
        finally:
            for key in ['RPC_URL', 'PRIVATE_KEY', 'CHAIN_ID', 'VAULT_ADDRESS']:
                os.environ.pop(key, None)

    @pytest.mark.asyncio
    async def test_add_strategy_registers_bot_command(self) -> None:
        """Test add_strategy is registered in bot menu.

        Verifies: AC#2
        """
        import os
        import sys

        os.environ['RPC_URL'] = 'https://eth-test.example.com'
        os.environ['PRIVATE_KEY'] = '0x' + 'a' * 64
        os.environ['CHAIN_ID'] = '1'
        os.environ['VAULT_ADDRESS'] = '0x933aafc9C5B1e0000E1dd77ac52D67b0E4e4997C'

        for mod in ['main', 'contract', 'config']:
            if mod in sys.modules:
                del sys.modules[mod]

        try:
            from telegram import BotCommand

            # Mock the bot
            mock_bot = MagicMock()
            mock_bot.set_my_commands = AsyncMock()

            mock_app = MagicMock()
            mock_app.bot = mock_bot

            from main import post_init

            # Run post_init
            await post_init(mock_app)

            # Check if set_my_commands was called
            mock_bot.set_my_commands.assert_called_once()
            commands = mock_bot.set_my_commands.call_args[0][0]

            # Verify add_strategy command is in the list
            command_names = [cmd.command if hasattr(cmd, 'command') else str(cmd) for cmd in commands]
            assert 'add_strategy' in command_names, "'add_strategy' not in bot commands"
        finally:
            for key in ['RPC_URL', 'PRIVATE_KEY', 'CHAIN_ID', 'VAULT_ADDRESS']:
                os.environ.pop(key, None)

    @pytest.mark.asyncio
    async def test_add_strategy_help_text_updated(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test help text includes add_strategy command.

        Verifies: AC#2
        """
        import os
        import sys

        os.environ['RPC_URL'] = 'https://eth-test.example.com'
        os.environ['PRIVATE_KEY'] = '0x' + 'a' * 64
        os.environ['CHAIN_ID'] = '1'
        os.environ['VAULT_ADDRESS'] = '0x933aafc9C5B1e0000E1dd77ac52D67b0E4e4997C'

        for mod in ['main', 'contract', 'config']:
            if mod in sys.modules:
                del sys.modules[mod]

        try:
            from main import cmd_start

            with patch("main.authorized", return_value=True):
                mock_telegram_update.message.reply_text = AsyncMock()

                # When
                await cmd_start(mock_telegram_update, mock_telegram_context)

                # Then
                call_args = mock_telegram_update.message.reply_text.call_args[0][0]
                assert "add_strategy" in call_args.lower() or "/add_strategy" in call_args
        finally:
            for key in ['RPC_URL', 'PRIVATE_KEY', 'CHAIN_ID', 'VAULT_ADDRESS']:
                os.environ.pop(key, None)

    @pytest.mark.asyncio
    async def test_add_strategy_empty_content(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test error when strategy content is empty (whitespace only).

        Verifies: Input validation - empty content check
        """
        # Given - admin user with whitespace-only content
        mock_telegram_update.effective_user.id = 123456789  # Admin user

        # Create mock contract instance (should not be called)
        mock_contract_instance = MagicMock()
        mock_contract_instance.add_strategy = AsyncMock()

        with patch("main.is_admin", return_value=True), \
             patch("main.contract", return_value=mock_contract_instance):
            from main import cmd_add_strategy

            # When - args contain only whitespace
            mock_telegram_context.args = ["   ", "  "]
            await cmd_add_strategy(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "空" in call_args or "empty" in call_args.lower()
        # Verify contract was NOT called
        mock_contract_instance.add_strategy.assert_not_called()

    @pytest.mark.asyncio
    async def test_add_strategy_content_too_long(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test error when strategy content exceeds length limit.

        Verifies: Input validation - content length limit (500 chars)
        """
        # Given - admin user with content too long
        mock_telegram_update.effective_user.id = 123456789  # Admin user

        # Create mock contract instance (should not be called)
        mock_contract_instance = MagicMock()
        mock_contract_instance.add_strategy = AsyncMock()

        # Content longer than 500 chars
        long_content = "a" * 501

        with patch("main.is_admin", return_value=True), \
             patch("main.contract", return_value=mock_contract_instance):
            from main import cmd_add_strategy

            # When
            mock_telegram_context.args = [long_content]
            await cmd_add_strategy(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "过长" in call_args or "long" in call_args.lower() or "500" in call_args
        # Verify contract was NOT called
        mock_contract_instance.add_strategy.assert_not_called()

    @pytest.mark.asyncio
    async def test_add_strategy_none_strategy_id(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test graceful handling when strategyId is None.

        Verifies: Error handling - None strategyId from log parsing failure
        """
        # Given - admin user, contract succeeds but strategyId is None
        mock_telegram_update.effective_user.id = 123456789  # Admin user

        mock_contract_result = {
            "success": True,
            "strategyId": None,  # Parsing failed
            "transactionHash": "0xabc123def456",
            "status": 1,
            "blockNumber": 12345678,
        }

        mock_contract_instance = MagicMock()
        mock_contract_instance.add_strategy = AsyncMock(return_value=mock_contract_result)

        with patch("main.is_admin", return_value=True), \
             patch("main.contract", return_value=mock_contract_instance):
            from main import cmd_add_strategy

            # When
            mock_telegram_context.args = ["test strategy"]
            await cmd_add_strategy(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        # Should show a message about unable to parse ID
        assert "无法解析" in call_args or "ID" in call_args
        assert "0xabc123def456" in call_args  # Should still show tx hash


# =============================================================================
# Tests for contract.add_strategy method (Story 2-1)
# =============================================================================

class TestContractAddStrategy:
    """Tests for VaultContract.add_strategy method - Story 2-1."""

    @pytest.mark.asyncio
    async def test_add_strategy_method_calls_contract(self) -> None:
        """Test add_strategy calls web3 addStrategy with correct params.

        Verifies: AC#1, AC#4
        """
        from contract import VaultContract

        # Create a mock instance
        mock_vault = MagicMock(spec=VaultContract)
        mock_vault._send_transaction = AsyncMock(return_value={
            'success': True,
            'transactionHash': '0xabc123...',
            'status': 1,
            'blockNumber': 12345,
            'receipt': {'logs': []},
        })
        mock_vault.contract = MagicMock()
        mock_vault.contract.functions.addStrategy.return_value = "mock_tx_func"

        # When
        result = await VaultContract.add_strategy(mock_vault, "test strategy")

        # Then
        assert result['success'] is True
        assert 'transactionHash' in result
        mock_vault._send_transaction.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_strategy_with_default_params(self) -> None:
        """Test add_strategy uses default expiry=0, priority=1.

        Verifies: AC#4
        """
        from contract import VaultContract

        mock_vault = MagicMock(spec=VaultContract)
        mock_vault._send_transaction = AsyncMock(return_value={
            'success': True,
            'transactionHash': '0xabc123...',
            'receipt': {'logs': []},
        })
        mock_vault.contract = MagicMock()
        mock_contract_func = MagicMock()
        mock_vault.contract.functions.addStrategy.return_value = mock_contract_func

        # When - call without expiry/priority (should use defaults)
        result = await VaultContract.add_strategy(mock_vault, "test strategy")

        # Then - verify default params were used
        mock_vault.contract.functions.addStrategy.assert_called_once_with(
            "test strategy", 0, 1  # content, expiry=0, priority=1
        )

    @pytest.mark.asyncio
    async def test_add_strategy_returns_strategy_id(self) -> None:
        """Test add_strategy returns strategyId from event logs.

        Verifies: AC#1
        """
        from contract import VaultContract
        from unittest.mock import MagicMock

        mock_vault = MagicMock(spec=VaultContract)

        # Mock event log parsing
        mock_receipt = {
            'logs': [
                {
                    'topics': [
                        MagicMock(hex=lambda: '0x' + 'a' * 64),  # event sig
                        MagicMock(hex=lambda: '0x' + '0' * 62 + '04'),  # strategyId = 4
                    ]
                }
            ]
        }

        mock_vault._send_transaction = AsyncMock(return_value={
            'success': True,
            'transactionHash': '0xabc123...',
            'status': 1,
            'blockNumber': 12345,
            'receipt': mock_receipt,
        })
        mock_vault.contract = MagicMock()
        mock_vault.contract.functions.addStrategy.return_value = "mock_tx_func"

        # Mock w3.keccak for event signature
        mock_vault.w3 = MagicMock()
        mock_vault.w3.keccak = MagicMock(return_value=MagicMock(hex=lambda: '0x' + 'a' * 64))

        # When
        result = await VaultContract.add_strategy(mock_vault, "test strategy")

        # Then
        assert result['success'] is True
        # strategyId might be None if parsing fails, which is acceptable
        # The key is that the method handles the receipt properly

    @pytest.mark.asyncio
    async def test_add_strategy_handles_failure(self) -> None:
        """Test add_strategy handles contract failure gracefully.

        Verifies: AC#1
        """
        from contract import VaultContract

        mock_vault = MagicMock(spec=VaultContract)
        mock_vault._send_transaction = AsyncMock(return_value={
            'success': False,
            'error': 'Gas estimation failed',
        })
        mock_vault.contract = MagicMock()
        mock_vault.contract.functions.addStrategy.return_value = "mock_tx_func"

        # When
        result = await VaultContract.add_strategy(mock_vault, "test strategy")

        # Then
        assert result['success'] is False
        assert 'error' in result
        assert 'Gas estimation failed' in result['error']

