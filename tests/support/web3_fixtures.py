"""
Web3 mock fixtures and data factories for testing.

These fixtures provide mock Web3 objects for unit testing
without requiring actual blockchain connections.
"""

import os
from typing import Any, Dict
from unittest.mock import MagicMock

import pytest


# ============================================================================
# Test Configuration
# ============================================================================

TEST_CONFIG = {
    'rpc_url': 'https://eth-test.example.com',
    'private_key': '0x' + 'a' * 64,
    'chain_id': 1,
    'vault_address': '0x933aafc9C5B1e0000E1dd77ac52D67b0E4e4997C',
    'test_user_address': '0xTestUser' + '0' * 32,
}


# ============================================================================
# Mock Web3 Fixtures
# ============================================================================

@pytest.fixture
def mock_web3() -> MagicMock:
    """Create a mock Web3 instance."""
    mock = MagicMock()
    mock.eth = MagicMock()
    mock.eth.gas_price = 1000000000  # 1 Gwei
    mock.eth.chain_id = TEST_CONFIG['chain_id']
    mock.eth.get_transaction_count.return_value = 1
    return mock


@pytest.fixture
def mock_account() -> MagicMock:
    """Create a mock Ethereum account."""
    mock = MagicMock()
    mock.address = TEST_CONFIG['test_user_address']
    mock.sign_transaction.return_value = MagicMock(
        raw_transaction=b'\x12\x34' * 64  # Mock signed transaction (snake_case per web3.py)
    )
    return mock


@pytest.fixture
def mock_contract() -> MagicMock:
    """Create a mock smart contract instance."""
    mock = MagicMock()

    # Mock function calls
    mock.functions.disableStrategy.return_value.estimate_gas.return_value = 50000
    mock.functions.disableStrategy.return_value.build_transaction.return_value = {
        'from': TEST_CONFIG['test_user_address'],
        'to': TEST_CONFIG['vault_address'],
        'data': '0xmockdata',
        'nonce': 1,
        'gas': 50000,
        'gasPrice': 1000000000,
        'chainId': TEST_CONFIG['chain_id'],
    }

    mock.functions.disableAllActiveStrategies.return_value.estimate_gas.return_value = 100000
    mock.functions.disableAllActiveStrategies.return_value.build_transaction.return_value = {
        'from': TEST_CONFIG['test_user_address'],
        'to': TEST_CONFIG['vault_address'],
        'data': '0xmockdata2',
        'nonce': 1,
        'gas': 100000,
        'gasPrice': 1000000000,
        'chainId': TEST_CONFIG['chain_id'],
    }

    return mock


@pytest.fixture
def mock_transaction_receipt() -> Dict[str, Any]:
    """Create a mock transaction receipt."""
    return {
        'transactionHash': b'\x12\x34' * 16,
        'transactionIndex': 1,
        'blockNumber': 12345678,
        'blockHash': b'\xab\xcd' * 16,
        'from': TEST_CONFIG['test_user_address'],
        'to': TEST_CONFIG['vault_address'],
        'status': 1,  # Success
        'gasUsed': 50000,
        'contractAddress': None,
        'logs': [],
    }


@pytest.fixture
def mock_failed_receipt() -> Dict[str, Any]:
    """Create a mock failed transaction receipt."""
    return {
        'transactionHash': b'\x12\x34' * 16,
        'transactionIndex': 1,
        'blockNumber': 12345678,
        'blockHash': b'\xab\xcd' * 16,
        'from': TEST_CONFIG['test_user_address'],
        'to': TEST_CONFIG['vault_address'],
        'status': 0,  # Failed
        'gasUsed': 50000,
        'contractAddress': None,
        'logs': [],
    }


# ============================================================================
# Environment Setup Fixture
# ============================================================================

@pytest.fixture
def web3_env():
    """Set up environment variables for Web3 testing."""
    original_env = os.environ.copy()

    os.environ['RPC_URL'] = TEST_CONFIG['rpc_url']
    os.environ['PRIVATE_KEY'] = TEST_CONFIG['private_key']
    os.environ['CHAIN_ID'] = str(TEST_CONFIG['chain_id'])
    os.environ['VAULT_ADDRESS'] = TEST_CONFIG['vault_address']

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


# ============================================================================
# Web3 Data Factory
# ============================================================================

class Web3DataFactory:
    """Factory for creating Web3 test data."""

    @staticmethod
    def create_strategy(
        strategy_id: int = 1,
        content: str = "Test strategy",
        expiry: int = 0,
        priority: int = 1,
        active: bool = True,
    ) -> Dict[str, Any]:
        """Create a strategy object for testing."""
        return {
            'id': strategy_id,
            'content': content,
            'expiry': expiry,
            'priority': priority,
            'active': active,
        }

    @staticmethod
    def create_transaction_hash() -> str:
        """Create a mock transaction hash."""
        return '0x' + 'a' * 64

    @staticmethod
    def create_address(prefix: str = '') -> str:
        """Create a mock Ethereum address."""
        addr = '0x' + (prefix * 2)[:8].ljust(40, '0')
        return addr

    @staticmethod
    def create_gas_price(gwei: int = 10) -> int:
        """Create a gas price in Wei."""
        return gwei * 10**9

    @staticmethod
    def create_eth_amount(eth: float = 1.0) -> int:
        """Create an ETH amount in Wei."""
        return int(eth * 10**18)


@pytest.fixture
def web3_factory() -> Web3DataFactory:
    """Provide Web3 data factory."""
    return Web3DataFactory()
