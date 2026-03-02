"""
Unit tests for story 5.1: deposits history command (atdd red phase)
Tests for:
- cmd_deposits_success
- cmd_deposits_with_limit
- cmd_deposits_empty
- cmd_deposits_api_error
- cmd_deposits_unauthorized
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# =============================================================================
# Tests for cmd_deposits
# =============================================================================


class TestCmdDeposits:
    """Tests for /deposits command."""

    @pytest.mark.asyncio
    async def test_deposits_success(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test normal query - cmd_deposits returns formatted deposit/ withdrawal history."""
        # Given
        mock_api_response = {
            "items": [
                {
                    "type": "deposit",
                    "timestamp": "2026-03-01T12:00:00Z",
                    "status": "Confirmed",
                    "deposit": {"amountWei": "1000000000000000000"},  # 1 ETH
                },
                {
                    "type": "withdrawal",
                    "timestamp": "2026-03-02T14:30:00Z",
                    "status": "Confirmed",
                    "withdrawal": {"amountWei": "500000000000000000"},  # 0.5 ETH
                },
            ]
        }

        with (
            patch("commands.query.authorized", return_value=True),
            patch("commands.query._get_api") as mock_get_api,
        ):
            mock_api = MagicMock()
            mock_api.get_deposits_withdrawals = AsyncMock(return_value=mock_api_response)
            mock_get_api.return_value = mock_api
            from commands.query import cmd_deposits

            # When
            await cmd_deposits(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "存取款历史" in call_args
        assert "存入" in call_args
        assert "取出" in call_args
        assert "1.000000" in call_args  # 1 ETH
        assert "0.500000" in call_args  # 0.5 ETH
        assert "Confirmed" in call_args

    @pytest.mark.asyncio
    async def test_deposits_with_limit(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test custom limit - cmd_deposits correctly passes limit to to API."""
        # Given
        mock_telegram_context.args = ["20"]

        with (
            patch("commands.query.authorized", return_value=True),
            patch("commands.query._get_api") as mock_get_api,
        ):
            mock_api = MagicMock()
            mock_api.get_deposits_withdrawals = AsyncMock(return_value={"items": []})
            mock_get_api.return_value = mock_api
            from commands.query import cmd_deposits

            # When
            await cmd_deposits(mock_telegram_update, mock_telegram_context)

            # Then
            mock_api.get_deposits_withdrawals.assert_called_once_with(20)

    @pytest.mark.asyncio
    async def test_deposits_empty(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test empty results - cmd_deposits returns friendly message."""
        # Given
        mock_api_response = {"items": []}

        with (
            patch("commands.query.authorized", return_value=True),
            patch("commands.query._get_api") as mock_get_api,
        ):
            mock_api = MagicMock()
            mock_api.get_deposits_withdrawals = AsyncMock(return_value=mock_api_response)
            mock_get_api.return_value = mock_api
            from commands.query import cmd_deposits

            # When
            await cmd_deposits(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "暂无存取款记录" in call_args

    @pytest.mark.asyncio
    async def test_deposits_api_error(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test API error handling - cmd_deposits displays error message."""
        # Given
        mock_api_response = {"error": "HTTP 500: Internal Server Error"}

        with (
            patch("commands.query.authorized", return_value=True),
            patch("commands.query._get_api") as mock_get_api,
        ):
            mock_api = MagicMock()
            mock_api.get_deposits_withdrawals = AsyncMock(return_value=mock_api_response)
            mock_get_api.return_value = mock_api
            from commands.query import cmd_deposits

            # When
            await cmd_deposits(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "错误" in call_args
        assert "HTTP 500" in call_args
        assert "Internal Server Error" in call_args

    @pytest.mark.asyncio
    async def test_deposits_unauthorized(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test unauthorized user - cmd_deposits rejects access."""
        # Given
        with patch("commands.query.authorized", return_value=False):
            from commands.query import cmd_deposits

            # When
            await cmd_deposits(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_not_called()
