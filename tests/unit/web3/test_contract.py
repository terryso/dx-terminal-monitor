"""
Unit tests for VaultContract class.

Story: 1.0 - Web3 Infrastructure Setup
"""

import json
import os
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open

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


# ============================================================================
# AC2: contract.py module exists
# ============================================================================

class TestContractModuleExists:
    """Tests for contract module existence."""

    def test_contract_module_importable(self, web3_test_env):
        """VaultContract should be importable from contract module."""
        from contract import VaultContract

        assert VaultContract is not None

    def test_contract_module_has_vault_class(self, web3_test_env):
        """contract module should expose VaultContract class."""
        import contract

        assert hasattr(contract, 'VaultContract')
        assert callable(contract.VaultContract)


# ============================================================================
# AC3: ABI file exists and is loadable
# ============================================================================

class TestABIFileLoading:
    """Tests for ABI file loading."""

    def test_abi_file_exists(self):
        """AgentVault.json ABI file should exist."""
        abi_path = Path(__file__).parent.parent.parent.parent / 'abi' / 'AgentVault.json'
        assert abi_path.exists(), f"ABI file not found at {abi_path}"

    def test_abi_file_valid_json(self):
        """AgentVault.json should be valid JSON."""
        abi_path = Path(__file__).parent.parent.parent.parent / 'abi' / 'AgentVault.json'
        with open(abi_path, 'r') as f:
            abi_data = json.load(f)

        assert isinstance(abi_data, list)

    def test_abi_contains_required_functions(self):
        """ABI should contain required contract functions."""
        abi_path = Path(__file__).parent.parent.parent.parent / 'abi' / 'AgentVault.json'
        with open(abi_path, 'r') as f:
            abi_data = json.load(f)

        function_names = [
            item.get('name')
            for item in abi_data
            if item.get('type') == 'function'
        ]

        required_functions = [
            'disableStrategy',
            'disableAllActiveStrategies',
            'addStrategy',
            'pauseVault',
            'updateSettings',
            'withdraw',
        ]

        for func in required_functions:
            assert func in function_names, f"Missing required function: {func}"


# ============================================================================
# AC4: Environment variables configuration
# ============================================================================

class TestEnvironmentConfiguration:
    """Tests for environment variable configuration."""

    def test_config_has_rpc_url(self, web3_test_env):
        """config module should expose RPC_URL."""
        import config
        assert hasattr(config, 'RPC_URL')

    def test_config_has_chain_id(self, web3_test_env):
        """config module should expose CHAIN_ID."""
        import config
        assert hasattr(config, 'CHAIN_ID')
        assert config.CHAIN_ID == 1

    def test_config_has_admin_users(self, web3_test_env):
        """config module should expose ADMIN_USERS."""
        import config
        assert hasattr(config, 'ADMIN_USERS')
        assert isinstance(config.ADMIN_USERS, list)

    def test_config_has_is_admin_function(self, web3_test_env):
        """config module should expose is_admin function."""
        import config

        assert hasattr(config, 'is_admin')
        assert callable(config.is_admin)

    def test_is_admin_returns_false_when_not_configured(self, web3_test_env):
        """is_admin should return False when ADMIN_USERS is empty (secure default)."""
        import config

        # When ADMIN_USERS is empty, deny admin access (secure default)
        assert config.is_admin(123456789) is False

    def test_is_admin_checks_membership(self):
        """is_admin should check if user is in ADMIN_USERS list."""
        os.environ['ADMIN_USERS'] = '111111111,222222222'
        os.environ['RPC_URL'] = 'https://test.com'
        os.environ['PRIVATE_KEY'] = '0x' + 'a' * 64
        os.environ['CHAIN_ID'] = '1'
        os.environ['VAULT_ADDRESS'] = '0x933aafc9C5B1e0000E1dd77ac52D67b0E4e4997C'

        import importlib
        import config
        importlib.reload(config)

        assert config.is_admin(111111111) is True
        assert config.is_admin(222222222) is True
        assert config.is_admin(999999999) is False


# ============================================================================
# AC5: VaultContract class basic structure
# ============================================================================

