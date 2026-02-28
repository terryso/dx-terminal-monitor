"""
Unit tests for Telegram bot command handlers.
"""

import pytest
from unittest.mock import MagicMock, patch

from tests.support.helpers import assert_valid_position


class TestAuthorizedFunction:
    """Tests for the authorized helper function."""

    def test_authorized_when_allowed_users_empty(self) -> None:
        """Test authorization passes when no allowed users configured."""
        # Given
        update = MagicMock()
        update.effective_user.id = 999

        # When allowed_users is empty, should return True
        with patch("main.ALLOWED_USERS", []):
            from main import authorized
            result = authorized(update)

        # Then
        assert result is True

    def test_authorized_when_user_in_allowed_list(self) -> None:
        """Test authorization passes for allowed user."""
        # Given
        update = MagicMock()
        update.effective_user.id = 123456789

        with patch("main.ALLOWED_USERS", [123456789]):
            from main import authorized
            result = authorized(update)

        # Then
        assert result is True

    def test_unauthorized_when_user_not_in_list(self) -> None:
        """Test authorization fails for non-allowed user."""
        # Given
        update = MagicMock()
        update.effective_user.id = 999999

        # Patch where the function is defined (main module)
        with patch("main.ALLOWED_USERS", [123456789]):
            from main import authorized
            result = authorized(update)

        # Then
        assert result is False


class TestCommandHandlers:
    """Tests for bot command handlers."""

    @pytest.mark.asyncio
    async def test_start_command_sends_help_text(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /start command sends help text."""
        # Given
        from main import cmd_start

        # When
        with patch("main.authorized", return_value=True):
            await cmd_start(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "Terminal Markets Monitor" in call_args
        assert "/balance" in call_args

    @pytest.mark.asyncio
    async def test_start_command_unauthorized(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /start command handles unauthorized user."""
        # Given
        from main import cmd_start

        # When
        with patch("main.authorized", return_value=False):
            await cmd_start(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once_with("Unauthorized")


class TestPositionValidation:
    """Tests for position data validation."""

    def test_valid_position(self, position_factory) -> None:
        """Test valid position passes validation."""
        position = position_factory.create()
        assert_valid_position(position)

    def test_missing_symbol(self) -> None:
        """Test position missing tokenSymbol fails."""
        position = {
            "currentValueUsd": "1000.00",
            "totalPnlUsd": "100.00",
        }
        with pytest.raises(AssertionError, match="tokenSymbol"):
            assert_valid_position(position)
