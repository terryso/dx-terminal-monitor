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