class TestVaultContractClassStructure:
    """Tests for VaultContract class structure."""

    def test_vault_contract_instantiation(self, web3_test_env, mock_web3_components):
        """VaultContract should be instantiable."""
        vc = create_mocked_vault_contract(mock_web3_components)
        assert vc is not None

    def test_vault_contract_has_w3_attribute(self, web3_test_env, mock_web3_components):
        """VaultContract should have w3 (Web3) attribute."""
        vc = create_mocked_vault_contract(mock_web3_components)
        assert hasattr(vc, 'w3')

    def test_vault_contract_has_account_attribute(self, web3_test_env, mock_web3_components):
        """VaultContract should have account attribute."""
        vc = create_mocked_vault_contract(mock_web3_components)
        assert hasattr(vc, 'account')

    def test_vault_contract_has_contract_attribute(self, web3_test_env, mock_web3_components):
        """VaultContract should have contract attribute."""
        vc = create_mocked_vault_contract(mock_web3_components)
        assert hasattr(vc, 'contract')

    def test_vault_contract_has_address_attribute(self, web3_test_env, mock_web3_components):
        """VaultContract should have vault address attribute."""
        vc = create_mocked_vault_contract(mock_web3_components)
        assert hasattr(vc, 'address')
        assert vc.address.startswith('0x')


# ============================================================================
# AC5: _send_transaction method
# ============================================================================

class TestSendTransactionMethod:
    """Tests for _send_transaction private method."""

    def test_send_transaction_exists(self, web3_test_env, mock_web3_components):
        """VaultContract should have _send_transaction method."""
        vc = create_mocked_vault_contract(mock_web3_components)
        assert hasattr(vc, '_send_transaction')
        assert callable(vc._send_transaction)

    @pytest.mark.asyncio
    async def test_send_transaction_returns_transaction_hash(self, web3_test_env, mock_web3_components):
        """_send_transaction should return transaction hash on success."""
        mock_w3, mock_account, mock_contract = mock_web3_components

        # Setup mock for transaction flow
        mock_contract.functions.testMethod.return_value.estimate_gas.return_value = 50000
        mock_contract.functions.testMethod.return_value.build_transaction.return_value = {
            'from': '0xTestSender0000000000000000000000000000',
            'nonce': 1,
            'gas': 60000,
            'gasPrice': 1000000000,
            'chainId': 1,
        }

        vc = create_mocked_vault_contract(mock_web3_components)

        tx_func = mock_contract.functions.testMethod()
        result = await vc._send_transaction(tx_func)

        assert result is not None
        assert result['success'] is True
        assert 'transactionHash' in result
        assert result['status'] == 1

    @pytest.mark.asyncio
    async def test_send_transaction_handles_gas_estimation(self, web3_test_env, mock_web3_components):
        """_send_transaction should estimate gas properly."""
        mock_w3, mock_account, mock_contract = mock_web3_components

        mock_contract.functions.testMethod.return_value.estimate_gas.return_value = 50000
        mock_contract.functions.testMethod.return_value.build_transaction.return_value = {
            'from': '0xTestSender0000000000000000000000000000',
            'nonce': 1,
            'gas': 60000,
        }

        vc = create_mocked_vault_contract(mock_web3_components)

        tx_func = mock_contract.functions.testMethod()
        await vc._send_transaction(tx_func)

        mock_contract.functions.testMethod.return_value.estimate_gas.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_transaction_signs_with_private_key(self, web3_test_env, mock_web3_components):
        """_send_transaction should sign transaction with account."""
        mock_w3, mock_account, mock_contract = mock_web3_components

        mock_contract.functions.testMethod.return_value.estimate_gas.return_value = 50000
        mock_contract.functions.testMethod.return_value.build_transaction.return_value = {
            'from': '0xTestSender0000000000000000000000000000',
            'nonce': 1,
            'gas': 60000,
        }

        vc = create_mocked_vault_contract(mock_web3_components)

        tx_func = mock_contract.functions.testMethod()
        await vc._send_transaction(tx_func)

        mock_account.sign_transaction.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_transaction_waits_for_receipt(self, web3_test_env, mock_web3_components):
        """_send_transaction should wait for transaction receipt."""
        mock_w3, mock_account, mock_contract = mock_web3_components

        mock_contract.functions.testMethod.return_value.estimate_gas.return_value = 50000
        mock_contract.functions.testMethod.return_value.build_transaction.return_value = {
            'from': '0xTestSender0000000000000000000000000000',
            'nonce': 1,
            'gas': 60000,
        }

        vc = create_mocked_vault_contract(mock_web3_components)

        tx_func = mock_contract.functions.testMethod()
        await vc._send_transaction(tx_func)

        mock_w3.eth.wait_for_transaction_receipt.assert_called_once()


