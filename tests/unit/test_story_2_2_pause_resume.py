"""
Unit tests for Story 2.2: Pause/Resume Agent Trading Commands

Tests for: contract.pause_vault(), cmd_pause, cmd_resume
"""

import os
from unittest.mock import MagicMock, AsyncMock, patch, mock_open

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
# Tests for VaultContract.pause_vault() Method
# =============================================================================

class TestContractPauseVault:
    """Tests for VaultContract.pause_vault() method."""

    @pytest.mark.asyncio
    async def test_pause_vault_calls_web3_function(self, web3_test_env, mock_web3_components):
        """Test that pause_vault(True) calls the correct web3 function."""
        mock_w3, mock_account, mock_contract = mock_web3_components

        # Setup mock for pauseVault transaction
        mock_contract.functions.pauseVault.return_value.estimate_gas.return_value = 100000
        mock_contract.functions.pauseVault.return_value.build_transaction.return_value = {
            'from': '0xTestSender0000000000000000000000000000',
            'nonce': 1,
            'gas': 120000,
        }

        vault = create_mocked_vault_contract(mock_web3_components)

        # When
        result = await vault.pause_vault(True)

        # Then
        mock_contract.functions.pauseVault.assert_called_once_with(True)
        assert result is not None

    @pytest.mark.asyncio
    async def test_resume_vault_calls_web3_function(self, web3_test_env, mock_web3_components):
        """Test that pause_vault(False) calls the correct web3 function."""
        mock_w3, mock_account, mock_contract = mock_web3_components

        # Setup mock for pauseVault transaction
        mock_contract.functions.pauseVault.return_value.estimate_gas.return_value = 100000
        mock_contract.functions.pauseVault.return_value.build_transaction.return_value = {
            'from': '0xTestSender0000000000000000000000000000',
            'nonce': 1,
            'gas': 120000,
        }

        vault = create_mocked_vault_contract(mock_web3_components)

        # When
        result = await vault.pause_vault(False)

        # Then
        mock_contract.functions.pauseVault.assert_called_once_with(False)
        assert result is not None

    @pytest.mark.asyncio
    async def test_pause_vault_returns_success_dict(self, web3_test_env, mock_web3_components):
        """Test that pause_vault returns standard result dictionary."""
        mock_w3, mock_account, mock_contract = mock_web3_components

        # Setup mock for pauseVault transaction
        mock_contract.functions.pauseVault.return_value.estimate_gas.return_value = 100000
        mock_contract.functions.pauseVault.return_value.build_transaction.return_value = {
            'from': '0xTestSender0000000000000000000000000000',
            'nonce': 1,
            'gas': 120000,
        }

        vault = create_mocked_vault_contract(mock_web3_components)

        # When
        result = await vault.pause_vault(True)

        # Then
        assert result["success"] is True
        assert "transactionHash" in result
        assert result["status"] == 1
        assert "blockNumber" in result

    @pytest.mark.asyncio
    async def test_pause_vault_handles_exception(self, web3_test_env, mock_web3_components):
        """Test that pause_vault handles exceptions gracefully."""
        mock_w3, mock_account, mock_contract = mock_web3_components

        # Setup mock to simulate failure
        mock_contract.functions.pauseVault.side_effect = Exception("Network error")

        vault = create_mocked_vault_contract(mock_web3_components)

        # When
        result = await vault.pause_vault(True)

        # Then
        assert result["success"] is False
        assert "error" in result
        assert "Network error" in result["error"]

    @pytest.mark.asyncio
    async def test_pause_vault_transaction_format(self, web3_test_env, mock_web3_components):
        """Test that _send_transaction receives correct transaction function."""
        mock_w3, mock_account, mock_contract = mock_web3_components

        # Setup mock for pauseVault transaction
        mock_contract.functions.pauseVault.return_value.estimate_gas.return_value = 100000
        mock_contract.functions.pauseVault.return_value.build_transaction.return_value = {
            'from': '0xTestSender0000000000000000000000000000',
            'nonce': 1,
            'gas': 120000,
        }

        vault = create_mocked_vault_contract(mock_web3_components)

        # When
        await vault.pause_vault(True)

        # Then
        # Verify the contract was called with correct parameters
        mock_contract.functions.pauseVault.assert_called_once_with(True)


