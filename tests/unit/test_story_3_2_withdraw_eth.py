"""
Unit tests for Story 3.2: Withdraw ETH Command

Tests for: contract.withdraw_eth(), cmd_withdraw command handler
GREEN PHASE: Tests are now enabled after implementation is complete.
"""

import os
from unittest.mock import MagicMock, AsyncMock, patch, mock_open
import pytest
from web3 import Web3


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
    os.environ['ADMIN_USERS'] = '123456789'


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


@pytest.fixture
def mock_update():
    """Create mock Telegram Update object."""
    update = MagicMock()
    update.effective_user = MagicMock()
    update.effective_user.id = 123456789
    update.message = AsyncMock()
    return update


@pytest.fixture
def mock_context():
    """Create mock Telegram Context object."""
    context = MagicMock()
    context.args = []
    context.bot = AsyncMock()
    return context


@pytest.fixture
def mock_vault_with_balance():
    """Mock vault API with sufficient balance."""
    return {'balance': '2.0'}


@pytest.fixture
def mock_vault_low_balance():
    """Mock vault API with insufficient balance."""
    return {'balance': '0.3'}


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

        vault_contract = contract.VaultContract()

        # Replace internal components with mocks
        vault_contract.w3 = mock_w3
        vault_contract.account = mock_account
        vault_contract.contract = mock_contract

        return vault_contract


# ============================================================================
# Test Class: TestCmdWithdraw (Command Handler Tests)
# ============================================================================

