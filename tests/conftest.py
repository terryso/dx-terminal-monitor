"""
Pytest configuration and fixtures for dx-terminal-monitor tests.

This module provides shared fixtures for testing the Telegram bot
and Terminal Markets API integration.
"""

import asyncio
import os
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from dotenv import load_dotenv

# Load test environment
load_dotenv(".env.test", override=True)


# ============================================================================
# Event Loop Configuration
# ============================================================================

@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# Configuration Fixtures
# ============================================================================

@pytest.fixture
def test_config() -> dict:
    """Provide test configuration values."""
    return {
        "telegram_token": os.getenv("TELEGRAM_BOT_TOKEN", "test_token"),
        "allowed_users": [int(x) for x in os.getenv("ALLOWED_USERS", "").split(",")
                         if x.strip().isdigit()],
        "vault_address": os.getenv("VAULT_ADDRESS", "0x933aafc9C5B1e0000E1dd77ac52D67b0E4e4997C"),
        "api_base_url": os.getenv("API_BASE_URL", "https://api.terminal.markets/api/v1"),
        "test_user_id": int(os.getenv("TEST_USER_ID", "123456789")),
    }


# ============================================================================
# Mock Fixtures
# ============================================================================

@pytest.fixture
def mock_telegram_update() -> MagicMock:
    """Create a mock Telegram Update object."""
    update = MagicMock()
    update.effective_user = MagicMock()
    update.effective_user.id = 123456789
    update.effective_user.username = "test_user"
    update.message = AsyncMock()
    return update


@pytest.fixture
def mock_telegram_context() -> MagicMock:
    """Create a mock Telegram Context object."""
    context = MagicMock()
    context.bot = AsyncMock()
    return context


@pytest.fixture
def mock_api_response_positions() -> dict:
    """Sample positions API response."""
    return {
        "ethBalance": "1000000000000000000",  # 1 ETH
        "overallValueUsd": "3500.00",
        "overallPnlUsd": "150.00",
        "overallPnlPercent": "4.5",
        "positions": [
            {
                "tokenSymbol": "ETH",
                "currentValueUsd": "3500.00",
                "totalPnlUsd": "150.00",
                "totalPnlPercent": "4.5",
                "realizedPnlUsd": "50.00",
                "unrealizedPnlUsd": "100.00",
            }
        ],
    }


@pytest.fixture
def mock_api_response_activity() -> dict:
    """Sample activity API response."""
    return {
        "items": [
            {
                "type": "swap",
                "swap": {
                    "tokenSymbol": "USDC",
                    "side": "buy",
                    "ethAmount": "500000000000000000",
                },
            },
            {
                "type": "deposit",
                "deposit": {
                    "amountWei": "1000000000000000000",
                },
            },
        ]
    }


@pytest.fixture
def mock_api_response_vault() -> dict:
    """Sample vault API response."""
    return {
        "vaultAddress": "0x933aafc9C5B1e0000E1dd77ac52D67b0E4e4997C",
        "nftId": "1",
        "nftName": "Test Vault",
        "ownerAddress": "0xOwner",
        "state": "active",
        "paused": False,
        "maxTradeAmount": "1000",
        "slippageBps": "50",
    }


# ============================================================================
# API Mock Patches
# ============================================================================

@pytest.fixture
async def mock_terminal_api(mock_api_response_positions: dict) -> AsyncGenerator[AsyncMock, None]:
    """Mock TerminalAPI for unit tests."""
    with patch("api.TerminalAPI") as mock_api_class:
        mock_instance = AsyncMock()
        mock_instance.get_positions = AsyncMock(return_value=mock_api_response_positions)
        mock_instance.get_activity = AsyncMock(return_value={"items": []})
        mock_instance.get_vault = AsyncMock(return_value={})
        mock_api_class.return_value = mock_instance
        yield mock_instance


# ============================================================================
# Test Data Factories
# ============================================================================

class PositionFactory:
    """Factory for creating test position data."""

    @staticmethod
    def create(
        token_symbol: str = "ETH",
        current_value_usd: str = "1000.00",
        total_pnl_usd: str = "100.00",
        total_pnl_percent: str = "10.0",
        **kwargs,
    ) -> dict:
        """Create a position with default values."""
        return {
            "tokenSymbol": token_symbol,
            "currentValueUsd": current_value_usd,
            "totalPnlUsd": total_pnl_usd,
            "totalPnlPercent": total_pnl_percent,
            "realizedPnlUsd": kwargs.get("realized_pnl_usd", "50.00"),
            "unrealizedPnlUsd": kwargs.get("unrealized_pnl_usd", "50.00"),
        }


class ActivityFactory:
    """Factory for creating test activity data."""

    @staticmethod
    def create_swap(
        token_symbol: str = "USDC",
        side: str = "buy",
        eth_amount: str = "500000000000000000",
    ) -> dict:
        """Create a swap activity."""
        return {
            "type": "swap",
            "swap": {
                "tokenSymbol": token_symbol,
                "side": side,
                "ethAmount": eth_amount,
            },
        }

    @staticmethod
    def create_deposit(amount_wei: str = "1000000000000000000") -> dict:
        """Create a deposit activity."""
        return {
            "type": "deposit",
            "deposit": {"amountWei": amount_wei},
        }

    @staticmethod
    def create_withdrawal(amount_wei: str = "500000000000000000") -> dict:
        """Create a withdrawal activity."""
        return {
            "type": "withdrawal",
            "withdrawal": {"amountWei": amount_wei},
        }


@pytest.fixture
def position_factory() -> PositionFactory:
    """Provide position factory."""
    return PositionFactory()


@pytest.fixture
def activity_factory() -> ActivityFactory:
    """Provide activity factory."""
    return ActivityFactory()
