"""
Unit tests for Story 1-3: Update command menu and help documentation.

Tests for: post_init registers new commands, cmd_start includes new help text,
create_app registers new handlers.

Priority: P2 (Documentation update, low risk)
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from telegram import BotCommand


# =============================================================================
# Tests for post_init - Story 1-3 AC #2
# =============================================================================

class TestPostInitStory13:
    """Tests for post_init function - Story 1-3 updates."""

    @pytest.mark.asyncio
    async def test_post_init_registers_disable_strategy_command(self) -> None:
        """Test post_init registers disable_strategy command (AC #2)."""
        # Given
        mock_app = MagicMock()
        mock_app.bot = AsyncMock()

        from main import post_init

        # When
        await post_init(mock_app)

        # Then
        mock_app.bot.set_my_commands.assert_called_once()
        call_args = mock_app.bot.set_my_commands.call_args[0][0]
        command_names = [cmd.command for cmd in call_args]
        assert "disable_strategy" in command_names, "disable_strategy command should be registered"

        # Also verify the command description
        disable_strategy_cmd = next((cmd for cmd in call_args if cmd.command == "disable_strategy"), None)
        assert disable_strategy_cmd is not None, "disable_strategy command should exist"
        assert disable_strategy_cmd.description == "Disable strategy", "Command description should match"

    @pytest.mark.asyncio
    async def test_post_init_registers_disable_all_command(self) -> None:
        """Test post_init registers disable_all command (AC #2)."""
        # Given
        mock_app = MagicMock()
        mock_app.bot = AsyncMock()

        from main import post_init

        # When
        await post_init(mock_app)

        # Then
        mock_app.bot.set_my_commands.assert_called_once()
        call_args = mock_app.bot.set_my_commands.call_args[0][0]
        command_names = [cmd.command for cmd in call_args]
        assert "disable_all" in command_names, "disable_all command should be registered"

        # Also verify the command description
        disable_all_cmd = next((cmd for cmd in call_args if cmd.command == "disable_all"), None)
        assert disable_all_cmd is not None, "disable_all command should exist"
        assert disable_all_cmd.description == "Disable all strategies", "Command description should match"

    @pytest.mark.asyncio
    async def test_post_init_registers_all_expected_commands(self) -> None:
        """Test post_init registers all 10 expected commands."""
        # Given
        mock_app = MagicMock()
        mock_app.bot = AsyncMock()

        from main import post_init

        # When
        await post_init(mock_app)

        # Then
        mock_app.bot.set_my_commands.assert_called_once()
        call_args = mock_app.bot.set_my_commands.call_args[0][0]
        command_names = [cmd.command for cmd in call_args]

        # All expected commands including the new ones from Story 1-3, 2-1, and 2-2
        expected_commands = [
            "start",
            "balance",
            "pnl",
            "positions",
            "activity",
            "swaps",
            "strategies",
            "vault",
            "add_strategy",      # NEW - Story 2-1
            "disable_strategy",  # NEW - Story 1-3
            "disable_all",       # NEW - Story 1-3
            "pause",             # NEW - Story 2-2
            "resume",            # NEW - Story 2-2
        ]

        assert len(command_names) == 13, f"Expected 13 commands, got {len(command_names)}"
        for expected in expected_commands:
            assert expected in command_names, f"Command '{expected}' should be registered"


# =============================================================================
# Tests for cmd_start help text - Story 1-3 AC #1
# =============================================================================

class TestCmdStartStory13:
    """Tests for cmd_start function - Story 1-3 updates."""

    @pytest.mark.asyncio
    async def test_cmd_start_includes_disable_strategy_help(self) -> None:
        """Test /start command includes disable_strategy in help text (AC #1)."""
        # Given - Mock authorized user
        mock_update = MagicMock()
        mock_update.effective_user.id = 123456789  # Authorized user
        mock_update.message = AsyncMock()
        mock_context = MagicMock()

        # Mock ALLOWED_USERS to include our test user
        with patch("main.ALLOWED_USERS", [123456789]):
            from main import cmd_start

            # When
            await cmd_start(mock_update, mock_context)

            # Then
            mock_update.message.reply_text.assert_called_once()
            help_text = mock_update.message.reply_text.call_args[0][0]
            assert "/disable_strategy" in help_text, "Help text should include /disable_strategy command"
            assert "<id>" in help_text, "Help text should show parameter placeholder"

    @pytest.mark.asyncio
    async def test_cmd_start_includes_disable_all_help(self) -> None:
        """Test /start command includes disable_all in help text (AC #1)."""
        # Given - Mock authorized user
        mock_update = MagicMock()
        mock_update.effective_user.id = 123456789  # Authorized user
        mock_update.message = AsyncMock()
        mock_context = MagicMock()

        # Mock ALLOWED_USERS to include our test user
        with patch("main.ALLOWED_USERS", [123456789]):
            from main import cmd_start

            # When
            await cmd_start(mock_update, mock_context)

            # Then
            mock_update.message.reply_text.assert_called_once()
            help_text = mock_update.message.reply_text.call_args[0][0]
            assert "/disable_all" in help_text, "Help text should include /disable_all command"

    @pytest.mark.asyncio
    async def test_cmd_start_help_text_format(self) -> None:
        """Test /start command help text has correct format."""
        # Given - Mock authorized user
        mock_update = MagicMock()
        mock_update.effective_user.id = 123456789  # Authorized user
        mock_update.message = AsyncMock()
        mock_context = MagicMock()

        # Mock ALLOWED_USERS to include our test user
        with patch("main.ALLOWED_USERS", [123456789]):
            from main import cmd_start

            # When
            await cmd_start(mock_update, mock_context)

            # Then
            mock_update.message.reply_text.assert_called_once()
            help_text = mock_update.message.reply_text.call_args[0][0]

            # Verify help text structure
            assert "Terminal Markets Monitor" in help_text
            assert "Commands:" in help_text

            # Verify new commands appear after existing commands
            disable_strategy_pos = help_text.find("/disable_strategy")
            vault_pos = help_text.find("/vault")
            assert vault_pos > 0, "/vault should be in help text"
            assert disable_strategy_pos > vault_pos, "/disable_strategy should appear after /vault"

            # Verify parameter is shown for disable_strategy
            assert "/disable_strategy <id>" in help_text or "/disable_strategy" in help_text


# =============================================================================
# Tests for create_app handler registration - Story 1-3 additional verification
# =============================================================================

class TestCreateAppStory13:
    """Tests for create_app function - Story 1-3 handler registration."""

    @pytest.mark.asyncio
    async def test_create_app_registers_disable_strategy_handler(self) -> None:
        """Test create_app registers disable_strategy command handler."""
        # Given
        with patch("main.TELEGRAM_BOT_TOKEN", "test_token"):
            from main import create_app

            # When
            app = create_app()

            # Then - CommandHandler.commands returns a list/tuple of command strings
            handlers = app.handlers[0]  # CommandHandler group
            # Collect all commands from handlers (commands is a tuple/list)
            handler_commands = []
            for handler in handlers:
                handler_commands.extend(handler.commands)

            assert "disable_strategy" in handler_commands, "disable_strategy handler should be registered"

    @pytest.mark.asyncio
    async def test_create_app_registers_disable_all_handler(self) -> None:
        """Test create_app registers disable_all command handler."""
        # Given
        with patch("main.TELEGRAM_BOT_TOKEN", "test_token"):
            from main import create_app

            # When
            app = create_app()

            # Then
            handlers = app.handlers[0]  # CommandHandler group
            handler_commands = []
            for handler in handlers:
                handler_commands.extend(handler.commands)

            assert "disable_all" in handler_commands, "disable_all handler should be registered"

    @pytest.mark.asyncio
    async def test_create_app_registers_all_command_handlers(self) -> None:
        """Test create_app registers all expected command handlers."""
        # Given
        with patch("main.TELEGRAM_BOT_TOKEN", "test_token"):
            from main import create_app

            # When
            app = create_app()

            # Then
            handlers = app.handlers[0]  # CommandHandler group
            handler_commands = []
            for handler in handlers:
                handler_commands.extend(handler.commands)

            # Verify all expected handlers are registered
            expected_handlers = [
                "start",
                "help",
                "balance",
                "pnl",
                "positions",
                "activity",
                "swaps",
                "strategies",
                "vault",
                "disable_strategy",  # NEW - Story 1-3
                "disable_all",       # NEW - Story 1-3
            ]

            for expected in expected_handlers:
                assert expected in handler_commands, f"Handler '{expected}' should be registered"
