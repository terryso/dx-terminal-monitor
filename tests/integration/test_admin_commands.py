"""
Integration tests for admin commands module (AC 4, AC 9)

Tests for: commands/admin.py command handlers
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# =============================================================================
# Tests for cmd_pause (AC 4, AC 9)
# =============================================================================

class TestCmdPauseRefactored:
    """Tests for /pause command after refactoring."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_pause_non_admin_rejected(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /pause rejects non-admin users (AC 4)."""
        # Given
        from commands.admin import cmd_pause

        with patch("commands.admin.is_admin", return_value=False):
            # When
            await cmd_pause(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "Unauthorized" in call_args

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_pause_success(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /pause successfully pauses vault."""
        # Given
        from commands.admin import cmd_pause

        mock_vault_response = {"paused": False}
        mock_pause_response = {"success": True, "transactionHash": "0xabc123"}

        mock_api = MagicMock()
        mock_api.get_vault = AsyncMock(return_value=mock_vault_response)
        mock_contract = MagicMock()
        mock_contract.pause_vault = AsyncMock(return_value=mock_pause_response)

        with patch("commands.admin.is_admin", return_value=True), \
             patch("commands.admin._get_api", return_value=mock_api), \
             patch("commands.admin._get_contract", return_value=mock_contract):

            # When
            await cmd_pause(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "paused" in call_args.lower()

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_pause_contract_failure(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /pause handles contract failure (AC 9)."""
        # Given
        from commands.admin import cmd_pause

        mock_vault_response = {"paused": False}
        mock_pause_response = {"success": False, "error": "Transaction reverted"}

        mock_api = MagicMock()
        mock_api.get_vault = AsyncMock(return_value=mock_vault_response)
        mock_contract = MagicMock()
        mock_contract.pause_vault = AsyncMock(return_value=mock_pause_response)

        with patch("commands.admin.is_admin", return_value=True), \
             patch("commands.admin._get_api", return_value=mock_api), \
             patch("commands.admin._get_contract", return_value=mock_contract):

            # When
            await cmd_pause(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "failed" in call_args.lower()


class TestCmdResumeRefactored:
    """Tests for /resume command after refactoring."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_resume_non_admin_rejected(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /resume rejects non-admin users (AC 4)."""
        # Given
        from commands.admin import cmd_resume

        with patch("commands.admin.is_admin", return_value=False):
            # When
            await cmd_resume(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "Unauthorized" in call_args

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_resume_success(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /resume successfully resumes vault."""
        # Given
        from commands.admin import cmd_resume

        mock_vault_response = {"paused": True}
        mock_resume_response = {"success": True, "transactionHash": "0xdef456"}

        mock_api = MagicMock()
        mock_api.get_vault = AsyncMock(return_value=mock_vault_response)
        mock_contract = MagicMock()
        mock_contract.pause_vault = AsyncMock(return_value=mock_resume_response)

        with patch("commands.admin.is_admin", return_value=True), \
             patch("commands.admin._get_api", return_value=mock_api), \
             patch("commands.admin._get_contract", return_value=mock_contract):

            # When
            await cmd_resume(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "resumed" in call_args.lower()


class TestCmdAddStrategyRefactored:
    """Tests for /add_strategy command after refactoring."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_add_strategy_non_admin_rejected(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /add_strategy rejects non-admin users (AC 4)."""
        # Given
        from commands.admin import cmd_add_strategy

        with patch("commands.admin.is_admin", return_value=False):
            # When
            await cmd_add_strategy(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "Unauthorized" in call_args


class TestCmdDisableStrategyRefactored:
    """Tests for /disable_strategy command after refactoring."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_disable_strategy_non_admin_rejected(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /disable_strategy rejects non-admin users (AC 4)."""
        # Given
        from commands.admin import cmd_disable_strategy

        with patch("commands.admin.is_admin", return_value=False):
            mock_telegram_context.args = ["1"]
            # When
            await cmd_disable_strategy(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "Unauthorized" in call_args


class TestCmdDisableAllRefactored:
    """Tests for /disable_all command after refactoring."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_disable_all_non_admin_rejected(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /disable_all rejects non-admin users (AC 4)."""
        # Given
        from commands.admin import cmd_disable_all

        with patch("commands.admin.is_admin", return_value=False):
            # When
            await cmd_disable_all(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "Unauthorized" in call_args


class TestCmdUpdateSettingsRefactored:
    """Tests for /update_settings command after refactoring."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_update_settings_non_admin_rejected(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /update_settings rejects non-admin users (AC 4)."""
        # Given
        from commands.admin import cmd_update_settings

        with patch("commands.admin.is_admin", return_value=False):
            mock_telegram_context.args = ["max_trade=1000"]
            # When
            await cmd_update_settings(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "Unauthorized" in call_args

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_update_settings_contract_failure(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /update_settings handles contract failure (AC 9)."""
        # Given
        from commands.admin import cmd_update_settings

        mock_vault_response = {"maxTradeAmount": 1000, "slippageBps": 50}
        mock_update_response = {"success": False, "error": "Gas estimation failed"}

        mock_api = MagicMock()
        mock_api.get_vault = AsyncMock(return_value=mock_vault_response)
        mock_contract = MagicMock()
        mock_contract.update_settings = AsyncMock(return_value=mock_update_response)

        with patch("commands.admin.is_admin", return_value=True), \
             patch("commands.admin._get_api", return_value=mock_api), \
             patch("commands.admin._get_contract", return_value=mock_contract):

            mock_telegram_context.args = ["max_trade=2000"]
            # When
            await cmd_update_settings(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "failed" in call_args.lower() or "error" in call_args.lower()
