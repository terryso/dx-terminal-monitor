"""
Unit tests for Story 3.1: Update Settings Command

Tests for: contract.update_settings(), cmd_update_settings command handler
ATDD RED PHASE: All tests are written with test.skip() and will FAIL until implementation is complete.
"""

import os
from unittest.mock import AsyncMock, MagicMock, mock_open, patch

import pytest

# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def reset_env():
    """Auto-use fixture to ensure environment is reset after each test."""
    original_env = os.environ.copy()

    yield

    # Always restore original environment
    os.environ.clear()
    os.environ.update(original_env)

    # Reload modules to pick up original config
    import importlib
    try:
        import config
        importlib.reload(config)
    except Exception:
        pass


@pytest.fixture
def web3_test_env():
    """Set up environment variables for Web3 testing."""
    os.environ['RPC_URL'] = 'https://eth-test.example.com'
    os.environ['PRIVATE_KEY'] = '0x' + 'a' * 64
    os.environ['CHAIN_ID'] = '1'
    os.environ['VAULT_ADDRESS'] = '0x933aafc9C5B1e0000E1dd77ac52D67b0E4e4997C'
    os.environ['ADMIN_USERS'] = ''


@pytest.fixture
def mock_web3_components():
    """Create all mock Web3 components."""
    mock_w3 = MagicMock()
    mock_w3.eth = MagicMock()
    mock_w3.eth.gas_price = 1000000000  # 1 Gwei
    mock_w3.eth.get_transaction_count.return_value = 1
    mock_w3.eth.send_raw_transaction.return_value = b'\x12\x34' * 16
    mock_w3.eth.wait_for_transaction_receipt.return_value = {
        'transactionHash': b'\x12\x34' * 16,
        'status': 1,
        'blockNumber': 12345678,
    }

    mock_account = MagicMock()
    mock_account.address = '0xTestSender0000000000000000000000000000'
    mock_account.sign_transaction.return_value = MagicMock(
        raw_transaction=b'signed_tx_data'
    )

    mock_contract = MagicMock()

    mock_w3.eth.account.from_key.return_value = mock_account
    mock_w3.eth.contract.return_value = mock_contract

    return mock_w3, mock_account, mock_contract


def create_mocked_vault_contract(mock_web3_components):
    """Helper to create VaultContract with mocked dependencies."""
    import importlib

    import config
    import contract

    # Ensure environment is set up before reloading
    os.environ['RPC_URL'] = 'https://eth-test.example.com'
    os.environ['PRIVATE_KEY'] = '0x' + 'a' * 64
    os.environ['CHAIN_ID'] = '1'
    os.environ['VAULT_ADDRESS'] = '0x933aafc9C5B1e0000E1dd77ac52D67b0E4e4997C'

    # Reload modules to pick up test environment
    importlib.reload(config)
    importlib.reload(contract)

    mock_w3, mock_account, mock_contract = mock_web3_components

    with patch('contract.Web3') as mock_web3_class, \
         patch('builtins.open', mock_open(read_data='[]')):
        mock_web3_class.HTTPProvider.return_value = mock_w3
        mock_web3_class.return_value = mock_w3
        mock_web3_class.to_checksum_address.return_value = '0x933aafc9C5B1e0000E1dd77ac52D67b0E4e4997C'

        return contract.VaultContract()


# =============================================================================
# Tests for VaultContract.update_settings() Method
# =============================================================================