# =============================================================================
# Tests for cmd_pause Command Handler
# =============================================================================

class TestCmdPause:
    """Tests for /pause command handler."""

    @pytest.mark.asyncio
    async def test_cmd_pause_success(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ):
        """Test successful vault pause by admin user."""
        # Given
        mock_telegram_update.effective_user.id = 12345  # Admin user

        mock_contract = AsyncMock()
        mock_contract.pause_vault.return_value = {
            "success": True,
            "transactionHash": "0xabc123def456",
        }

        mock_api = AsyncMock()
        mock_api.get_vault.return_value = {"paused": False}  # Not already paused

        with patch("main.is_admin", return_value=True), \
             patch("main.contract", return_value=mock_contract), \
             patch("main.api", mock_api), \
             patch("main.logger") as mock_logger:
            from main import cmd_pause

            # When
            await cmd_pause(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "⏸️" in call_args
        assert "暂停" in call_args
        assert "0xabc123def456" in call_args
        mock_contract.pause_vault.assert_called_once_with(True)

        # Verify audit log
        mock_logger.info.assert_called()
        log_call = str(mock_logger.info.call_args)
        assert "12345" in log_call
        assert "paus" in log_call.lower()

    @pytest.mark.asyncio
    async def test_cmd_pause_unauthorized(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ):
        """Test that non-admin user cannot pause vault."""
        # Given
        mock_telegram_update.effective_user.id = 99999  # Non-admin user

        with patch("main.is_admin", return_value=False):
            from main import cmd_pause

            # When
            await cmd_pause(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "未授权" in call_args or "Unauthorized" in call_args

    @pytest.mark.asyncio
    async def test_cmd_pause_contract_failure(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ):
        """Test cmd_pause handles contract call failure."""
        # Given
        mock_telegram_update.effective_user.id = 12345  # Admin user

        mock_contract = AsyncMock()
        mock_contract.pause_vault.return_value = {
            "success": False,
            "error": "Insufficient gas",
        }

        mock_api = AsyncMock()
        mock_api.get_vault.return_value = {"paused": False}  # Not already paused

        with patch("main.is_admin", return_value=True), \
             patch("main.contract", return_value=mock_contract), \
             patch("main.api", mock_api):
            from main import cmd_pause

            # When
            await cmd_pause(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "失败" in call_args or "error" in call_args.lower()
        assert "Insufficient gas" in call_args

    @pytest.mark.asyncio
    async def test_cmd_pause_logs_audit(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ):
        """Test that cmd_pause logs admin action for audit."""
        # Given
        mock_telegram_update.effective_user.id = 12345

        mock_contract = AsyncMock()
        mock_contract.pause_vault.return_value = {"success": True, "transactionHash": "0xabc"}

        mock_api = AsyncMock()
        mock_api.get_vault.return_value = {"paused": False}

        with patch("main.is_admin", return_value=True), \
             patch("main.contract", return_value=mock_contract), \
             patch("main.api", mock_api), \
             patch("main.logger") as mock_logger:
            from main import cmd_pause

            # When
            await cmd_pause(mock_telegram_update, mock_telegram_context)

        # Then
        # Verify logger.info was called with admin ID and action
        assert mock_logger.info.called
        log_call_args = str(mock_logger.info.call_args)
        assert "12345" in log_call_args  # Admin ID logged
        assert "pause" in log_call_args.lower() or "paus" in log_call_args.lower()

    @pytest.mark.asyncio
    async def test_cmd_pause_already_paused(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ):
        """Test cmd_pause returns early if vault is already paused (idempotency)."""
        # Given
        mock_telegram_update.effective_user.id = 12345  # Admin user

        mock_api = AsyncMock()
        mock_api.get_vault.return_value = {"paused": True}  # Already paused

        with patch("main.is_admin", return_value=True), \
             patch("main.api", mock_api):
            from main import cmd_pause

            # When
            await cmd_pause(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "已经" in call_args or "already" in call_args.lower()
        assert "暂停" in call_args


# =============================================================================
# Tests for cmd_resume Command Handler
# =============================================================================

class TestCmdResume:
    """Tests for /resume command handler."""

    @pytest.mark.asyncio
    async def test_cmd_resume_success(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ):
        """Test successful vault resume by admin user."""
        # Given
        mock_telegram_update.effective_user.id = 12345  # Admin user

        mock_contract = AsyncMock()
        mock_contract.pause_vault.return_value = {
            "success": True,
            "transactionHash": "0xxyz789abc",
        }

        mock_api = AsyncMock()
        mock_api.get_vault.return_value = {"paused": True}  # Currently paused

        with patch("main.is_admin", return_value=True), \
             patch("main.contract", return_value=mock_contract), \
             patch("main.api", mock_api), \
             patch("main.logger") as mock_logger:
            from main import cmd_resume

            # When
            await cmd_resume(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "▶️" in call_args
        assert "恢复" in call_args
        assert "0xxyz789abc" in call_args
        mock_contract.pause_vault.assert_called_once_with(False)

        # Verify audit log
        mock_logger.info.assert_called()
        log_call = str(mock_logger.info.call_args)
        assert "12345" in log_call
        assert "resum" in log_call.lower()

    @pytest.mark.asyncio
    async def test_cmd_resume_unauthorized(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ):
        """Test that non-admin user cannot resume vault."""
        # Given
        mock_telegram_update.effective_user.id = 99999  # Non-admin user

        with patch("main.is_admin", return_value=False):
            from main import cmd_resume

            # When
            await cmd_resume(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "未授权" in call_args or "Unauthorized" in call_args

    @pytest.mark.asyncio
    async def test_cmd_resume_contract_failure(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ):
        """Test cmd_resume handles contract call failure."""
        # Given
        mock_telegram_update.effective_user.id = 12345  # Admin user

        mock_contract = AsyncMock()
        mock_contract.pause_vault.return_value = {
            "success": False,
            "error": "Transaction reverted",
        }

        mock_api = AsyncMock()
        mock_api.get_vault.return_value = {"paused": True}  # Currently paused

        with patch("main.is_admin", return_value=True), \
             patch("main.contract", return_value=mock_contract), \
             patch("main.api", mock_api):
            from main import cmd_resume

            # When
            await cmd_resume(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "失败" in call_args or "error" in call_args.lower()
        assert "Transaction reverted" in call_args

    @pytest.mark.asyncio
    async def test_cmd_resume_logs_audit(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ):
        """Test that cmd_resume logs admin action for audit."""
        # Given
        mock_telegram_update.effective_user.id = 12345

        mock_contract = AsyncMock()
        mock_contract.pause_vault.return_value = {"success": True, "transactionHash": "0xxyz"}

        mock_api = AsyncMock()
        mock_api.get_vault.return_value = {"paused": True}

        with patch("main.is_admin", return_value=True), \
             patch("main.contract", return_value=mock_contract), \
             patch("main.api", mock_api), \
             patch("main.logger") as mock_logger:
            from main import cmd_resume

            # When
            await cmd_resume(mock_telegram_update, mock_telegram_context)

        # Then
        # Verify logger.info was called with admin ID and action
        assert mock_logger.info.called
        log_call_args = str(mock_logger.info.call_args)
        assert "12345" in log_call_args  # Admin ID logged
        assert "resum" in log_call_args.lower()

    @pytest.mark.asyncio
    async def test_cmd_resume_already_running(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ):
        """Test cmd_resume returns early if vault is already running (idempotency)."""
        # Given
        mock_telegram_update.effective_user.id = 12345  # Admin user

        mock_api = AsyncMock()
        mock_api.get_vault.return_value = {"paused": False}  # Already running

        with patch("main.is_admin", return_value=True), \
             patch("main.api", mock_api):
            from main import cmd_resume

            # When
            await cmd_resume(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "已经" in call_args or "already" in call_args.lower()
        assert "运行" in call_args


# =============================================================================
# Tests for Permission Checks
# =============================================================================

class TestPermissionChecks:
    """Tests for admin permission verification."""

    @pytest.mark.asyncio
    async def test_pause_uses_is_admin_not_authorized(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ):
        """Test that cmd_pause uses is_admin() for permission check."""
        # Given
        mock_telegram_update.effective_user.id = 12345

        mock_contract = AsyncMock()
        mock_contract.pause_vault.return_value = {"success": True, "transactionHash": "0xabc"}

        mock_api = AsyncMock()
        mock_api.get_vault.return_value = {"paused": False}

        with patch("main.is_admin", return_value=True) as mock_is_admin, \
             patch("main.authorized") as mock_authorized, \
             patch("main.contract", return_value=mock_contract), \
             patch("main.api", mock_api):
            from main import cmd_pause

            # When
            await cmd_pause(mock_telegram_update, mock_telegram_context)

        # Then
        # is_admin should be called (admin-only operation)
        assert mock_is_admin.called
        # authorized() should NOT be called
        assert not mock_authorized.called

    @pytest.mark.asyncio
    async def test_resume_uses_is_admin_not_authorized(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ):
        """Test that cmd_resume uses is_admin() for permission check."""
        # Given
        mock_telegram_update.effective_user.id = 12345

        mock_contract = AsyncMock()
        mock_contract.pause_vault.return_value = {"success": True, "transactionHash": "0xabc"}

        mock_api = AsyncMock()
        mock_api.get_vault.return_value = {"paused": True}

        with patch("main.is_admin", return_value=True) as mock_is_admin, \
             patch("main.authorized") as mock_authorized, \
             patch("main.contract", return_value=mock_contract), \
             patch("main.api", mock_api):
            from main import cmd_resume

            # When
            await cmd_resume(mock_telegram_update, mock_telegram_context)

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
    async def test_pause_resume_commands_registered_in_post_init(self):
        """Test that pause and resume BotCommands are registered in post_init."""
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

        assert "pause" in command_names, "pause command should be registered"
        assert "resume" in command_names, "resume command should be registered"

        # Verify descriptions
        pause_cmd = next((cmd for cmd in call_args if cmd.command == "pause"), None)
        resume_cmd = next((cmd for cmd in call_args if cmd.command == "resume"), None)
        assert pause_cmd is not None and "pause" in pause_cmd.description.lower()
        assert resume_cmd is not None and "resume" in resume_cmd.description.lower()

    @pytest.mark.asyncio
    async def test_pause_resume_handlers_registered_in_create_app(self):
        """Test that pause and resume CommandHandlers are registered."""
        # Given
        with patch("main.TELEGRAM_BOT_TOKEN", "test_token"):
            from main import create_app

            # When
            app = create_app()

            # Then
            handlers = app.handlers[0]  # CommandHandler group
            handler_commands = []
            for handler in handlers:
                handler_commands.extend(handler.commands)

            assert "pause" in handler_commands, "pause handler should be registered"
            assert "resume" in handler_commands, "resume handler should be registered"

    @pytest.mark.asyncio
    async def test_start_help_includes_pause_resume(self):
        """Test that /start help text includes pause and resume commands."""
        # Given
        from main import cmd_start

        mock_update = MagicMock()
        mock_update.effective_user.id = 12345
        mock_update.message = AsyncMock()

        mock_context = MagicMock()

        with patch("main.authorized", return_value=True):
            # When
            await cmd_start(mock_update, mock_context)

        # Then
        call_args = mock_update.message.reply_text.call_args[0][0]
        # Should mention /pause and /resume in help text
        assert "/pause" in call_args or "pause" in call_args.lower()
        assert "/resume" in call_args or "resume" in call_args.lower()
