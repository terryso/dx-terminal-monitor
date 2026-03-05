"""
Unit tests for Story 6.4: New Coin Launch Schedule

Tests for: api.get_launch_schedule(), cmd_launches command handler

ATDD Checklist:
- [ ] AC1: Add get_launch_schedule() method to api.py TerminalAPI class
- [ ] AC2: Add cmd_launches command handler in commands/query.py
- [ ] AC3: Command format: /launches - no parameters required
- [ ] AC4: Format output: token name, launch time
- [ ] AC5: Handle empty results with appropriate message
- [ ] AC6: Register /launches command in Bot command menu
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
def mock_launch_schedule_response():
    """Create mock launch schedule API response.

    Based on actual API response structure from /launch-schedule endpoint.
    """
    return [
        {
            "tokenSymbol": "NEWTOKEN",
            "tokenName": "New Token",
            "timestamp": "2026-03-05T12:00:00Z",
        },
        {
            "tokenSymbol": "ANOTHER",
            "tokenName": "Another Token",
            "timestamp": "2026-03-10T08:00:00Z",
        },
    ]


@pytest.fixture
def mock_empty_launch_schedule_response():
    """Create mock empty launch schedule API response."""
    return []


# =============================================================================
# Test Class: TestGetLaunchSchedule (API Method Tests) - AC1
# =============================================================================


class TestGetLaunchSchedule:
    """Tests for get_launch_schedule API method - AC1."""

    @pytest.mark.asyncio
    async def test_get_launch_schedule_success(self, mock_launch_schedule_response):
        """Test get_launch_schedule returns list of launch items.

        AC1: Add get_launch_schedule() method to api.py that calls /launch-schedule endpoint
        """
        # Given
        from api import TerminalAPI

        api = TerminalAPI()

        with patch.object(api, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_launch_schedule_response

            # When
            result = await api.get_launch_schedule()

        # Then
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["tokenSymbol"] == "NEWTOKEN"
        assert result[1]["tokenSymbol"] == "ANOTHER"
        mock_get.assert_called_once_with("/launch-schedule")

    @pytest.mark.asyncio
    async def test_get_launch_schedule_empty(self, mock_empty_launch_schedule_response):
        """Test get_launch_schedule returns empty list when no launches."""
        # Given
        from api import TerminalAPI

        api = TerminalAPI()

        with patch.object(api, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_empty_launch_schedule_response

            # When
            result = await api.get_launch_schedule()

        # Then
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 0
        mock_get.assert_called_once_with("/launch-schedule")

    @pytest.mark.asyncio
    async def test_get_launch_schedule_api_error(self):
        """Test get_launch_schedule handles API errors."""
        # Given
        from api import TerminalAPI

        api = TerminalAPI()

        with patch.object(api, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {"error": "HTTP 500"}

            # When
            result = await api.get_launch_schedule()

        # Then
        assert "error" in result
        mock_get.assert_called_once_with("/launch-schedule")


# =============================================================================
# Test Class: TestCmdLaunches (Command Handler Tests) - AC2, AC3, AC4, AC5
# =============================================================================


class TestCmdLaunches:
    """Tests for cmd_launches command handler - AC2, AC3, AC4, AC5."""

    @pytest.mark.asyncio
    async def test_cmd_launches_success(
        self, mock_update, mock_context, mock_launch_schedule_response
    ):
        """Test normal query - cmd_launches returns formatted launch schedule.

        AC2: Add cmd_launches command handler in commands/query.py
        AC3: Command format: /launches - no parameters required
        AC4: Format output: token name, launch time
        """
        # Given
        mock_api = AsyncMock()
        mock_api.get_launch_schedule = AsyncMock(return_value=mock_launch_schedule_response)

        with (
            patch("commands.query.authorized", return_value=True),
            patch("commands.query._get_api") as mock_get_api,
        ):
            mock_get_api.return_value = mock_api
            from commands.query import cmd_launches

            # When
            await cmd_launches(mock_update, mock_context)

        # Then
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "Launch Schedule" in call_args or "Launch" in call_args
        assert "NEWTOKEN" in call_args
        assert "ANOTHER" in call_args
        # AC4: Check for launch time formatting
        assert "2026-03-05" in call_args or "12:00" in call_args

    @pytest.mark.asyncio
    async def test_cmd_launches_unauthorized(self, mock_update, mock_context):
        """Test unauthorized user is rejected."""
        # Given
        mock_update.effective_user.id = 99999  # Non-authorized user

        with patch("commands.query.authorized", return_value=False):
            from commands.query import cmd_launches

            # When
            await cmd_launches(mock_update, mock_context)

        # Then
        # Should not call reply_text since user is not authorized
        mock_update.message.reply_text.assert_not_called()

    @pytest.mark.asyncio
    async def test_cmd_launches_empty_results(
        self, mock_update, mock_context, mock_empty_launch_schedule_response
    ):
        """Test empty results displays appropriate message.

        AC5: Handle empty results with appropriate message
        """
        # Given
        mock_api = AsyncMock()
        mock_api.get_launch_schedule = AsyncMock(return_value=mock_empty_launch_schedule_response)

        with (
            patch("commands.query.authorized", return_value=True),
            patch("commands.query._get_api") as mock_get_api,
        ):
            mock_get_api.return_value = mock_api
            from commands.query import cmd_launches

            # When
            await cmd_launches(mock_update, mock_context)

        # Then
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "No upcoming launches" in call_args or "No launches" in call_args.lower()

    @pytest.mark.asyncio
    async def test_cmd_launches_api_error(self, mock_update, mock_context):
        """Test API error message display."""
        # Given
        mock_api = AsyncMock()
        mock_api.get_launch_schedule = AsyncMock(return_value={"error": "HTTP 500"})

        with (
            patch("commands.query.authorized", return_value=True),
            patch("commands.query._get_api") as mock_get_api,
        ):
            mock_get_api.return_value = mock_api
            from commands.query import cmd_launches

            # When
            await cmd_launches(mock_update, mock_context)

        # Then
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "Error" in call_args or "error" in call_args.lower()


# =============================================================================
# Test Class: TestCommandRegistration - AC6
# =============================================================================


class TestCommandRegistration:
    """Tests for launches command registration - AC6."""

    def test_cmd_launches_exported_from_query(self):
        """Test that cmd_launches is exported from commands.query module."""
        try:
            from commands.query import cmd_launches

            assert cmd_launches is not None
        except ImportError:
            pytest.fail("cmd_launches not exported from commands.query")

    def test_cmd_launches_in_all_exports(self):
        """Test that cmd_launches is in __all__ list."""
        import commands

        if hasattr(commands, "__all__"):
            assert "cmd_launches" in commands.__all__
        else:
            # Verify the function exists
            assert hasattr(commands, "cmd_launches")

    @pytest.mark.asyncio
    async def test_launches_command_in_bot_commands(self):
        """Test that launches command is in bot commands.

        AC6: Register /launches command in Bot command menu
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
        assert "launches" in command_names

    @pytest.mark.asyncio
    async def test_cmd_start_includes_launches_help(self):
        """Test that /start help text includes /launches command."""
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
        assert "/launches" in call_args


