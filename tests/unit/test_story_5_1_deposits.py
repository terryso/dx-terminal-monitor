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
        # Given - API returns flat structure with amount at top level
        mock_api_response = {
            "items": [
                {
                    "type": "deposit",
                    "amount": "1000000000000000000",  # 1 ETH
                    "blockNumber": 42787368,
                    "transactionHash": "0xf0460c3e8afde09a9dfd563170b1cfc4f5f40be8285bd72de81c881644f1cde0",
                },
                {
                    "type": "withdrawal",
                    "amount": "500000000000000000",  # 0.5 ETH
                    "blockNumber": 42772431,
                    "transactionHash": "0x11946c44f5c0e8cda6a3d3b101556f3e5a7c5e6d5400b71d116cb30f2b37e8ee",
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
        assert "Deposit/Withdrawal History" in call_args
        assert "Deposit" in call_args
        assert "Withdraw" in call_args
        assert "1.000000" in call_args  # 1 ETH
        assert "0.500000" in call_args  # 0.5 ETH

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
        assert "No deposit/withdrawal records" in call_args

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
        assert "Error:" in call_args
        assert "HTTP 500" in call_args

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
