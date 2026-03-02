"""
Unit tests for Story 6.2: Tokens List Query

Tests for: api.get_tokens(), cmd_tokens command handler
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
def mock_tokens_response():
    """Create mock tokens API response."""
    return {
        "items": [
            {
                "symbol": "ETH",
                "name": "Ethereum",
                "priceUsd": "3000.00",
                "change24h": "2.5",
            },
            {
                "symbol": "USDC",
                "name": "USD Coin",
                "priceUsd": "1.00",
                "change24h": "0.1",
            },
        ],
        "total": 50,
        "page": 1,
        "limit": 10,
    }


# =============================================================================
# Test Class: TestGetTokens (API Method Tests)
# =============================================================================


class TestGetTokens:
    """Tests for get_tokens API method."""

    @pytest.mark.asyncio
    async def test_get_tokens_success(self, mock_tokens_response):
        """Test get_tokens returns token list from API."""
        # Given
        from api import TerminalAPI

        api = TerminalAPI()

        # Mock the _get method
        with patch.object(api, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_tokens_response

            # When
            result = await api.get_tokens()

        # Then
        assert result is not None
        assert "items" in result
        assert len(result["items"]) == 2
        assert result["items"][0]["symbol"] == "ETH"
        mock_get.assert_called_once_with("/tokens", {"page": 1, "limit": 10})

    @pytest.mark.asyncio
    async def test_get_tokens_with_pagination(self, mock_tokens_response):
        """Test get_tokens supports pagination parameters."""
        # Given
        from api import TerminalAPI

        api = TerminalAPI()

        with patch.object(api, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_tokens_response

            # When
            result = await api.get_tokens(page=2, limit=20)

        # Then
        mock_get.assert_called_once_with("/tokens", {"page": 2, "limit": 20})


# =============================================================================
# Test Class: TestCmdTokens (Command Handler Tests)
# =============================================================================


class TestCmdTokens:
    """Tests for cmd_tokens command handler."""

    @pytest.mark.asyncio
    async def test_cmd_tokens_success(self, mock_update, mock_context, mock_tokens_response):
        """Test normal query - cmd_tokens returns formatted token list."""
        # Given
        mock_api = AsyncMock()
        mock_api.get_tokens = AsyncMock(return_value=mock_tokens_response)

        with patch("commands.query.authorized", return_value=True), patch(
            "commands.query._get_api"
        ) as mock_get_api:
            mock_get_api.return_value = mock_api
            from commands.query import cmd_tokens

            # When
            await cmd_tokens(mock_update, mock_context)

        # Then
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "Tradeable Tokens" in call_args
        assert "ETH" in call_args
        assert "Ethereum" in call_args
        assert "USDC" in call_args
        assert "USD Coin" in call_args

    @pytest.mark.asyncio
    async def test_cmd_tokens_unauthorized(self, mock_update, mock_context):
        """Test unauthorized user is rejected."""
        # Given
        mock_update.effective_user.id = 99999  # Non-authorized user

        with patch("commands.query.authorized", return_value=False):
            from commands.query import cmd_tokens

            # When
            await cmd_tokens(mock_update, mock_context)

        # Then
        # Should not call reply_text since user is not authorized
        mock_update.message.reply_text.assert_not_called()

    @pytest.mark.asyncio
    async def test_cmd_tokens_api_error(self, mock_update, mock_context):
        """Test API error message display."""
        # Given
        mock_api = AsyncMock()
        mock_api.get_tokens = AsyncMock(return_value={"error": "API unavailable"})

        with patch("commands.query.authorized", return_value=True), patch(
            "commands.query._get_api"
        ) as mock_get_api:
            mock_get_api.return_value = mock_api
            from commands.query import cmd_tokens

            # When
            await cmd_tokens(mock_update, mock_context)

        # Then
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "Error" in call_args or "error" in call_args.lower()

    @pytest.mark.asyncio
    async def test_cmd_tokens_empty_list(self, mock_update, mock_context):
        """Test empty token list displays appropriate message."""
        # Given
        mock_api = AsyncMock()
        mock_api.get_tokens = AsyncMock(return_value={"items": [], "total": 0})

        with patch("commands.query.authorized", return_value=True), patch(
            "commands.query._get_api"
        ) as mock_get_api:
            mock_get_api.return_value = mock_api
            from commands.query import cmd_tokens

            # When
            await cmd_tokens(mock_update, mock_context)

        # Then
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "No tokens" in call_args

    @pytest.mark.asyncio
    async def test_cmd_tokens_pagination(self, mock_update, mock_context, mock_tokens_response):
        """Test pagination parameter parsing."""
        # Given
        mock_context.args = ["2"]  # Page 2
        mock_tokens_response["page"] = 2

        mock_api = AsyncMock()
        mock_api.get_tokens = AsyncMock(return_value=mock_tokens_response)

        with patch("commands.query.authorized", return_value=True), patch(
            "commands.query._get_api"
        ) as mock_get_api:
            mock_get_api.return_value = mock_api
            from commands.query import cmd_tokens

            # When
            await cmd_tokens(mock_update, mock_context)

        # Then
        # Verify get_tokens was called with page=2
        mock_api.get_tokens.assert_called_once_with(2)
        # Verify output shows correct range
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "11-" in call_args  # Page 2 shows tokens 11-20

    @pytest.mark.asyncio
    async def test_cmd_tokens_invalid_page_zero(self, mock_update, mock_context, mock_tokens_response):
        """Test page 0 defaults to page 1."""
        # Given
        mock_context.args = ["0"]  # Invalid page 0
        mock_tokens_response["page"] = 1

        mock_api = AsyncMock()
        mock_api.get_tokens = AsyncMock(return_value=mock_tokens_response)

        with patch("commands.query.authorized", return_value=True), patch(
            "commands.query._get_api"
        ) as mock_get_api:
            mock_get_api.return_value = mock_api
            from commands.query import cmd_tokens

            # When
            await cmd_tokens(mock_update, mock_context)

        # Then
        # Verify get_tokens was called with page=1 (not 0)
        mock_api.get_tokens.assert_called_once_with(1)


# =============================================================================
# Test Class: TestCommandRegistration
# =============================================================================


class TestCommandRegistration:
    """Tests for tokens command registration."""

    def test_cmd_tokens_exported_from_query(self):
        """Test that cmd_tokens is exported from commands.query module."""
        try:
            from commands.query import cmd_tokens

            assert cmd_tokens is not None
        except ImportError:
            pytest.fail("cmd_tokens not exported from commands.query")

    def test_cmd_tokens_in_all_exports(self):
        """Test that cmd_tokens is in __all__ list."""
        import commands

        if hasattr(commands, "__all__"):
            assert "cmd_tokens" in commands.__all__
        else:
            # Verify the function exists
            assert hasattr(commands, "cmd_tokens")

    @pytest.mark.asyncio
    async def test_tokens_command_in_bot_commands(self):
        """Test that tokens command is in bot commands."""
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
        assert "tokens" in command_names

    @pytest.mark.asyncio
    async def test_cmd_start_includes_tokens_help(self):
        """Test that /start help text includes /tokens command."""
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
        assert "/tokens" in call_args