# ============================================================================
# AC6: _send_transaction error handling
# ============================================================================

class TestSendTransactionErrorHandling:
    """Tests for _send_transaction error handling."""

    @pytest.mark.asyncio
    async def test_send_transaction_returns_error_on_gas_failure(self, web3_test_env, mock_web3_components):
        """_send_transaction should return error dict on gas estimation failure."""
        mock_w3, mock_account, mock_contract = mock_web3_components

        mock_contract.functions.testMethod.return_value.estimate_gas.side_effect = Exception("Gas estimation failed")

        vc = create_mocked_vault_contract(mock_web3_components)

        tx_func = mock_contract.functions.testMethod()
        result = await vc._send_transaction(tx_func)

        assert result['success'] is False
        assert "Gas estimation failed" in result['error']

    @pytest.mark.asyncio
    async def test_send_transaction_returns_error_on_tx_failure(self, web3_test_env, mock_web3_components):
        """_send_transaction should return error dict on transaction failure."""
        mock_w3, mock_account, mock_contract = mock_web3_components

        mock_contract.functions.testMethod.return_value.estimate_gas.return_value = 50000
        mock_contract.functions.testMethod.return_value.build_transaction.return_value = {
            'from': '0xTestSender0000000000000000000000000000',
            'nonce': 1,
            'gas': 60000,
        }
        mock_w3.eth.send_raw_transaction.side_effect = Exception("Network error")

        vc = create_mocked_vault_contract(mock_web3_components)

        tx_func = mock_contract.functions.testMethod()
        result = await vc._send_transaction(tx_func)

        assert result['success'] is False
        assert "Network error" in result['error']

    @pytest.mark.asyncio
    async def test_send_transaction_returns_error_on_receipt_failure(self, web3_test_env, mock_web3_components):
        """_send_transaction should return error dict on failed transaction receipt (status: 0)."""
        mock_w3, mock_account, mock_contract = mock_web3_components

        mock_contract.functions.testMethod.return_value.estimate_gas.return_value = 50000
        mock_contract.functions.testMethod.return_value.build_transaction.return_value = {
            'from': '0xTestSender0000000000000000000000000000',
            'nonce': 1,
            'gas': 60000,
        }
        mock_w3.eth.wait_for_transaction_receipt.return_value = {
            'transactionHash': b'hash',
            'status': 0,  # Failed
            'blockNumber': 12345,
        }

        vc = create_mocked_vault_contract(mock_web3_components)

        tx_func = mock_contract.functions.testMethod()
        result = await vc._send_transaction(tx_func)

        assert result['success'] is False
        assert "failed" in result['error'].lower()


# ============================================================================
# Configuration Validation
# ============================================================================

class TestConfigurationValidation:
    """Tests for configuration validation in VaultContract."""

    def test_raises_on_missing_rpc_url(self):
        """VaultContract should raise when RPC_URL is not configured."""
        os.environ['RPC_URL'] = ''
        os.environ['PRIVATE_KEY'] = '0x' + 'a' * 64
        os.environ['VAULT_ADDRESS'] = '0x933aafc9C5B1e0000E1dd77ac52D67b0E4e4997C'
        os.environ['CHAIN_ID'] = '1'

        import importlib
        import config
        import contract
        importlib.reload(config)
        importlib.reload(contract)

        with pytest.raises(ValueError) as exc_info:
            contract.VaultContract()

        assert "RPC_URL" in str(exc_info.value)

    def test_raises_on_missing_private_key(self):
        """VaultContract should raise when PRIVATE_KEY is not configured."""
        os.environ['RPC_URL'] = 'https://test.com'
        os.environ['PRIVATE_KEY'] = ''
        os.environ['VAULT_ADDRESS'] = '0x933aafc9C5B1e0000E1dd77ac52D67b0E4e4997C'
        os.environ['CHAIN_ID'] = '1'

        import importlib
        import config
        import contract
        importlib.reload(config)
        importlib.reload(contract)

        with pytest.raises(ValueError) as exc_info:
            contract.VaultContract()

        assert "PRIVATE_KEY" in str(exc_info.value)
