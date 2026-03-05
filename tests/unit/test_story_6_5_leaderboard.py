"""
Unit tests for Story 6.5: Leaderboard Query

Tests for: api.get_leaderboard(), cmd_leaderboard command handler

ATDD Checklist:
- [ ] AC1: Add get_leaderboard(limit) method to api.py TerminalAPI class
- [ ] AC2: Add cmd_leaderboard command handler in commands/query.py
- [ ] AC3: Command format: /leaderboard [limit] - optional limit parameter (default 10)
- [ ] AC4: Format output: rank, vault name, PnL, return rate
- [ ] AC5: Handle empty results with appropriate message
- [ ] AC6: Register /leaderboard command in Bot command menu
- [ ] AC7: Add unit tests for the new command
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
def mock_leaderboard_response():
    """Create mock leaderboard API response.

    Based on actual API response structure from /leaderboard endpoint.
    """
    return {
        "totalCount": 3,
        "hasMoreItems": False,
        "items": [
            {
                "rank": 1,
                "nftName": "AlphaVault",
                "totalPnlUsd": 125000.00,
                "totalPnlPercent": 45.2,
            },
            {
                "rank": 2,
                "nftName": "DiamondHands",
                "totalPnlUsd": 89000.00,
                "totalPnlPercent": 32.1,
            },
            {
                "rank": 3,
                "nftName": "SmartTrader",
                "totalPnlUsd": 67500.00,
                "totalPnlPercent": 28.5,
            },
        ],
    }


@pytest.fixture
def mock_empty_leaderboard_response():
    """Create mock empty leaderboard API response."""
    return {"totalCount": 0, "hasMoreItems": False, "items": []}


@pytest.fixture
def mock_api_error_response():
    """Create mock API error response."""
    return {"error": "HTTP 500 - Internal Server Error"}


# =============================================================================
# Helper Functions (Data Factories)
# =============================================================================


def create_leaderboard_entry(overrides=None):
    """Create a single leaderboard entry with optional overrides.

    Args:
        overrides: Dict of fields to override defaults

    Returns:
        Dict with leaderboard entry data
    """
    defaults = {
        "rank": 1,
        "nftName": "TestVault",
        "totalPnlUsd": 50000.00,
        "totalPnlPercent": 15.5,
    }
    if overrides:
        defaults.update(overrides)
    return defaults


def create_leaderboard_entries(count):
    """Create multiple leaderboard entries.

    Args:
        count: Number of entries to create

    Returns:
        List of leaderboard entry dicts
    """
    entries = []
    for i in range(count):
        entries.append(
            create_leaderboard_entry(
                {
                    "rank": i + 1,
                    "nftName": f"Vault{i + 1}",
                    "totalPnlUsd": float(10000 * (count - i)),
                    "totalPnlPercent": float(10 + (count - i) * 2),
                }
            )
        )
    return entries


# =============================================================================
# Test Class: TestGetLeaderboard (API Method Tests) - AC1
# =============================================================================


class TestGetLeaderboard:
    """Tests for get_leaderboard API method - AC1."""

    @pytest.mark.asyncio
    async def test_get_leaderboard_success(self, mock_leaderboard_response):
        """Test get_leaderboard returns list of leaderboard items.

        AC1: Add get_leaderboard(limit) method to api.py that calls /leaderboard endpoint
        """
        # Given
        from api import TerminalAPI

        api = TerminalAPI()

        with patch.object(api, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_leaderboard_response

            # When
            result = await api.get_leaderboard()

        # Then
        assert result is not None
        assert isinstance(result, dict)
        assert "items" in result
        assert len(result["items"]) == 3
        assert result["items"][0]["nftName"] == "AlphaVault"
        assert result["items"][1]["nftName"] == "DiamondHands"
        assert result["items"][2]["nftName"] == "SmartTrader"
        mock_get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_leaderboard_with_custom_limit(self, mock_leaderboard_response):
        """Test get_leaderboard accepts custom limit parameter.

        AC1, AC3: Method should accept optional limit parameter
        """
        # Given
        from api import TerminalAPI

        api = TerminalAPI()

        with patch.object(api, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_leaderboard_response

            # When
            result = await api.get_leaderboard(limit=2)

        # Then
        assert result is not None
        # Verify limit and sortBy were passed as query parameters
        call_args = mock_get.call_args
        assert call_args[0][0] == "/leaderboard"
        assert call_args[0][1] == {"limit": 2, "sortBy": "total_pnl_usd"}

    @pytest.mark.asyncio
    async def test_get_leaderboard_empty(self, mock_empty_leaderboard_response):
        """Test get_leaderboard returns empty items when no data."""
        # Given
        from api import TerminalAPI

        api = TerminalAPI()

        with patch.object(api, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_empty_leaderboard_response

            # When
            result = await api.get_leaderboard()

        # Then
        assert result is not None
        assert isinstance(result, dict)
        assert "items" in result
        assert len(result["items"]) == 0
        mock_get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_leaderboard_api_error(self, mock_api_error_response):
        """Test get_leaderboard handles API errors."""
        # Given
        from api import TerminalAPI

        api = TerminalAPI()

        with patch.object(api, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_api_error_response

            # When
            result = await api.get_leaderboard()

        # Then
        assert "error" in result
        mock_get.assert_called_once()


# =============================================================================
# Test Class: TestCmdLeaderboard (Command Handler Tests) - AC2, AC3, AC4, AC5
# =============================================================================


class TestCmdLeaderboard:
    """Tests for cmd_leaderboard command handler - AC2, AC3, AC4, AC5."""

    @pytest.mark.asyncio
    async def test_cmd_leaderboard_success(
        self, mock_update, mock_context, mock_leaderboard_response
    ):
        """Test normal query - cmd_leaderboard returns formatted leaderboard.

        AC2: Add cmd_leaderboard command handler in commands/query.py
        AC4: Format output: rank, vault name, PnL, return rate
        """
        # Given
        mock_api = AsyncMock()
        mock_api.get_leaderboard = AsyncMock(return_value=mock_leaderboard_response)

        with (
            patch("commands.query.authorized", return_value=True),
            patch("commands.query._get_api") as mock_get_api,
        ):
            mock_get_api.return_value = mock_api
            from commands.query import cmd_leaderboard

            # When
            await cmd_leaderboard(mock_update, mock_context)

        # Then
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "Leaderboard" in call_args or "leaderboard" in call_args.lower()
        assert "AlphaVault" in call_args
        assert "DiamondHands" in call_args
        assert "SmartTrader" in call_args
        # AC4: Check for PnL formatting
        assert "125000" in call_args or "125,000" in call_args
        assert "45.2" in call_args or "45.2%" in call_args

    @pytest.mark.asyncio
    async def test_cmd_leaderboard_unauthorized(self, mock_update, mock_context):
        """Test unauthorized user is rejected."""
        # Given
        mock_update.effective_user.id = 99999  # Non-authorized user

        with patch("commands.query.authorized", return_value=False):
            from commands.query import cmd_leaderboard

            # When
            await cmd_leaderboard(mock_update, mock_context)

        # Then
        # Should not call reply_text since user is not authorized
        mock_update.message.reply_text.assert_not_called()

    @pytest.mark.asyncio
    async def test_cmd_leaderboard_empty_results(
        self, mock_update, mock_context, mock_empty_leaderboard_response
    ):
        """Test empty results displays appropriate message.

        AC5: Handle empty results with appropriate message
        """
        # Given
        mock_api = AsyncMock()
        mock_api.get_leaderboard = AsyncMock(return_value=mock_empty_leaderboard_response)

        with (
            patch("commands.query.authorized", return_value=True),
            patch("commands.query._get_api") as mock_get_api,
        ):
            mock_get_api.return_value = mock_api
            from commands.query import cmd_leaderboard

            # When
            await cmd_leaderboard(mock_update, mock_context)

        # Then
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert (
            "No leaderboard data" in call_args
            or "no leaderboard" in call_args.lower()
            or "empty" in call_args.lower()
        )

    @pytest.mark.asyncio
    async def test_cmd_leaderboard_api_error(
        self, mock_update, mock_context, mock_api_error_response
    ):
        """Test API error message display."""
        # Given
        mock_api = AsyncMock()
        mock_api.get_leaderboard = AsyncMock(return_value=mock_api_error_response)

        with (
            patch("commands.query.authorized", return_value=True),
            patch("commands.query._get_api") as mock_get_api,
        ):
            mock_get_api.return_value = mock_api
            from commands.query import cmd_leaderboard

            # When
            await cmd_leaderboard(mock_update, mock_context)

        # Then
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "Error" in call_args or "error" in call_args.lower()

    @pytest.mark.asyncio
    async def test_cmd_leaderboard_with_limit_arg(
        self, mock_update, mock_context, mock_leaderboard_response
    ):
        """Test command with custom limit argument.

        AC3: Command format: /leaderboard [limit] - optional limit parameter
        """
        # Given
        mock_context.args = ["5"]  # User passed limit argument
        mock_api = AsyncMock()
        mock_api.get_leaderboard = AsyncMock(return_value=mock_leaderboard_response)

        with (
            patch("commands.query.authorized", return_value=True),
            patch("commands.query._get_api") as mock_get_api,
        ):
            mock_get_api.return_value = mock_api
            from commands.query import cmd_leaderboard

            # When
            await cmd_leaderboard(mock_update, mock_context)

        # Then
        # Verify API was called with the limit from args
        mock_api.get_leaderboard.assert_called_once_with(5)

    @pytest.mark.asyncio
    async def test_cmd_leaderboard_invalid_limit_arg(
        self, mock_update, mock_context, mock_leaderboard_response
    ):
        """Test command with invalid limit argument uses default.

        AC3: Invalid/non-integer limit should use default (10)
        """
        # Given
        mock_context.args = ["invalid"]  # Invalid limit argument
        mock_api = AsyncMock()
        mock_api.get_leaderboard = AsyncMock(return_value=mock_leaderboard_response)

        with (
            patch("commands.query.authorized", return_value=True),
            patch("commands.query._get_api") as mock_get_api,
        ):
            mock_get_api.return_value = mock_api
            from commands.query import cmd_leaderboard

            # When
            await cmd_leaderboard(mock_update, mock_context)

        # Then
        # Verify API was called with default limit (10)
        mock_api.get_leaderboard.assert_called_once_with(10)


# =============================================================================
# Test Class: TestCommandRegistration - AC6
# =============================================================================


class TestCommandRegistration:
    """Tests for leaderboard command registration - AC6."""

    def test_cmd_leaderboard_exported_from_query(self):
        """Test that cmd_leaderboard is exported from commands.query module."""
        try:
            from commands.query import cmd_leaderboard

            assert cmd_leaderboard is not None
        except ImportError:
            pytest.fail("cmd_leaderboard not exported from commands.query")

    def test_cmd_leaderboard_in_all_exports(self):
        """Test that cmd_leaderboard is in __all__ list."""
        import commands

        if hasattr(commands, "__all__"):
            assert "cmd_leaderboard" in commands.__all__
        else:
            # Verify the function exists
            assert hasattr(commands, "cmd_leaderboard")

    @pytest.mark.asyncio
    async def test_leaderboard_command_in_bot_commands(self):
        """Test that leaderboard command is in bot commands.

        AC6: Register /leaderboard command in Bot command menu
        """
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
        assert "leaderboard" in command_names

    @pytest.mark.asyncio
    async def test_cmd_start_includes_leaderboard_help(self):
        """Test that /start help text includes /leaderboard command."""
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
        assert "/leaderboard" in call_args


# =============================================================================
# Test Class: TestOutputFormatting - AC4
# =============================================================================


class TestOutputFormatting:
    """Tests for output formatting - AC4."""

    @pytest.mark.asyncio
    async def test_output_format_includes_rank_and_name(
        self, mock_update, mock_context, mock_leaderboard_response
    ):
        """Test output includes rank number and vault name - AC4."""
        # Given
        mock_api = AsyncMock()
        mock_api.get_leaderboard = AsyncMock(return_value=mock_leaderboard_response)

        with (
            patch("commands.query.authorized", return_value=True),
            patch("commands.query._get_api") as mock_get_api,
        ):
            mock_get_api.return_value = mock_api
            from commands.query import cmd_leaderboard

            # When
            await cmd_leaderboard(mock_update, mock_context)

        # Then
        call_args = mock_update.message.reply_text.call_args[0][0]
        # Should include rank numbers (1., 2., 3.)
        assert "1." in call_args or "1)" in call_args
        assert "2." in call_args or "2)" in call_args
        assert "3." in call_args or "3)" in call_args
        # Should include vault names
        assert "AlphaVault" in call_args
        assert "DiamondHands" in call_args
        assert "SmartTrader" in call_args

    @pytest.mark.asyncio
    async def test_output_format_includes_pnl_and_return(
        self, mock_update, mock_context, mock_leaderboard_response
    ):
        """Test output includes PnL and return rate - AC4."""
        # Given
        mock_api = AsyncMock()
        mock_api.get_leaderboard = AsyncMock(return_value=mock_leaderboard_response)

        with (
            patch("commands.query.authorized", return_value=True),
            patch("commands.query._get_api") as mock_get_api,
        ):
            mock_get_api.return_value = mock_api
            from commands.query import cmd_leaderboard

            # When
            await cmd_leaderboard(mock_update, mock_context)

        # Then
        call_args = mock_update.message.reply_text.call_args[0][0]
        # Should include PnL values (formatted with $ or similar)
        assert "125000" in call_args or "125,000" in call_args or "PnL" in call_args
        # Should include return percentages
        assert "45.2" in call_args or "45.2%" in call_args or "Return" in call_args
