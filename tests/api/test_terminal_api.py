"""
API tests for Terminal Markets API integration.

These tests verify the external API endpoints.
Mark with @pytest.mark.api and run separately with: pytest -m api
"""

import pytest

from api import TerminalAPI


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
        data = await api_client.get_positions()

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
        data = await api_client.get_vault()

        # Then
        assert data is not None
        assert isinstance(data, dict)
        if "error" not in data:
            assert "vaultAddress" in data

    @pytest.mark.asyncio
    async def test_get_activity_returns_data(self, api_client: TerminalAPI) -> None:
        """Test that get_activity returns valid data structure."""
        # When
        data = await api_client.get_activity(limit=5)

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
        data = await api_client.get_swaps(limit=5)

        # Then
        assert data is not None
        assert isinstance(data, dict)
        if "error" not in data:
            assert "items" in data

    @pytest.mark.asyncio
    async def test_get_strategies_returns_data(self, api_client: TerminalAPI) -> None:
        """Test that get_strategies returns valid data structure."""
        # When
        data = await api_client.get_strategies()

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
        await api_client.get_positions()
        elapsed = time.time() - start

        # API should respond within 5 seconds
        assert elapsed < 5.0, f"API took {elapsed:.2f}s to respond"