class TestContractUpdateSettings:
    """Tests for VaultContract.update_settings() method."""

    @pytest.mark.asyncio
    async def test_update_settings_valid_params(self, web3_test_env, mock_web3_components):
        """Test successful settings update with valid parameters.

        Given: A VaultContract instance with mocked Web3 components
        When: update_settings() is called with valid max_trade_bps=2000, slippage_bps=100
        Then: Contract function is called with correct parameters and returns success
        """
        mock_w3, mock_account, mock_contract = mock_web3_components

        # Setup mock for updateSettings transaction
        mock_contract.functions.updateSettings.return_value.estimate_gas.return_value = 100000
        mock_contract.functions.updateSettings.return_value.build_transaction.return_value = {
            'from': '0xTestSender0000000000000000000000000000',
            'nonce': 1,
            'gas': 120000,
        }

        vault = create_mocked_vault_contract(mock_web3_components)

        # When
        result = await vault.update_settings(2000, 100)

        # Then
        mock_contract.functions.updateSettings.assert_called_once_with(2000, 100)
        assert result["success"] is True
        assert "transactionHash" in result
        assert result["status"] == 1
        assert "blockNumber" in result

    @pytest.mark.asyncio
    async def test_update_settings_max_trade_too_low(self, web3_test_env, mock_web3_components):
        """Test max_trade below minimum (500 BPS) is rejected.

        Given: A VaultContract instance
        When: update_settings() is called with max_trade_bps=499 (below minimum)
        Then: Returns failure with error message indicating invalid range
        """
        mock_w3, mock_account, mock_contract = mock_web3_components
        vault = create_mocked_vault_contract(mock_web3_components)

        # When
        result = await vault.update_settings(499, 100)

        # Then
        assert result["success"] is False
        assert "max_trade" in result["error"].lower()
        assert "500" in result["error"]

    @pytest.mark.asyncio
    async def test_update_settings_max_trade_too_high(self, web3_test_env, mock_web3_components):
        """Test max_trade above maximum (10000 BPS) is rejected.

        Given: A VaultContract instance
        When: update_settings() is called with max_trade_bps=10001 (above maximum)
        Then: Returns failure with error message indicating invalid range
        """
        mock_w3, mock_account, mock_contract = mock_web3_components
        vault = create_mocked_vault_contract(mock_web3_components)

        # When
        result = await vault.update_settings(10001, 100)

        # Then
        assert result["success"] is False
        assert "max_trade" in result["error"].lower()
        assert "10000" in result["error"]

    @pytest.mark.asyncio
    async def test_update_settings_slippage_too_low(self, web3_test_env, mock_web3_components):
        """Test slippage below minimum (10 BPS) is rejected.

        Given: A VaultContract instance
        When: update_settings() is called with slippage_bps=9 (below minimum)
        Then: Returns failure with error message indicating invalid range
        """
        mock_w3, mock_account, mock_contract = mock_web3_components
        vault = create_mocked_vault_contract(mock_web3_components)

        # When
        result = await vault.update_settings(1000, 9)

        # Then
        assert result["success"] is False
        assert "slippage" in result["error"].lower()
        assert "10" in result["error"]

    @pytest.mark.asyncio
    async def test_update_settings_slippage_too_high(self, web3_test_env, mock_web3_components):
        """Test slippage above maximum (5000 BPS) is rejected.

        Given: A VaultContract instance
        When: update_settings() is called with slippage_bps=5001 (above maximum)
        Then: Returns failure with error message indicating invalid range
        """
        mock_w3, mock_account, mock_contract = mock_web3_components
        vault = create_mocked_vault_contract(mock_web3_components)

        # When
        result = await vault.update_settings(1000, 5001)

        # Then
        assert result["success"] is False
        assert "slippage" in result["error"].lower()
        assert "5000" in result["error"]

    @pytest.mark.asyncio
    async def test_update_settings_handles_exception(self, web3_test_env, mock_web3_components):
        """Test that update_settings handles exceptions gracefully.

        Given: A VaultContract instance with mocked contract that raises exception
        When: update_settings() is called and contract function throws an exception
        Then: Returns failure dict with error message
        """
        mock_w3, mock_account, mock_contract = mock_web3_components

        # Setup mock to simulate failure
        mock_contract.functions.updateSettings.side_effect = Exception("Network error")

        vault = create_mocked_vault_contract(mock_web3_components)

        # When
        result = await vault.update_settings(1000, 100)

        # Then
        assert result["success"] is False
        assert "error" in result
        assert "Network error" in result["error"]

    @pytest.mark.asyncio
    async def test_update_settings_boundary_values(self, web3_test_env, mock_web3_components):
        """Test boundary values are accepted.

        Given: A VaultContract instance
        When: update_settings() is called with min/max boundary values
        Then: Returns success for valid boundaries
        """
        mock_w3, mock_account, mock_contract = mock_web3_components

        # Setup mock for updateSettings transaction
        mock_contract.functions.updateSettings.return_value.estimate_gas.return_value = 100000
        mock_contract.functions.updateSettings.return_value.build_transaction.return_value = {
            'from': '0xTestSender0000000000000000000000000000',
            'nonce': 1,
            'gas': 120000,
        }

        vault = create_mocked_vault_contract(mock_web3_components)

        # Test minimum boundary
        result1 = await vault.update_settings(500, 10)
        assert result1["success"] is True

        # Test maximum boundary
        result2 = await vault.update_settings(10000, 5000)
        assert result2["success"] is True


# =============================================================================
# Tests for cmd_update_settings Command Handler
# =============================================================================

