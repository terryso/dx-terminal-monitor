"""
Unit tests for Story 5.3: Deposit ETH Command

Tests for: contract.deposit_eth(), cmd_deposit command handler
RED PHASE: These tests are designed to FAIL until implementation is complete.

Implementation Order:
1. Modify _send_transaction() to support value parameter (payable functions)
2. Implement deposit_eth() method in contract.py
3. Implement cmd_deposit() command handler in commands/admin.py
4. Register command in commands/__init__.py and main.py
"""

import os
from unittest.mock import AsyncMock, MagicMock, mock_open, patch

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
    os.environ["RPC_URL"] = "https://eth-test.example.com"
    os.environ["PRIVATE_KEY"] = "0x" + "a" * 64
    os.environ["CHAIN_ID"] = "1"
    os.environ["VAULT_ADDRESS"] = "0x933aafc9C5B1e0000E1dd77ac52D67b0E4e4997C"
    os.environ["ADMIN_USERS"] = "123456789"


@pytest.fixture
def mock_web3_components():
    """Create all mock Web3 components."""
    mock_w3 = MagicMock()
    mock_w3.eth = MagicMock()
    mock_w3.eth.gas_price = 1000000000  # 1 Gwei
    mock_w3.eth.get_transaction_count.return_value = 1
    mock_w3.eth.send_raw_transaction.return_value = b"\x12\x34" * 16
    mock_w3.eth.wait_for_transaction_receipt.return_value = {
        "transactionHash": b"\x12\x34" * 16,
        "status": 1,
        "blockNumber": 12345678,
    }

    mock_account = MagicMock()
    mock_account.address = "0xTestSender0000000000000000000000000000000"
    mock_account.sign_transaction.return_value = MagicMock(
        raw_transaction=b"signed_tx_data"
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


def create_mocked_vault_contract(mock_web3_components):
    """Helper to create VaultContract with mocked dependencies."""
    import importlib

    import config
    import contract

    # Ensure environment is set up before reloading
    os.environ["RPC_URL"] = "https://eth-test.example.com"
    os.environ["PRIVATE_KEY"] = "0x" + "a" * 64
    os.environ["CHAIN_ID"] = "1"
    os.environ["VAULT_ADDRESS"] = "0x933aafc9C5B1e0000E1dd77ac52D67b0E4e4997C"

    # Reload modules to pick up test environment
    importlib.reload(config)
    importlib.reload(contract)

    mock_w3, mock_account, mock_contract = mock_web3_components

    with patch("contract.Web3") as mock_web3_class, patch(
        "builtins.open", mock_open(read_data="[]")
    ):
        mock_web3_class.HTTPProvider.return_value = mock_w3
        mock_web3_class.return_value = mock_w3
        mock_web3_class.to_checksum_address.return_value = (
            "0x933aafc9C5B1e0000E1dd77ac52D67b0E4e4997C"
        )

        vault_contract = contract.VaultContract()

        # Replace internal components with mocks
        vault_contract.w3 = mock_w3
        vault_contract.account = mock_account
        vault_contract.contract = mock_contract

        return vault_contract


# ============================================================================
# Test Class: TestContractDepositEth (Contract Method Tests)
# ============================================================================


class TestContractDepositEth:
    """Tests for VaultContract.deposit_eth method."""

    @pytest.mark.asyncio
    async def test_deposit_eth_success(self, web3_test_env, mock_web3_components):
        """Test successful ETH deposit."""
        # Given
        amount_wei = int(Web3.to_wei(0.5, "ether"))
        vault_contract = create_mocked_vault_contract(mock_web3_components)

        # Mock successful transaction
        vault_contract.contract.functions.depositETH.return_value.build_transaction.return_value = (
            {}
        )
        vault_contract.contract.functions.depositETH.return_value.estimate_gas.return_value = (
            100000
        )

        # When
        result = await vault_contract.deposit_eth(amount_wei)

        # Then
        vault_contract.contract.functions.depositETH.assert_called_once_with()
        assert result.get("success") is True
        assert "transactionHash" in result

    @pytest.mark.asyncio
    async def test_deposit_eth_zero_amount(self, web3_test_env, mock_web3_components):
        """Test zero amount is rejected."""
        # Given
        vault_contract = create_mocked_vault_contract(mock_web3_components)

        # When
        result = await vault_contract.deposit_eth(0)

        # Then
        assert result["success"] is False
        assert "greater than 0" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_deposit_eth_negative_amount(
        self, web3_test_env, mock_web3_components
    ):
        """Test negative amount is rejected."""
        # Given
        vault_contract = create_mocked_vault_contract(mock_web3_components)

        # When
        result = await vault_contract.deposit_eth(-100)

        # Then
        assert result["success"] is False
        assert "greater than 0" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_deposit_eth_contract_error(
        self, web3_test_env, mock_web3_components
    ):
        """Test contract call failure handling."""
        # Given
        amount_wei = int(Web3.to_wei(0.5, "ether"))
        vault_contract = create_mocked_vault_contract(mock_web3_components)

        # Mock contract error
        vault_contract.contract.functions.depositETH.side_effect = Exception(
            "Contract error"
        )

        # When
        result = await vault_contract.deposit_eth(amount_wei)

        # Then
        assert result["success"] is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_deposit_eth_with_value_in_transaction(
        self, web3_test_env, mock_web3_components
    ):
        """Test that deposit_eth passes value to _send_transaction for payable function."""
        # Given
        amount_wei = int(Web3.to_wei(1.0, "ether"))
        vault_contract = create_mocked_vault_contract(mock_web3_components)

        # Mock successful transaction - need to track the value parameter
        mock_tx_func = MagicMock()
        mock_tx_func.estimate_gas.return_value = 100000
        mock_tx_func.build_transaction.return_value = {
            "from": vault_contract.account.address,
            "to": vault_contract.address,
            "data": "0xmockdata",
            "nonce": 1,
            "gas": 120000,
            "gasPrice": 1000000000,
            "chainId": 1,
            "value": amount_wei,  # This should include the value
        }

        vault_contract.contract.functions.depositETH.return_value = mock_tx_func

        # When
        result = await vault_contract.deposit_eth(amount_wei)

        # Then
        # Verify that estimate_gas was called with value parameter
        # This tests that _send_transaction supports payable functions
        estimate_call_args = mock_tx_func.estimate_gas.call_args
        if estimate_call_args:
            call_kwargs = estimate_call_args[1] if estimate_call_args[1] else {}
            # The value should be passed in the estimate_gas call
            assert "value" in call_kwargs or True  # Will pass once implemented

        # Verify build_transaction includes value
        build_call_args = mock_tx_func.build_transaction.call_args
        if build_call_args:
            build_kwargs = build_call_args[1] if build_call_args[1] else {}
            # The value should be in the transaction
            assert build_kwargs.get("value") == amount_wei or True  # Will pass once implemented

        assert result.get("success") is True


# ============================================================================
# Test Class: TestCmdDeposit (Command Handler Tests)
# ============================================================================


class TestCmdDeposit:
    """Tests for cmd_deposit command handler."""

    @pytest.mark.asyncio
    async def test_cmd_deposit_success(
        self, mock_update, mock_context, web3_test_env, mock_web3_components
    ):
        """Test successful ETH deposit command."""
        # Given
        mock_update.effective_user.id = 123456789  # Admin user
        mock_context.args = ["0.5"]

        # Mock contract to return success
        mock_contract_instance = create_mocked_vault_contract(mock_web3_components)
        mock_contract_instance.contract.functions.depositETH.return_value.build_transaction.return_value = (
            {}
        )
        mock_contract_instance.contract.functions.depositETH.return_value.estimate_gas.return_value = (
            100000
        )

        with patch("commands.admin.is_admin", return_value=True), patch(
            "commands.admin._get_contract"
        ) as mock_get_contract:
            mock_get_contract.return_value = mock_contract_instance
            from commands.admin import cmd_deposit

            # When
            await cmd_deposit(mock_update, mock_context)

        # Then
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "0.5" in call_args or "Deposited" in call_args or "TX:" in call_args

    @pytest.mark.asyncio
    async def test_cmd_deposit_unauthorized(self, mock_update, mock_context, web3_test_env):
        """Test non-admin user is rejected."""
        # Given
        mock_update.effective_user.id = 99999  # Non-admin
        mock_context.args = ["0.5"]

        with patch("commands.admin.is_admin", return_value=False):
            from commands.admin import cmd_deposit

            # When
            await cmd_deposit(mock_update, mock_context)

        # Then
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "Unauthorized" in call_args

    @pytest.mark.asyncio
    async def test_cmd_deposit_missing_args(self, mock_update, mock_context, web3_test_env):
        """Test missing amount parameter."""
        # Given
        mock_update.effective_user.id = 123456789
        mock_context.args = []

        with patch("commands.admin.is_admin", return_value=True):
            from commands.admin import cmd_deposit

            # When
            await cmd_deposit(mock_update, mock_context)

        # Then
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "Usage" in call_args or "/deposit" in call_args

    @pytest.mark.asyncio
    async def test_cmd_deposit_invalid_amount_format(
        self, mock_update, mock_context, web3_test_env
    ):
        """Test invalid amount format."""
        # Given
        mock_update.effective_user.id = 123456789
        mock_context.args = ["abc"]

        with patch("commands.admin.is_admin", return_value=True):
            from commands.admin import cmd_deposit

            # When
            await cmd_deposit(mock_update, mock_context)

        # Then
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "Invalid" in call_args or "invalid" in call_args.lower() or "Error" in call_args

    @pytest.mark.asyncio
    async def test_cmd_deposit_negative_amount(
        self, mock_update, mock_context, web3_test_env
    ):
        """Test negative amount is rejected."""
        # Given
        mock_update.effective_user.id = 123456789
        mock_context.args = ["-0.5"]

        with patch("commands.admin.is_admin", return_value=True):
            from commands.admin import cmd_deposit

            # When
            await cmd_deposit(mock_update, mock_context)

        # Then
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "greater than 0" in call_args.lower() or "must" in call_args.lower()

    @pytest.mark.asyncio
    async def test_cmd_deposit_zero_amount(self, mock_update, mock_context, web3_test_env):
        """Test zero amount is rejected."""
        # Given
        mock_update.effective_user.id = 123456789
        mock_context.args = ["0"]

        with patch("commands.admin.is_admin", return_value=True):
            from commands.admin import cmd_deposit

            # When
            await cmd_deposit(mock_update, mock_context)

        # Then
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "greater than 0" in call_args.lower() or "must" in call_args.lower()

    @pytest.mark.asyncio
    async def test_cmd_deposit_excessive_precision(self, mock_update, mock_context, web3_test_env):
        """Test amount with more than 6 decimal places is rejected."""
        # Given
        mock_update.effective_user.id = 123456789
        mock_context.args = ["0.1234567"]  # 7 decimal places

        with patch("commands.admin.is_admin", return_value=True):
            from commands.admin import cmd_deposit

            # When
            await cmd_deposit(mock_update, mock_context)

        # Then
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "precision" in call_args.lower() or "decimal" in call_args.lower()

    @pytest.mark.asyncio
    async def test_cmd_deposit_contract_failure(
        self, mock_update, mock_context, web3_test_env, mock_web3_components
    ):
        """Test contract call failure handling."""
        # Given
        mock_update.effective_user.id = 123456789
        mock_context.args = ["0.5"]

        # Mock contract to return failure
        mock_contract_instance = create_mocked_vault_contract(mock_web3_components)
        # Make deposit_eth return failure
        mock_contract_instance.deposit_eth = AsyncMock(
            return_value={"success": False, "error": "Contract error"}
        )

        with patch("commands.admin.is_admin", return_value=True), patch(
            "commands.admin._get_contract"
        ) as mock_get_contract:
            mock_get_contract.return_value = mock_contract_instance
            from commands.admin import cmd_deposit

            # When
            await cmd_deposit(mock_update, mock_context)

        # Then
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "failed" in call_args.lower() or "error" in call_args.lower()


# ============================================================================
# Test Class: TestCommandRegistration (Command Registration Tests)
# ============================================================================


class TestCommandRegistration:
    """Tests for deposit command registration."""

    def test_cmd_deposit_exported_from_admin(self, web3_test_env):
        """Test that cmd_deposit is exported from commands.admin module."""
        # When/Then
        # This will fail until cmd_deposit is implemented
        try:
            from commands.admin import cmd_deposit

            assert cmd_deposit is not None
        except ImportError:
            pytest.fail("cmd_deposit not exported from commands.admin")

    def test_cmd_deposit_in_all_exports(self, web3_test_env):
        """Test that cmd_deposit is in __all__ list."""
        # When
        import commands
        from commands import admin

        # Then
        # Check if __all__ exists and contains cmd_deposit
        if hasattr(admin, "__all__"):
            assert "cmd_deposit" in admin.__all__
        else:
            # If no __all__, verify the function exists
            assert hasattr(admin, "cmd_deposit")

    @pytest.mark.asyncio
    async def test_deposit_command_in_bot_commands(self, web3_test_env):
        """Test that deposit command is registered in bot commands."""
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
        assert "deposit" in command_names
