"""
API tests for Terminal Markets API integration.

These tests verify the external API endpoints.
Mark with @pytest.mark.api and run separately with: pytest -m api

Note: These tests require network access to api.terminal.markets.
They will be skipped if the API is unreachable.
"""

import aiohttp
import pytest

from api import TerminalAPI


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "api: marks tests as API integration tests (deselect with '-m \"not api\"')")


@pytest.mark.api
class TestTerminalAPI:
    """Integration tests for Terminal API."""

    @pytest.fixture
    def api_client(self) -> TerminalAPI:
        """Create API client. Reads config from environment variables."""
        # API_BASE_URL and VAULT_ADDRESS are read by TerminalAPI from os.environ
        return TerminalAPI()

    @pytest.mark.asyncio
    async def test_get_positions_returns_data(self, api_client: TerminalAPI) -> None:
        """Test that get_positions returns valid data structure."""
        # When
        try:
            data = await api_client.get_positions()
        except aiohttp.client_exceptions.ClientConnectorError:
            pytest.skip("API unreachable - network or server issue")

        # Then
        assert data is not None
        assert isinstance(data, dict)
        # Either we get valid data or an error
        if "error" not in data:
            assert "ethBalance" in data or "positions" in data

    @pytest.mark.asyncio
    async def test_get_vault_returns_data(self, api_client: TerminalAPI) -> None:
        """Test that get_vault returns valid data structure."""
        # When
        try:
            data = await api_client.get_vault()
        except aiohttp.client_exceptions.ClientConnectorError:
            pytest.skip("API unreachable - network or server issue")

        # Then
        assert data is not None
        assert isinstance(data, dict)
        if "error" not in data:
            assert "vaultAddress" in data

    @pytest.mark.asyncio
    async def test_get_activity_returns_data(self, api_client: TerminalAPI) -> None:
        """Test that get_activity returns valid data structure."""
        # When
        try:
            data = await api_client.get_activity(limit=5)
        except aiohttp.client_exceptions.ClientConnectorError:
            pytest.skip("API unreachable - network or server issue")

        # Then
        assert data is not None
        assert isinstance(data, dict)
        if "error" not in data:
            assert "items" in data
            assert isinstance(data["items"], list)

    @pytest.mark.asyncio
    async def test_get_swaps_returns_data(self, api_client: TerminalAPI) -> None:
        """Test that get_swaps returns valid data structure."""
        # When
        try:
            data = await api_client.get_swaps(limit=5)
        except aiohttp.client_exceptions.ClientConnectorError:
            pytest.skip("API unreachable - network or server issue")

        # Then
        assert data is not None
        assert isinstance(data, dict)
        if "error" not in data:
            assert "items" in data

    @pytest.mark.asyncio
    async def test_get_strategies_returns_data(self, api_client: TerminalAPI) -> None:
        """Test that get_strategies returns valid data structure."""
        # When
        try:
            data = await api_client.get_strategies()
        except aiohttp.client_exceptions.ClientConnectorError:
            pytest.skip("API unreachable - network or server issue")

        # Then
        # Strategies can be empty list or list of strategy objects
        assert data is not None
        if isinstance(data, list):
            pass  # Valid empty or populated list
        elif isinstance(data, dict) and "error" in data:
            pass  # Valid error response
        else:
            pytest.fail("Unexpected response format")


@pytest.mark.api
@pytest.mark.slow
class TestTerminalAPIPerformance:
    """Performance tests for Terminal API."""

    @pytest.fixture
    def api_client(self) -> TerminalAPI:
        """Create API client."""
        return TerminalAPI()

    @pytest.mark.asyncio
    async def test_api_response_time(self, api_client: TerminalAPI) -> None:
        """Test API responds within acceptable time."""
        import time

        start = time.time()
        try:
            await api_client.get_positions()
        except aiohttp.client_exceptions.ClientConnectorError:
            pytest.skip("API unreachable - network or server issue")
        elapsed = time.time() - start

        # API should respond within 5 seconds
        assert elapsed < 5.0, f"API took {elapsed:.2f}s to respond"