class TestCmdWithdraw:
    """Tests for cmd_withdraw command handler."""

    @pytest.mark.asyncio
    async def test_withdraw_success_flow(self, mock_update, mock_context, web3_test_env, mock_web3_components, mock_vault_with_balance):
        """Test successful ETH withdrawal with confirmation."""
        # Given
        mock_update.effective_user.id = 123456789  # Admin user
        mock_context.args = ["0.5"]

        # Mock API to return sufficient balance
        mock_api = AsyncMock()
        mock_api.get_vault.return_value = mock_vault_with_balance

        # Mock contract to return success
        mock_contract_instance = create_mocked_vault_contract(mock_web3_components)
        mock_contract_instance.contract.functions.withdrawETH.return_value.build_transaction.return_value = {}
        mock_contract_instance.contract.functions.withdrawETH.return_value.estimate_gas.return_value = 100000

        with patch("main.is_admin", return_value=True), \
             patch("main.contract", return_value=mock_contract_instance), \
             patch("main.api", mock_api):
            from main import cmd_withdraw, handle_withdraw_confirm, _pending_withdrawals

            # Clear any pending withdrawals
            _pending_withdrawals.clear()

            # When - Start withdrawal
            result = await cmd_withdraw(mock_update, mock_context)
            assert result == 1  # WAITING_CONFIRMATION

            # When - Confirm withdrawal
            mock_update.message.text = "Y"
            result = await handle_withdraw_confirm(mock_update, mock_context)
            assert result == -1  # END

        # Then
        mock_contract_instance.contract.functions.withdrawETH.assert_called_once_with(
            int(Web3.to_wei(0.5, 'ether'))
        )

    @pytest.mark.asyncio
    async def test_withdraw_insufficient_balance(self, mock_update, mock_context, web3_test_env, mock_vault_low_balance):
        """Test withdrawal with insufficient balance."""
        # Given
        mock_update.effective_user.id = 123456789
        mock_context.args = ["0.5"]

        # Mock API to return low balance
        mock_api = AsyncMock()
        mock_api.get_vault.return_value = mock_vault_low_balance

        with patch("main.is_admin", return_value=True), \
             patch("main.api", mock_api):
            from main import cmd_withdraw

            # When
            result = await cmd_withdraw(mock_update, mock_context)

        # Then
        assert result == -1  # END (rejected)
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "余额不足" in call_args or "0.3" in call_args

    @pytest.mark.asyncio
    async def test_withdraw_unauthorized(self, mock_update, mock_context, web3_test_env):
        """Test non-admin user is rejected."""
        # Given
        mock_update.effective_user.id = 99999  # Non-admin
        mock_context.args = ["0.5"]

        with patch("main.is_admin", return_value=False):
            from main import cmd_withdraw

            # When
            result = await cmd_withdraw(mock_update, mock_context)

        # Then
        assert result == -1  # END
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "未授权" in call_args

    @pytest.mark.asyncio
    async def test_withdraw_cancel_confirmation(self, mock_update, mock_context, web3_test_env, mock_vault_with_balance):
        """Test cancelling withdrawal during confirmation."""
        # Given
        mock_update.effective_user.id = 123456789
        mock_context.args = ["0.5"]

        mock_api = AsyncMock()
        mock_api.get_vault.return_value = mock_vault_with_balance

        with patch("main.is_admin", return_value=True), \
             patch("main.api", mock_api):
            from main import cmd_withdraw, handle_withdraw_confirm, _pending_withdrawals

            # Clear any pending withdrawals
            _pending_withdrawals.clear()

            # Start withdrawal
            await cmd_withdraw(mock_update, mock_context)

            # When - Cancel
            mock_update.message.text = "N"
            result = await handle_withdraw_confirm(mock_update, mock_context)

        # Then
        assert result == -1  # END
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "取消" in call_args

    @pytest.mark.asyncio
    async def test_withdraw_invalid_amount(self, mock_update, mock_context, web3_test_env):
        """Test invalid amount format."""
        # Given
        mock_update.effective_user.id = 123456789
        mock_context.args = ["abc"]

        with patch("main.is_admin", return_value=True):
            from main import cmd_withdraw

            # When
            result = await cmd_withdraw(mock_update, mock_context)

        # Then
        assert result == -1  # END
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "无效" in call_args or "数字" in call_args

    @pytest.mark.asyncio
    async def test_withdraw_missing_amount(self, mock_update, mock_context, web3_test_env):
        """Test missing amount parameter."""
        # Given
        mock_update.effective_user.id = 123456789
        mock_context.args = []

        with patch("main.is_admin", return_value=True):
            from main import cmd_withdraw

            # When
            result = await cmd_withdraw(mock_update, mock_context)

        # Then
        assert result == -1  # END
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "用法" in call_args or "/withdraw" in call_args

    @pytest.mark.asyncio
    async def test_withdraw_negative_amount(self, mock_update, mock_context, web3_test_env):
        """Test negative amount is rejected."""
        # Given
        mock_update.effective_user.id = 123456789
        mock_context.args = ["-0.5"]

        with patch("main.is_admin", return_value=True):
            from main import cmd_withdraw

            # When
            result = await cmd_withdraw(mock_update, mock_context)

        # Then
        assert result == -1  # END
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "大于 0" in call_args or "必须" in call_args

    @pytest.mark.asyncio
    async def test_withdraw_excessive_precision(self, mock_update, mock_context, web3_test_env):
        """Test amount with excessive decimal precision is rejected."""
        # Given
        mock_update.effective_user.id = 123456789
        mock_context.args = ["0.1234567"]  # 7 decimal places

        with patch("main.is_admin", return_value=True):
            from main import cmd_withdraw

            # When
            result = await cmd_withdraw(mock_update, mock_context)

        # Then
        assert result == -1  # END
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "精度" in call_args or "小数" in call_args

    @pytest.mark.asyncio
    async def test_withdraw_session_expired(self, mock_update, mock_context, web3_test_env, mock_vault_with_balance):
        """Test handling of expired withdrawal session."""
        # Given
        mock_update.effective_user.id = 123456789
        mock_context.args = ["0.5"]

        mock_api = AsyncMock()
        mock_api.get_vault.return_value = mock_vault_with_balance

        with patch("main.is_admin", return_value=True), \
             patch("main.api", mock_api):
            from main import cmd_withdraw, handle_withdraw_confirm, _pending_withdrawals

            # Clear any pending withdrawals
            _pending_withdrawals.clear()

            # Start withdrawal
            await cmd_withdraw(mock_update, mock_context)

            # Simulate session expiration by clearing pending withdrawals
            _pending_withdrawals.clear()

            # When - Try to confirm without pending withdrawal
            mock_update.message.text = "Y"
            result = await handle_withdraw_confirm(mock_update, mock_context)

        # Then
        assert result == -1  # END
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "过期" in call_args or "重新" in call_args

    @pytest.mark.asyncio
    async def test_withdraw_contract_failure(self, mock_update, mock_context, web3_test_env, mock_web3_components, mock_vault_with_balance):
        """Test contract call failure handling."""
        # Given
        mock_update.effective_user.id = 123456789
        mock_context.args = ["0.5"]

        mock_api = AsyncMock()
        mock_api.get_vault.return_value = mock_vault_with_balance

        # Mock contract to return failure
        mock_contract_instance = create_mocked_vault_contract(mock_web3_components)
        mock_contract_instance.contract.functions.withdrawETH.return_value.build_transaction.return_value = {}
        mock_contract_instance.contract.functions.withdrawETH.return_value.estimate_gas.side_effect = Exception("Contract error")

        with patch("main.is_admin", return_value=True), \
             patch("main.contract", return_value=mock_contract_instance), \
             patch("main.api", mock_api):
            from main import cmd_withdraw, handle_withdraw_confirm, _pending_withdrawals

            # Clear any pending withdrawals
            _pending_withdrawals.clear()

            # Start withdrawal
            await cmd_withdraw(mock_update, mock_context)

            # When - Confirm withdrawal (should fail)
            mock_update.message.text = "Y"
            result = await handle_withdraw_confirm(mock_update, mock_context)

        # Then
        assert result == -1  # END
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "失败" in call_args