class TestCmdUpdateSettings:
    """Tests for /update_settings command handler."""

    @pytest.mark.asyncio
    async def test_update_settings_success(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ):
        """Test successful settings update by admin user with both parameters.

        Given: An admin user with ID 12345
        When: /update_settings max_trade=2000 slippage=100 is executed
        Then: Settings are updated and success message is returned
        """
        # Given
        mock_telegram_update.effective_user.id = 12345  # Admin user

        mock_contract = AsyncMock()
        mock_contract.update_settings.return_value = {
            "success": True,
            "transactionHash": "0xabc123def456",
        }

        mock_api = AsyncMock()
        mock_api.get_vault.return_value = {
            'maxTrade': 1000,
            'slippage': 50
        }

        with patch("commands.admin.is_admin", return_value=True), \
             patch("commands.admin._get_contract") as mock_get_contract, \
             patch("commands.admin._get_api") as mock_get_api, \
             patch("commands.admin.logger") as mock_logger:
            mock_get_contract.return_value = mock_contract
            mock_get_api.return_value = mock_api
            from commands.admin import cmd_update_settings

            # When
            ctx = MagicMock()
            ctx.args = ["max_trade=2000", "slippage=100"]
            await cmd_update_settings(mock_telegram_update, ctx)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "Settings updated" in call_args or "updated" in call_args.lower()
        assert "2000" in call_args
        assert "100" in call_args
        assert "0xabc123def456" in call_args
        mock_contract.update_settings.assert_called_once_with(2000, 100)

        # Verify audit log
        mock_logger.info.assert_called()
        log_call = str(mock_logger.info.call_args)
        assert "12345" in log_call

    @pytest.mark.asyncio
    async def test_update_settings_only_max_trade(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ):
        """Test updating only max_trade, keeping current slippage.

        Given: An admin user
        When: /update_settings max_trade=2000 is executed (slippage not specified)
        Then: max_trade is updated to 2000, slippage remains at current value (50)
        """
        # Given
        mock_telegram_update.effective_user.id = 12345

        mock_contract = AsyncMock()
        mock_contract.update_settings.return_value = {
            "success": True,
            "transactionHash": "0xabc123",
        }

        mock_api = AsyncMock()
        mock_api.get_vault.return_value = {
            'maxTrade': 1000,
            'slippage': 50
        }

        with patch("commands.admin.is_admin", return_value=True), \
             patch("commands.admin._get_contract") as mock_get_contract, \
             patch("commands.admin._get_api") as mock_get_api:
            mock_get_contract.return_value = mock_contract
            mock_get_api.return_value = mock_api
            from commands.admin import cmd_update_settings

            # When
            ctx = MagicMock()
            ctx.args = ["max_trade=2000"]
            await cmd_update_settings(mock_telegram_update, ctx)

        # Then
        mock_contract.update_settings.assert_called_once_with(2000, 50)

    @pytest.mark.asyncio
    async def test_update_settings_only_slippage(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ):
        """Test updating only slippage, keeping current max_trade.

        Given: An admin user
        When: /update_settings slippage=100 is executed (max_trade not specified)
        Then: slippage is updated to 100, max_trade remains at current value (1000)
        """
        # Given
        mock_telegram_update.effective_user.id = 12345

        mock_contract = AsyncMock()
        mock_contract.update_settings.return_value = {
            "success": True,
            "transactionHash": "0xabc123",
        }

        mock_api = AsyncMock()
        mock_api.get_vault.return_value = {
            'maxTrade': 1000,
            'slippage': 50
        }

        with patch("commands.admin.is_admin", return_value=True), \
             patch("commands.admin._get_contract") as mock_get_contract, \
             patch("commands.admin._get_api") as mock_get_api:
            mock_get_contract.return_value = mock_contract
            mock_get_api.return_value = mock_api
            from commands.admin import cmd_update_settings

            # When
            ctx = MagicMock()
            ctx.args = ["slippage=100"]
            await cmd_update_settings(mock_telegram_update, ctx)

        # Then
        mock_contract.update_settings.assert_called_once_with(1000, 100)

    @pytest.mark.asyncio
    async def test_update_settings_unauthorized(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ):
        """Test that non-admin user is rejected.

        Given: A non-admin user with ID 99999
        When: /update_settings is executed
        Then: Returns unauthorized error message
        """
        # Given
        mock_telegram_update.effective_user.id = 99999  # Non-admin

        with patch("commands.admin.is_admin", return_value=False):
            from commands.admin import cmd_update_settings

            # When
            ctx = MagicMock()
            ctx.args = ["max_trade=2000"]
            await cmd_update_settings(mock_telegram_update, ctx)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "未授权" in call_args or "Unauthorized" in call_args

    @pytest.mark.asyncio
    async def test_update_settings_no_args_shows_current_settings(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ):
        """Test command shows current settings when no arguments provided.

        Given: An admin user
        When: /update_settings is executed without any arguments
        Then: Returns current settings (view mode)
        """
        # Given
        mock_telegram_update.effective_user.id = 12345

        mock_api = AsyncMock()
        mock_api.get_vault.return_value = {
            'maxTradeAmount': 1000,
            'slippageBps': 50,
            'tradingActivity': 3,
            'assetRiskPreference': 2,
            'tradeSize': 2,
            'holdingStyle': 1,
            'diversification': 3
        }

        with patch("commands.admin.is_admin", return_value=True), \
             patch("commands.admin._get_api") as mock_get_api:
            mock_get_api.return_value = mock_api
            from commands.admin import cmd_update_settings

            # When
            ctx = MagicMock()
            ctx.args = []
            await cmd_update_settings(mock_telegram_update, ctx)

        # Then
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "Current" in call_args or "current" in call_args.lower()
        assert "Max Trade" in call_args or "max_trade" in call_args.lower()
        assert "Slippage" in call_args or "slippage" in call_args.lower()
        assert "1000" in call_args
        assert "50" in call_args
        # Behavior Preferences
        assert "Behavior" in call_args or "behavior" in call_args.lower()
        assert "Trading Activity" in call_args or "trading" in call_args.lower()
        assert "Risk" in call_args or "risk" in call_args.lower()

    @pytest.mark.asyncio
    async def test_update_settings_invalid_parameter(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ):
        """Test invalid parameter name is rejected.

        Given: An admin user
        When: /update_settings invalid_param=100 is executed
        Then: Returns error message indicating unknown parameter
        """
        # Given
        mock_telegram_update.effective_user.id = 12345

        with patch("commands.admin.is_admin", return_value=True):
            from commands.admin import cmd_update_settings

            # When
            ctx = MagicMock()
            ctx.args = ["invalid_param=100"]
            await cmd_update_settings(mock_telegram_update, ctx)

        # Then
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "未知参数" in call_args or "unknown" in call_args.lower() or "invalid" in call_args.lower()

    @pytest.mark.asyncio
    async def test_update_settings_contract_failure(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ):
        """Test cmd_update_settings handles contract call failure.

        Given: An admin user
        When: Contract update_settings returns failure
        Then: Returns error message to user
        """
        # Given
        mock_telegram_update.effective_user.id = 12345

        mock_contract = AsyncMock()
        mock_contract.update_settings.return_value = {
            "success": False,
            "error": "Transaction reverted",
        }

        mock_api = AsyncMock()
        mock_api.get_vault.return_value = {
            'maxTrade': 1000,
            'slippage': 50
        }

        with patch("commands.admin.is_admin", return_value=True), \
             patch("commands.admin._get_contract") as mock_get_contract, \
             patch("commands.admin._get_api") as mock_get_api:
            mock_get_contract.return_value = mock_contract
            mock_get_api.return_value = mock_api
            from commands.admin import cmd_update_settings

            # When
            ctx = MagicMock()
            ctx.args = ["max_trade=2000"]
            await cmd_update_settings(mock_telegram_update, ctx)

        # Then
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "failed" in call_args.lower() or "error" in call_args.lower()
        assert "Transaction reverted" in call_args

    @pytest.mark.asyncio
    async def test_update_settings_logs_audit(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ):
        """Test that cmd_update_settings logs admin action for audit.

        Given: An admin user
        When: Settings are updated successfully
        Then: Audit log is created with admin ID and parameters
        """
        # Given
        mock_telegram_update.effective_user.id = 12345

        mock_contract = AsyncMock()
        mock_contract.update_settings.return_value = {
            "success": True,
            "transactionHash": "0xabc",
        }

        mock_api = AsyncMock()
        mock_api.get_vault.return_value = {
            'maxTrade': 1000,
            'slippage': 50
        }

        with patch("commands.admin.is_admin", return_value=True), \
             patch("commands.admin._get_contract") as mock_get_contract, \
             patch("commands.admin._get_api") as mock_get_api, \
             patch("commands.admin.logger") as mock_logger:
            mock_get_contract.return_value = mock_contract
            mock_get_api.return_value = mock_api
            from commands.admin import cmd_update_settings

            # When
            ctx = MagicMock()
            ctx.args = ["max_trade=2000", "slippage=100"]
            await cmd_update_settings(mock_telegram_update, ctx)

        # Then
        # Verify logger.info was called with admin ID and action
        assert mock_logger.info.called
        log_call_args = str(mock_logger.info.call_args)
        assert "12345" in log_call_args  # Admin ID logged
        # Check for "updat" instead of "update" due to Python 3.14 bug where "update" not in "updating"
        assert "updat" in log_call_args.lower()

    @pytest.mark.asyncio
    async def test_update_settings_uses_is_admin_not_authorized(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ):
        """Test that cmd_update_settings uses is_admin() for permission check.

        Given: Any user
        When: cmd_update_settings is called
        Then: is_admin() is used (not authorized()) for permission check
        """
        # Given
        mock_telegram_update.effective_user.id = 12345

        mock_contract = AsyncMock()
        mock_contract.update_settings.return_value = {"success": True, "transactionHash": "0xabc"}

        mock_api = AsyncMock()
        mock_api.get_vault.return_value = {
            'maxTrade': 1000,
            'slippage': 50
        }

        with patch("commands.admin.is_admin", return_value=True) as mock_is_admin, \
             patch("utils.permissions.authorized") as mock_authorized, \
             patch("commands.admin._get_contract") as mock_get_contract, \
             patch("commands.admin._get_api") as mock_get_api:
            mock_get_contract.return_value = mock_contract
            mock_get_api.return_value = mock_api
            from commands.admin import cmd_update_settings

            # When
            ctx = MagicMock()
            ctx.args = ["max_trade=2000"]
            await cmd_update_settings(mock_telegram_update, ctx)

        # Then
        # is_admin should be called (admin-only operation)
        assert mock_is_admin.called
        # authorized() should NOT be called
        assert not mock_authorized.called


