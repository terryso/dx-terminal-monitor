"""
Unit tests for Story 6.3: Token Detail Query

Tests for: api.get_token(), cmd_token command handler
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# =============================================================================
# Test Fixtures
# =============================================================================


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
def mock_token_response():
    """Create mock token detail API response.

    Based on actual API response structure from /token/{address} endpoint.
    """
    return {
        "symbol": "ETH",
        "name": "Ethereum",
        "tokenAddress": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
        "type": "blue_chip_token",
        "description": "Ethereum is a decentralized, open-source blockchain.",
        "totalSupply": "1000000000000000000000000000",
        "poolId": "0x1234...",
        "image": "https://example.com/eth.png",
    }


# =============================================================================
# Test Class: TestGetToken (API Method Tests)
# =============================================================================


class TestGetToken:
    """Tests for get_token API method."""

    @pytest.mark.asyncio
    async def test_get_token_success_with_symbol(self, mock_token_response):
        """Test get_token returns token details for symbol input.

        When a symbol is provided, get_token uses cache to find the address,
        then queries the specific token by address.
        """
        # Given
        import api as api_module
        from api import TerminalAPI

        # Pre-populate cache to avoid cache building
        token_address = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
        api_module._token_cache = {"ETH": token_address}
        api_module._token_cache_time = 9999999999  # Far future

        api = TerminalAPI()

        # Mock only the final token detail call
        with patch.object(api, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_token_response

            # When
            result = await api.get_token("ETH")

        # Then
        assert result is not None
        assert result["symbol"] == "ETH"
        assert result["name"] == "Ethereum"
        assert result["tokenAddress"] == token_address
        # Only one call to get token details (cache was pre-populated)
        mock_get.assert_called_once_with(f"/token/{token_address}")

    @pytest.mark.asyncio
    async def test_get_token_success_with_address(self, mock_token_response):
        """Test get_token returns token details for address input."""
        # Given
        from api import TerminalAPI

        api = TerminalAPI()
        token_address = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"

        with patch.object(api, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_token_response

            # When
            result = await api.get_token(token_address)

        # Then
        assert result is not None
        assert result["symbol"] == "ETH"
        mock_get.assert_called_once_with(f"/token/{token_address}")

    @pytest.mark.asyncio
    async def test_get_token_api_error(self):
        """Test get_token handles API errors when token not in cache."""
        # Given
        import api as api_module
        from api import TerminalAPI

        # Clear cache before test
        api_module._token_cache.clear()
        api_module._token_cache_time = 0

        api = TerminalAPI()

        # Mock empty tokens list (token not found)
        with patch.object(api, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {"items": []}  # Empty cache

            # When
            result = await api.get_token("INVALID")

        # Then
        assert "error" in result
        assert "INVALID" in result["error"]


# =============================================================================
# Test Class: TestCmdToken (Command Handler Tests)
# =============================================================================


class TestCmdToken:
    """Tests for cmd_token command handler."""

    @pytest.mark.asyncio
    async def test_cmd_token_success_with_symbol(
        self, mock_update, mock_context, mock_token_response
    ):
        """Test normal query - cmd_token returns formatted token details for symbol."""
        # Given
        mock_context.args = ["ETH"]
        mock_api = AsyncMock()
        mock_api.get_token = AsyncMock(return_value=mock_token_response)

        with (
            patch("commands.query.authorized", return_value=True),
            patch("commands.query._get_api") as mock_get_api,
        ):
            mock_get_api.return_value = mock_api
            from commands.query import cmd_token

            # When
            await cmd_token(mock_update, mock_context)

        # Then
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "Token Details: $ETH" in call_args
        assert "Ethereum" in call_args
        assert "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2" in call_args
        assert "Type: Blue Chip Token" in call_args
        assert "Ethereum is a decentralized" in call_args

    @pytest.mark.asyncio
    async def test_cmd_token_success_with_address(
        self, mock_update, mock_context, mock_token_response
    ):
        """Test cmd_token works with contract address input."""
        # Given
        token_address = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
        mock_context.args = [token_address]
        mock_api = AsyncMock()
        mock_api.get_token = AsyncMock(return_value=mock_token_response)

        with (
            patch("commands.query.authorized", return_value=True),
            patch("commands.query._get_api") as mock_get_api,
        ):
            mock_get_api.return_value = mock_api
            from commands.query import cmd_token

            # When
            await cmd_token(mock_update, mock_context)

        # Then
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "Token Details: $ETH" in call_args
        mock_api.get_token.assert_called_once_with(token_address)

    @pytest.mark.asyncio
    async def test_cmd_token_unauthorized(self, mock_update, mock_context):
        """Test unauthorized user is rejected."""
        # Given
        mock_context.args = ["ETH"]
        mock_update.effective_user.id = 99999  # Non-authorized user

        with patch("commands.query.authorized", return_value=False):
            from commands.query import cmd_token

            # When
            await cmd_token(mock_update, mock_context)

        # Then
        # Should not call reply_text since user is not authorized
        mock_update.message.reply_text.assert_not_called()

    @pytest.mark.asyncio
    async def test_cmd_token_missing_argument(self, mock_update, mock_context):
        """Test missing argument displays usage hint."""
        # Given
        mock_context.args = []  # No arguments

        with patch("commands.query.authorized", return_value=True):
            from commands.query import cmd_token

            # When
            await cmd_token(mock_update, mock_context)

        # Then
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "Usage" in call_args or "usage" in call_args.lower()

    @pytest.mark.asyncio
    async def test_cmd_token_api_error(self, mock_update, mock_context):
        """Test API error message display."""
        # Given
        mock_context.args = ["INVALID"]
        mock_api = AsyncMock()
        mock_api.get_token = AsyncMock(return_value={"error": "Token not found"})

        with (
            patch("commands.query.authorized", return_value=True),
            patch("commands.query._get_api") as mock_get_api,
        ):
            mock_get_api.return_value = mock_api
            from commands.query import cmd_token

            # When
            await cmd_token(mock_update, mock_context)

        # Then
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "Error" in call_args or "error" in call_args.lower()


# =============================================================================
# Test Class: TestCommandRegistration
# =============================================================================


class TestCommandRegistration:
    """Tests for token command registration."""

    def test_cmd_token_exported_from_query(self):
        """Test that cmd_token is exported from commands.query module."""
        try:
            from commands.query import cmd_token

            assert cmd_token is not None
        except ImportError:
            pytest.fail("cmd_token not exported from commands.query")

    def test_cmd_token_in_all_exports(self):
        """Test that cmd_token is in __all__ list."""
        import commands

        if hasattr(commands, "__all__"):
            assert "cmd_token" in commands.__all__
        else:
            # Verify the function exists
            assert hasattr(commands, "cmd_token")

    @pytest.mark.asyncio
    async def test_token_command_in_bot_commands(self):
        """Test that token command is in bot commands."""
        from main import post_init

        # Create a mock application
        mock_app = MagicMock()
        mock_app.bot = AsyncMock()
        mock_app.bot.set_my_commands = AsyncMock()

        # Call post_init
        await post_init(mock_app)

        # Verify set_my_commands was called
        mock_app.bot.set_my_commands.assert_called_once()
        commands = mock_app.bot.set_my_commands.call_args[0][0]
        command_names = [cmd.command for cmd in commands]
        assert "token" in command_names

    @pytest.mark.asyncio
    async def test_cmd_start_includes_token_help(self):
        """Test that /start help text includes /token command."""
        mock_update = MagicMock()
        mock_update.effective_user = MagicMock()
        mock_update.effective_user.id = 123456789
        mock_update.message = AsyncMock()

        mock_context = MagicMock()
        mock_context.args = []

        with patch("commands.query.authorized", return_value=True):
            from commands.query import cmd_start

            await cmd_start(mock_update, mock_context)

        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "/token" in call_args