# =============================================================================
# Test Class: TestOutputFormatting - AC4
# =============================================================================


class TestOutputFormatting:
    """Tests for output formatting - AC4."""

    @pytest.mark.asyncio
    async def test_output_format_includes_token_name(
        self, mock_update, mock_context, mock_launch_schedule_response
    ):
        """Test output includes token name/symbol - AC4."""
        # Given
        mock_api = AsyncMock()
        mock_api.get_launch_schedule = AsyncMock(return_value=mock_launch_schedule_response)

        with (
            patch("commands.query.authorized", return_value=True),
            patch("commands.query._get_api") as mock_get_api,
        ):
            mock_get_api.return_value = mock_api
            from commands.query import cmd_launches

            # When
            await cmd_launches(mock_update, mock_context)

        # Then
        call_args = mock_update.message.reply_text.call_args[0][0]
        # Should include token symbol
        assert "NEWTOKEN" in call_args
        assert "ANOTHER" in call_args

    @pytest.mark.asyncio
    async def test_output_format_includes_launch_time(
        self, mock_update, mock_context, mock_launch_schedule_response
    ):
        """Test output includes launch time - AC4."""
        # Given
        mock_api = AsyncMock()
        mock_api.get_launch_schedule = AsyncMock(return_value=mock_launch_schedule_response)

        with (
            patch("commands.query.authorized", return_value=True),
            patch("commands.query._get_api") as mock_get_api,
        ):
            mock_get_api.return_value = mock_api
            from commands.query import cmd_launches

            # When
            await cmd_launches(mock_update, mock_context)

        # Then
        call_args = mock_update.message.reply_text.call_args[0][0]
        # Should include launch time (formatted)
        assert "2026-03-05" in call_args or "12:00" in call_args or "Launch Time" in call_args

    @pytest.mark.asyncio
    async def test_output_format_includes_token_names(
        self, mock_update, mock_context, mock_launch_schedule_response
    ):
        """Test output includes token full names - AC4."""
        # Given
        mock_api = AsyncMock()
        mock_api.get_launch_schedule = AsyncMock(return_value=mock_launch_schedule_response)

        with (
            patch("commands.query.authorized", return_value=True),
            patch("commands.query._get_api") as mock_get_api,
        ):
            mock_get_api.return_value = mock_api
            from commands.query import cmd_launches

            # When
            await cmd_launches(mock_update, mock_context)

        # Then
        call_args = mock_update.message.reply_text.call_args[0][0]
        # Should include token names
        assert "New Token" in call_args or "Another Token" in call_args or "Name:" in call_args