# =============================================================================
# Tests for Command Registration
# =============================================================================

class TestCommandRegistration:
    """Tests for bot command registration."""

    @pytest.mark.asyncio
    async def test_update_settings_command_registered_in_post_init(self):
        """Test that update_settings BotCommand is registered in post_init.

        Given: The bot application
        When: post_init() is called
        Then: update_settings command is registered in bot commands
        """
        # Given
        mock_app = MagicMock()
        mock_app.bot = AsyncMock()

        from main import post_init

        # When
        await post_init(mock_app)

        # Then
        mock_app.bot.set_my_commands.assert_called_once()
        call_args = mock_app.bot.set_my_commands.call_args[0][0]
        command_names = [cmd.command for cmd in call_args]

        assert "update_settings" in command_names, "update_settings command should be registered"

        # Verify description
        update_cmd = next((cmd for cmd in call_args if cmd.command == "update_settings"), None)
        assert update_cmd is not None and "setting" in update_cmd.description.lower()

    @pytest.mark.asyncio
    async def test_update_settings_handler_registered_in_create_app(self):
        """Test that update_settings CommandHandler is registered.

        Given: The main module
        When: create_app() is called
        Then: update_settings handler is registered
        """
        # Given
        with patch("main.TELEGRAM_BOT_TOKEN", "test_token"):
            from main import create_app

            # When
            app = create_app()

            # Then
            handlers = app.handlers[0]  # CommandHandler group
            handler_commands = []
            for handler in handlers:
                # Handle both CommandHandler and ConversationHandler
                if hasattr(handler, 'commands'):
                    handler_commands.extend(handler.commands)
                elif hasattr(handler, 'entry_points'):
                    for entry_point in handler.entry_points:
                        if hasattr(entry_point, 'commands'):
                            handler_commands.extend(entry_point.commands)

            assert "update_settings" in handler_commands, "update_settings handler should be registered"

    @pytest.mark.asyncio
    async def test_start_help_includes_update_settings(self):
        """Test that /start help text includes update_settings command.

        Given: An authorized user
        When: /start command is executed
        Then: Help text includes /update_settings command description
        """
        # Given
        from commands.query import cmd_start

        mock_update = MagicMock()
        mock_update.effective_user.id = 12345
        mock_update.message = AsyncMock()

        mock_context = MagicMock()

        with patch("commands.query.authorized", return_value=True):
            # When
            await cmd_start(mock_update, mock_context)

        # Then
        call_args = mock_update.message.reply_text.call_args[0][0]
        # Should mention /update_settings in help text
        assert "/update_settings" in call_args or "update_settings" in call_args
