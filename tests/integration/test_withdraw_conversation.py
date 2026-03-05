"""
Integration tests for withdraw conversation handler (AC 6)

Tests for: commands/withdraw.py ConversationHandler
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# =============================================================================
# Tests for cmd_withdraw (AC 6)
# =============================================================================


class TestCmdWithdrawRefactored:
    """Tests for /withdraw command after refactoring."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_withdraw_starts_conversation(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /withdraw starts conversation handler (AC 6)."""
        # Given
        from commands.withdraw import _pending_withdrawals, cmd_withdraw

        _pending_withdrawals.clear()
        mock_telegram_context.args = ["1.5"]
        mock_api = MagicMock()
        mock_api.get_positions = AsyncMock(
            return_value={
                "ethBalance": "5000000000000000000"  # 5 ETH
            }
        )

        with (
            patch("commands.withdraw.is_admin", return_value=True),
            patch("commands.withdraw._get_api", return_value=mock_api),
        ):
            # When
            result = await cmd_withdraw(mock_telegram_update, mock_telegram_context)

        # Then
        # ConversationHandler should return WAITING_CONFIRMATION state
        assert result == 1  # WAITING_CONFIRMATION constant

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_withdraw_non_admin_rejected(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /withdraw rejects non-admin users."""
        # Given
        from commands.withdraw import cmd_withdraw

        mock_telegram_context.args = ["1.5"]

        with patch("commands.withdraw.is_admin", return_value=False):
            # When
            result = await cmd_withdraw(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "Unauthorized" in call_args or "unauthorized" in call_args.lower()

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_withdraw_no_args_shows_usage(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /withdraw without args shows usage message."""
        # Given
        from commands.withdraw import cmd_withdraw

        mock_telegram_context.args = None

        with patch("commands.withdraw.is_admin", return_value=True):
            # When
            await cmd_withdraw(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "Usage" in call_args


# =============================================================================
# Tests for handle_withdraw_confirm (AC 6)
# =============================================================================


class TestHandleWithdrawConfirmRefactored:
    """Tests for withdraw confirmation handler after refactoring."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_withdraw_confirm_executes_withdrawal(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test withdraw confirmation executes the withdrawal (AC 6)."""
        # Given
        from commands.withdraw import _pending_withdrawals, handle_withdraw_confirm

        user_id = 123456789
        mock_telegram_update.effective_user.id = user_id
        mock_telegram_update.message.text = "Y"  # Confirmation
        _pending_withdrawals.clear()
        _pending_withdrawals[user_id] = "1.5"  # Stores just the amount string

        mock_contract = MagicMock()
        mock_contract.withdraw_eth = AsyncMock(
            return_value={"success": True, "transactionHash": "0xtxhash"}
        )

        with (
            patch("commands.withdraw.is_admin", return_value=True),
            patch("commands.withdraw._get_contract", return_value=mock_contract),
        ):
            # When
            result = await handle_withdraw_confirm(mock_telegram_update, mock_telegram_context)

        # Then
        mock_contract.withdraw_eth.assert_called_once()
        mock_telegram_update.message.reply_text.assert_called()
        # Should return END to end conversation
        assert result == -1  # ConversationHandler.END

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_withdraw_confirm_cancel_cancels(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test withdraw cancel cancels the withdrawal."""
        # Given
        from commands.withdraw import _pending_withdrawals, handle_withdraw_confirm

        user_id = 123456789
        mock_telegram_update.effective_user.id = user_id
        mock_telegram_update.message.text = "N"  # Cancel
        _pending_withdrawals.clear()
        _pending_withdrawals[user_id] = "1.5"

        # When
        result = await handle_withdraw_confirm(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called()
        assert user_id not in _pending_withdrawals


# =============================================================================
# Tests for handle_withdraw_cancel (AC 6)
# =============================================================================


class TestHandleWithdrawCancelRefactored:
    """Tests for withdraw cancel handler after refactoring."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_withdraw_cancel_clears_pending(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /cancel clears pending withdrawal."""
        # Given
        from commands.withdraw import _pending_withdrawals, handle_withdraw_cancel

        user_id = 123456789
        mock_telegram_update.effective_user.id = user_id
        _pending_withdrawals.clear()
        _pending_withdrawals[user_id] = "1.5"  # Just the amount string

        # When
        result = await handle_withdraw_cancel(mock_telegram_update, mock_telegram_context)

        # Then
        assert user_id not in _pending_withdrawals
        mock_telegram_update.message.reply_text.assert_called()
        assert result == -1  # ConversationHandler.END


# =============================================================================
# Tests for create_withdraw_handler (AC 6)
# =============================================================================


class TestCreateWithdrawHandlerRefactored:
    """Tests for create_withdraw_handler factory function."""

    @pytest.mark.integration
    def test_create_withdraw_handler_returns_handler(self) -> None:
        """Test create_withdraw_handler returns ConversationHandler (AC 6)."""
        # Given
        from telegram.ext import ConversationHandler

        from commands.withdraw import create_withdraw_handler

        # When
        handler = create_withdraw_handler()

        # Then
        assert isinstance(handler, ConversationHandler)
        assert len(handler.entry_points) == 1
        assert 1 in handler.states  # WAITING_CONFIRMATION = 1

    @pytest.mark.integration
    def test_withdraw_handler_has_cancel_fallback(self) -> None:
        """Test withdraw handler has cancel fallback."""
        # Given
        from commands.withdraw import create_withdraw_handler

        # When
        handler = create_withdraw_handler()

        # Then
        assert len(handler.fallbacks) >= 1
