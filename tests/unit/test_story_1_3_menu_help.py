"""
Unit tests for Story 1-3: Update command menu and help documentation.

Tests for: post_init registers new commands, cmd_start includes new help text,
create_app registers new handlers.

Priority: P2 (Documentation update, low risk)
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

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
        """Test post_init registers all expected commands."""
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

        # All expected commands including the new ones from Story 1-3, 2-1, 2-2, 3-1, 3-2, 4-1, 5-1, 5-2, 5-3, 6-1, 6-4, 6-5, 7-1
        expected_commands = [
            "start",
            "balance",
            "pnl",
            "positions",
            "activity",
            "swaps",
            "strategies",
            "vault",
            "price",             # Story 6-1
            "tokens",            # Story 6-2
            "token",             # Story 6-3
            "launches",          # Story 6-4
            "leaderboard",       # Story 6-5
            "tweets",            # Story 6-6
            "deposits",          # Story 5-1
            "pnl_history",       # Story 5-2
            "deposit",           # Story 5-3
            "add_strategy",      # Story 2-1
            "disable_strategy",  # Story 1-3
            "disable_all",       # Story 1-3
            "pause",             # Story 2-2
            "resume",            # Story 2-2
            "update_settings",   # Story 3-1
            "withdraw",          # Story 3-2
            "monitor_status",    # Story 4-1
            "monitor_start",     # Story 4-1
            "monitor_stop",      # Story 4-1
            "report_on",         # Story 7-1
            "report_off",        # Story 7-1
            "alert_pnl",         # Story 7-2
            "alert_position",    # Story 7-2
            "alert_status",      # Story 7-2
        ]

        assert len(command_names) == len(expected_commands), f"Expected {len(expected_commands)} commands, got {len(command_names)}"
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

        # Mock authorized() to return True for this test
        with patch("commands.query.authorized", return_value=True):
            from commands.query import cmd_start

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

        # Mock authorized() to return True for this test
        with patch("commands.query.authorized", return_value=True):
            from commands.query import cmd_start

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

        # Mock authorized() to return True for this test
        with patch("commands.query.authorized", return_value=True):
            from commands.query import cmd_start

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

    def _extract_handler_commands(self, handlers) -> list:
        """Extract commands from handlers, handling both CommandHandler and ConversationHandler."""
        handler_commands = []
        for handler in handlers:
            # CommandHandler has 'commands' attribute
            if hasattr(handler, 'commands'):
                handler_commands.extend(handler.commands)
            # ConversationHandler has 'entry_points' with CommandHandlers inside
            elif hasattr(handler, 'entry_points'):
                for entry_point in handler.entry_points:
                    if hasattr(entry_point, 'commands'):
                        handler_commands.extend(entry_point.commands)
        return handler_commands

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
            handler_commands = self._extract_handler_commands(handlers)

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
            handler_commands = self._extract_handler_commands(handlers)

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
            handler_commands = self._extract_handler_commands(handlers)

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