# ============================================================================
# Test Class: TestContractWithdrawEth (Contract Method Tests)
# ============================================================================

class TestContractWithdrawEth:
    """Tests for VaultContract.withdraw_eth method."""

    @pytest.mark.asyncio
    async def test_withdraw_eth_valid_amount(self, web3_test_env, mock_web3_components):
        """Test successful ETH withdrawal."""
        # Given
        amount_wei = int(Web3.to_wei(0.5, 'ether'))
        vault_contract = create_mocked_vault_contract(mock_web3_components)

        # Mock successful transaction
        vault_contract.contract.functions.withdrawETH.return_value.build_transaction.return_value = {}
        vault_contract.contract.functions.withdrawETH.return_value.estimate_gas.return_value = 100000

        # When
        result = await vault_contract.withdraw_eth(amount_wei)

        # Then
        vault_contract.contract.functions.withdrawETH.assert_called_once_with(amount_wei)
        assert result.get("success") is True

    @pytest.mark.asyncio
    async def test_withdraw_eth_zero_amount(self, web3_test_env, mock_web3_components):
        """Test zero amount is rejected."""
        # Given
        vault_contract = create_mocked_vault_contract(mock_web3_components)

        # When
        result = await vault_contract.withdraw_eth(0)

        # Then
        assert result["success"] is False
        assert "大于 0" in result["error"]

    @pytest.mark.asyncio
    async def test_withdraw_eth_negative_amount(self, web3_test_env, mock_web3_components):
        """Test negative amount is rejected."""
        # Given
        vault_contract = create_mocked_vault_contract(mock_web3_components)

        # When
        result = await vault_contract.withdraw_eth(-100)

        # Then
        assert result["success"] is False
        assert "大于 0" in result["error"]

    @pytest.mark.asyncio
    async def test_withdraw_eth_contract_error(self, web3_test_env, mock_web3_components):
        """Test contract call failure handling."""
        # Given
        amount_wei = int(Web3.to_wei(0.5, 'ether'))
        vault_contract = create_mocked_vault_contract(mock_web3_components)

        # Mock contract error
        vault_contract.contract.functions.withdrawETH.side_effect = Exception("Contract error")

        # When
        result = await vault_contract.withdraw_eth(amount_wei)

        # Then
        assert result["success"] is False
        assert "error" in result


# ============================================================================
# Test Class: TestCommandRegistration (Command Registration Tests)
# ============================================================================

class TestCommandRegistration:
    """Tests for withdraw command registration."""

    @pytest.mark.asyncio
    async def test_withdraw_command_in_bot_commands(self, web3_test_env):
        """Test that withdraw command is registered in bot commands."""
        # When
        from main import post_init

        # Create a mock application
        mock_app = MagicMock()
        mock_app.bot = AsyncMock()
        mock_app.bot.set_my_commands = AsyncMock()

        await post_init(mock_app)

        # Then
        mock_app.bot.set_my_commands.assert_called_once()
        commands = mock_app.bot.set_my_commands.call_args[0][0]
        command_names = [cmd.command for cmd in commands]
        assert "withdraw" in command_names

    def test_withdraw_handler_in_create_app(self, web3_test_env):
        """Test that withdraw handler is added to application."""
        # When
        from main import create_app

        # Note: This test verifies the handler is added without actually creating the app
        # since that requires a valid bot token. Instead, we verify the code structure.
        import inspect
        source = inspect.getsource(create_app)

        # Then
        assert "withdraw_handler" in source
        assert "ConversationHandler" in source
        assert "cmd_withdraw" in source
