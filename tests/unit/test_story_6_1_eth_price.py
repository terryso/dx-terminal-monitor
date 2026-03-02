"""
Unit tests for Story 6.1: ETH Price Query

Tests for: api.get_eth_price(), cmd_price command handler
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


# =============================================================================
# Test Class: TestCmdPrice (Command Handler Tests)
# =============================================================================


class TestCmdPrice:
    """Tests for cmd_price command handler."""

    @pytest.mark.asyncio
    async def test_cmd_price_success(self, mock_update, mock_context):
        """Test normal query - cmd_price returns formatted ETH price."""
        # Given
        mock_api = AsyncMock()
        mock_api.get_eth_price = AsyncMock(return_value={
            "price": "3000.00",
            "change24h": "2.5"
        })

        with patch("commands.query.authorized", return_value=True), patch(
            "commands.query._get_api"
        ) as mock_get_api:
            mock_get_api.return_value = mock_api
            from commands.query import cmd_price

            # When
            await cmd_price(mock_update, mock_context)

        # Then
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "ETH Price" in call_args
        assert "3000" in call_args
        assert "2.5" in call_args

    @pytest.mark.asyncio
    async def test_cmd_price_unauthorized(self, mock_update, mock_context):
        """Test unauthorized user is rejected."""
        # Given
        mock_update.effective_user.id = 99999  # Non-authorized user

        with patch("commands.query.authorized", return_value=False):
            from commands.query import cmd_price

            # When
            await cmd_price(mock_update, mock_context)

        # Then
        # Should not call reply_text since user is not authorized
        mock_update.message.reply_text.assert_not_called()

    @pytest.mark.asyncio
    async def test_cmd_price_api_error(self, mock_update, mock_context):
        """Test API error message display."""
        # Given
        mock_api = AsyncMock()
        mock_api.get_eth_price = AsyncMock(return_value={"error": "API unavailable"})

        with patch("commands.query.authorized", return_value=True), patch(
            "commands.query._get_api"
        ) as mock_get_api:
            mock_get_api.return_value = mock_api
            from commands.query import cmd_price

            # When
            await cmd_price(mock_update, mock_context)

        # Then
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "Error" in call_args or "error" in call_args.lower()

    @pytest.mark.asyncio
    async def test_cmd_price_negative_change(self, mock_update, mock_context):
        """Test negative 24h change formatting."""
        # Given
        mock_api = AsyncMock()
        mock_api.get_eth_price = AsyncMock(return_value={
            "price": "2800.00",
            "change24h": "-3.5"
        })

        with patch("commands.query.authorized", return_value=True), patch(
            "commands.query._get_api"
        ) as mock_get_api:
            mock_get_api.return_value = mock_api
            from commands.query import cmd_price

            # When
            await cmd_price(mock_update, mock_context)

        # Then
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "-3.5" in call_args


# =============================================================================
# Test Class: TestCommandRegistration
# =============================================================================


class TestCommandRegistration:
    """Tests for price command registration."""

    def test_cmd_price_exported_from_query(self):
        """Test that cmd_price is exported from commands.query module."""
        try:
            from commands.query import cmd_price

            assert cmd_price is not None
        except ImportError:
            pytest.fail("cmd_price not exported from commands.query")

    def test_cmd_price_in_all_exports(self):
        """Test that cmd_price is in __all__ list."""
        import commands

        if hasattr(commands, "__all__"):
            assert "cmd_price" in commands.__all__
        else:
            # Verify the function exists
            assert hasattr(commands, "cmd_price")

    @pytest.mark.asyncio
    async def test_price_command_in_bot_commands(self):
        """Test that price command is in bot commands."""
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
        assert "price" in command_names

    @pytest.mark.asyncio
    async def test_cmd_start_includes_price_help(self):
        """Test that /start help text includes /price command."""
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
        assert "/price" in call_args
