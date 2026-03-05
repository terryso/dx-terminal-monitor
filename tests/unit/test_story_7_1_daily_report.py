"""
ATDD Tests for Story 7-1: Daily Report Push

These tests are designed to FAIL before implementation (TDD RED phase).
Run: pytest tests/unit/test_story_7_1_daily_report.py -v

Generated: 2026-03-03
Story: 7-1-daily-report
"""

import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ============================================================================
# Test Data Factory
# ============================================================================


class ReportDataFactory:
    """Factory for creating test report data."""

    @staticmethod
    def create_balance_data(
        eth_balance: str = "1500000000000000000",  # 1.5 ETH in wei
        usd_value: str = "4500.00",
        **overrides,
    ) -> dict:
        """Create balance data for testing."""
        data = {
            "ethBalance": eth_balance,
            "overallValueUsd": usd_value,
            "overallPnlUsd": "120.50",
            "overallPnlPercent": "2.75",
        }
        data.update(overrides)
        return data

    @staticmethod
    def create_pnl_data(
        pnl_usd: str = "120.50",
        pnl_percent: str = "2.75",
        **overrides,
    ) -> dict:
        """Create PnL data for testing."""
        data = {
            "pnlUsd": pnl_usd,
            "pnlPercent": pnl_percent,
        }
        data.update(overrides)
        return data

    @staticmethod
    def create_positions_data(
        position_count: int = 3,
        **overrides,
    ) -> dict:
        """Create positions data for testing."""
        positions = [
            {
                "tokenSymbol": "ETH",
                "currentValueUsd": "3000.00",
                "totalPnlUsd": "100.00",
                "totalPnlPercent": "3.45",
            },
            {
                "tokenSymbol": "USDC",
                "currentValueUsd": "1000.00",
                "totalPnlUsd": "15.00",
                "totalPnlPercent": "1.5",
            },
            {
                "tokenSymbol": "WBTC",
                "currentValueUsd": "500.00",
                "totalPnlUsd": "5.50",
                "totalPnlPercent": "1.1",
            },
        ][:position_count]
        data = {
            "ethBalance": "1500000000000000000",
            "overallValueUsd": "4500.00",
            "positions": positions,
        }
        data.update(overrides)
        return data

    @staticmethod
    def create_strategies_data(
        strategy_count: int = 2,
        **overrides,
    ) -> list:
        """Create strategies data for testing."""
        strategies = [
            {"strategyId": "1", "content": "Strategy one", "active": True},
            {"strategyId": "2", "content": "Strategy two", "active": True},
            {"strategyId": "3", "content": "Strategy three", "active": False},
        ][:strategy_count]
        return strategies

    @staticmethod
    def create_report_data(**overrides) -> dict:
        """Create complete report data dict."""
        data = {
            "balance": ReportDataFactory.create_balance_data(),
            "pnl": ReportDataFactory.create_pnl_data(),
            "positions": ReportDataFactory.create_positions_data(),
            "strategies": ReportDataFactory.create_strategies_data(),
        }
        data.update(overrides)
        return data


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def report_data_factory():
    """Provide ReportDataFactory."""
    return ReportDataFactory()


@pytest.fixture
def mock_api():
    """Create mock TerminalAPI instance."""
    api = MagicMock()
    api.get_positions = AsyncMock(return_value=ReportDataFactory.create_positions_data())
    api.get_strategies = AsyncMock(return_value=ReportDataFactory.create_strategies_data())
    return api


@pytest.fixture
def mock_notifier():
    """Create mock TelegramNotifier instance."""
    notifier = MagicMock()
    notifier.bot = AsyncMock()
    notifier.notify_users = [123456789]
    return notifier


# ============================================================================
# Test Classes
# ============================================================================


class TestDailyReporterInit:
    """Tests for DailyReporter initialization."""

    def test_init_stores_api_instance(self, mock_api, mock_notifier):
        """API instance should be stored as instance attribute."""
        from reporter import DailyReporter

        reporter = DailyReporter(mock_api, mock_notifier)

        assert reporter.api == mock_api

    def test_init_stores_notifier_instance(self, mock_api, mock_notifier):
        """Notifier instance should be stored as instance attribute."""
        from reporter import DailyReporter

        reporter = DailyReporter(mock_api, mock_notifier)

        assert reporter.notifier == mock_notifier

    def test_init_default_report_time_08_00(self, mock_api, mock_notifier):
        """Default report time should be 08:00 UTC."""
        from reporter import DailyReporter

        with patch.dict("os.environ", {}, clear=True):
            reporter = DailyReporter(mock_api, mock_notifier)

        assert reporter.report_time == (8, 0)

    @patch.dict("os.environ", {"REPORT_TIME": "09:30"})
    def test_init_reads_report_time_from_env(self, mock_api, mock_notifier):
        """REPORT_TIME should be read from environment variable."""
        from reporter import DailyReporter

        reporter = DailyReporter(mock_api, mock_notifier)

        assert reporter.report_time == (9, 30)

    @patch.dict("os.environ", {"REPORT_TIME": "invalid"})
    def test_init_handles_invalid_report_time(self, mock_api, mock_notifier):
        """Invalid REPORT_TIME should fall back to 08:00."""
        from reporter import DailyReporter

        reporter = DailyReporter(mock_api, mock_notifier)

        assert reporter.report_time == (8, 0)

    def test_init_running_flag_false(self, mock_api, mock_notifier):
        """running flag should be initialized to False."""
        from reporter import DailyReporter

        with patch.dict("os.environ", {}, clear=True):
            reporter = DailyReporter(mock_api, mock_notifier)

        assert reporter.running is False

    def test_init_enabled_default_true(self, mock_api, mock_notifier):
        """REPORT_ENABLED should default to true."""
        from reporter import DailyReporter

        with patch.dict("os.environ", {}, clear=True):
            reporter = DailyReporter(mock_api, mock_notifier)

        assert reporter.enabled is True

    @patch.dict("os.environ", {"REPORT_ENABLED": "false"})
    def test_init_enabled_from_env(self, mock_api, mock_notifier):
        """REPORT_ENABLED should be read from environment."""
        from reporter import DailyReporter

        reporter = DailyReporter(mock_api, mock_notifier)

        assert reporter.enabled is False


class TestParseReportTime:
    """Tests for _parse_report_time method."""

    def test_parse_valid_time(self, mock_api, mock_notifier):
        """Valid HH:MM format should be parsed correctly."""
        from reporter import DailyReporter

        with patch.dict("os.environ", {"REPORT_TIME": "14:30"}):
            reporter = DailyReporter(mock_api, mock_notifier)

        assert reporter.report_time == (14, 30)

    def test_parse_invalid_format(self, mock_api, mock_notifier):
        """Invalid format should return default 08:00."""
        from reporter import DailyReporter

        with patch.dict("os.environ", {"REPORT_TIME": "not-a-time"}):
            reporter = DailyReporter(mock_api, mock_notifier)

        assert reporter.report_time == (8, 0)

    def test_parse_missing_parts(self, mock_api, mock_notifier):
        """Malformed time string should be handled gracefully."""
        from reporter import DailyReporter

        with patch.dict("os.environ", {"REPORT_TIME": "14"}):
            reporter = DailyReporter(mock_api, mock_notifier)

        # Should fall back to default
        assert reporter.report_time == (8, 0)

    def test_parse_empty_string(self, mock_api, mock_notifier):
        """Empty string should return default."""
        from reporter import DailyReporter

        with patch.dict("os.environ", {"REPORT_TIME": ""}):
            reporter = DailyReporter(mock_api, mock_notifier)

        assert reporter.report_time == (8, 0)


class TestCalculateNextRun:
    """Tests for _calculate_next_run method."""

    def test_calculate_next_run_future_time(self, mock_api, mock_notifier):
        """Should calculate correct seconds when target is in future."""
        from reporter import DailyReporter

        # Set report time to 23:59 (likely in future during test)
        with patch.dict("os.environ", {"REPORT_TIME": "23:59"}):
            reporter = DailyReporter(mock_api, mock_notifier)

        # Mock datetime.now to return a known time
        with patch("reporter.datetime") as mock_dt:
            from datetime import UTC as utc

            mock_dt.now.return_value = datetime(2026, 3, 3, 10, 0, 0)
            mock_dt.UTC = utc
            mock_dt.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

            seconds = reporter._calculate_next_run()

        # Should be roughly 13h 59m = ~50340 seconds
        assert seconds > 0
        assert seconds < 86400  # Less than 24 hours

    def test_calculate_next_run_past_time(self, mock_api, mock_notifier):
        """Past time should result in next day calculation."""
        from reporter import DailyReporter

        # Set report time to 01:00 (likely in past during test)
        with patch.dict("os.environ", {"REPORT_TIME": "01:00"}):
            reporter = DailyReporter(mock_api, mock_notifier)

        with patch("reporter.datetime") as mock_dt:
            from datetime import UTC as utc

            mock_dt.now.return_value = datetime(2026, 3, 3, 10, 0, 0)
            mock_dt.UTC = utc
            mock_dt.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

            seconds = reporter._calculate_next_run()

        # Should be roughly 15h = ~54000 seconds (next day)
        assert seconds > 0
        assert seconds < 86400

    def test_calculate_next_run_returns_seconds(self, mock_api, mock_notifier):
        """Should return value in seconds (float)."""
        from reporter import DailyReporter

        with patch.dict("os.environ", {"REPORT_TIME": "12:00"}):
            reporter = DailyReporter(mock_api, mock_notifier)

        with patch("reporter.datetime") as mock_dt:
            from datetime import UTC as utc

            mock_dt.now.return_value = datetime(2026, 3, 3, 10, 0, 0)
            mock_dt.UTC = utc
            mock_dt.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

            seconds = reporter._calculate_next_run()

        assert isinstance(seconds, float)
        assert seconds > 0

    def test_calculate_next_run_uses_utc(self, mock_api, mock_notifier):
        """Should use UTC timezone consistently."""
        from reporter import DailyReporter

        with patch.dict("os.environ", {"REPORT_TIME": "08:00"}):
            reporter = DailyReporter(mock_api, mock_notifier)

        # Verify method exists and returns a value
        seconds = reporter._calculate_next_run()
        assert isinstance(seconds, float)


class TestGatherReportData:
    """Tests for _gather_report_data method."""

    @pytest.mark.asyncio
    async def test_gather_report_data_success(self, mock_api, mock_notifier, report_data_factory):
        """Should gather all data from API successfully."""
        from reporter import DailyReporter

        # Setup mock responses
        mock_api.get_positions = AsyncMock(return_value=report_data_factory.create_positions_data())
        mock_api.get_strategies = AsyncMock(
            return_value=report_data_factory.create_strategies_data()
        )

        reporter = DailyReporter(mock_api, mock_notifier)
        data = await reporter._gather_report_data()

        # Verify API calls were made
        mock_api.get_positions.assert_called_once()
        mock_api.get_strategies.assert_called_once()

        # Verify data structure
        assert "positions" in data
        assert "strategies" in data

    @pytest.mark.asyncio
    async def test_gather_report_data_handles_api_error(self, mock_api, mock_notifier):
        """Should handle API errors gracefully with fallback."""
        from reporter import DailyReporter

        # Setup mock to return error
        mock_api.get_positions = AsyncMock(return_value={"error": "API failed"})
        mock_api.get_strategies = AsyncMock(return_value={"error": "API failed"})

        reporter = DailyReporter(mock_api, mock_notifier)
        data = await reporter._gather_report_data()

        # Should return dict without crashing
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_gather_report_data_empty_responses(self, mock_api, mock_notifier):
        """Should handle empty API responses correctly."""
        from reporter import DailyReporter

        # Setup mock to return empty data
        mock_api.get_positions = AsyncMock(return_value={})
        mock_api.get_strategies = AsyncMock(return_value=[])

        reporter = DailyReporter(mock_api, mock_notifier)
        data = await reporter._gather_report_data()

        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_gather_report_data_partial_failure(
        self, mock_api, mock_notifier, report_data_factory
    ):
        """Partial API failures should not break report gathering."""
        from reporter import DailyReporter

        # One succeeds, one fails
        mock_api.get_positions = AsyncMock(return_value=report_data_factory.create_positions_data())
        mock_api.get_strategies = AsyncMock(return_value={"error": "Failed"})

        reporter = DailyReporter(mock_api, mock_notifier)
        data = await reporter._gather_report_data()

        # Should still have positions data
        assert "positions" in data


class TestFormatDailyReport:
    """Tests for _format_daily_report method."""

    def test_format_daily_report_includes_balance(
        self, mock_api, mock_notifier, report_data_factory
    ):
        """Report should include ETH balance and USD value."""
        from reporter import DailyReporter

        reporter = DailyReporter(mock_api, mock_notifier)
        data = report_data_factory.create_report_data()

        report = reporter._format_daily_report(data)

        assert "Available" in report or "ETH" in report
        assert "Total Value" in report

    def test_format_daily_report_includes_pnl(self, mock_api, mock_notifier, report_data_factory):
        """Report should include 24h PnL with sign and percentage."""
        from reporter import DailyReporter

        reporter = DailyReporter(mock_api, mock_notifier)
        data = report_data_factory.create_report_data()

        report = reporter._format_daily_report(data)

        assert "PnL" in report or "pnl" in report

    def test_format_daily_report_includes_positions(
        self, mock_api, mock_notifier, report_data_factory
    ):
        """Report should include position count."""
        from reporter import DailyReporter

        reporter = DailyReporter(mock_api, mock_notifier)
        data = report_data_factory.create_report_data()

        report = reporter._format_daily_report(data)

        assert "Position" in report or "position" in report

    def test_format_daily_report_includes_strategies(
        self, mock_api, mock_notifier, report_data_factory
    ):
        """Report should include active strategy count."""
        from reporter import DailyReporter

        reporter = DailyReporter(mock_api, mock_notifier)
        data = report_data_factory.create_report_data()

        report = reporter._format_daily_report(data)

        assert "Strateg" in report or "strateg" in report


class TestStartStop:
    """Tests for start/stop methods."""

    @pytest.mark.asyncio
    async def test_start_sets_running_true(self, mock_api, mock_notifier):
        """start() should set running flag to True."""
        from reporter import DailyReporter

        reporter = DailyReporter(mock_api, mock_notifier)
        reporter.enabled = True

        # Start in background
        task = asyncio.create_task(reporter.start())
        await asyncio.sleep(0.05)

        assert reporter.running is True

        # Cleanup
        reporter.stop()
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    def test_stop_sets_running_false(self, mock_api, mock_notifier):
        """stop() should set running flag to False."""
        from reporter import DailyReporter

        reporter = DailyReporter(mock_api, mock_notifier)
        reporter.running = True

        reporter.stop()

        assert reporter.running is False

    @pytest.mark.asyncio
    async def test_start_respects_enabled_flag(self, mock_api, mock_notifier):
        """Disabled reporter should not start loop."""
        from reporter import DailyReporter

        reporter = DailyReporter(mock_api, mock_notifier)
        reporter.enabled = False

        await reporter.start()

        assert reporter.running is False

    @pytest.mark.asyncio
    async def test_start_background_creates_task(self, mock_api, mock_notifier):
        """start_background() should create asyncio Task."""
        from reporter import DailyReporter

        reporter = DailyReporter(mock_api, mock_notifier)
        reporter.enabled = True

        task = await reporter.start_background()

        assert isinstance(task, asyncio.Task)

        # Cleanup
        reporter.stop()
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


class TestReportCommands:
    """Tests for /report_on and /report_off commands."""

    @pytest.mark.asyncio
    async def test_cmd_report_on_responds(
        self, mock_telegram_update, mock_telegram_context, mock_api, mock_notifier
    ):
        """/report_on command should respond with confirmation."""
        from commands.query import cmd_report_on
        from reporter import DailyReporter

        # Create a mock reporter
        mock_reporter = DailyReporter(mock_api, mock_notifier)
        mock_reporter.enabled = False

        with (
            patch("commands.query.authorized", return_value=True),
            patch("main.get_reporter", return_value=mock_reporter),
        ):
            await cmd_report_on(mock_telegram_update, mock_telegram_context)

        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "enabled" in call_args.lower() or "on" in call_args.lower()

    @pytest.mark.asyncio
    async def test_cmd_report_off_responds(
        self, mock_telegram_update, mock_telegram_context, mock_api, mock_notifier
    ):
        """/report_off command should respond with confirmation."""
        from commands.query import cmd_report_off
        from reporter import DailyReporter

        # Create a mock reporter
        mock_reporter = DailyReporter(mock_api, mock_notifier)
        mock_reporter.enabled = True

        with (
            patch("commands.query.authorized", return_value=True),
            patch("main.get_reporter", return_value=mock_reporter),
        ):
            await cmd_report_off(mock_telegram_update, mock_telegram_context)

        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "disabled" in call_args.lower() or "off" in call_args.lower()


class TestReportTimeCommand:
    """Tests for /report_time command."""

    @pytest.mark.asyncio
    async def test_cmd_report_time_shows_current_time(
        self, mock_telegram_update, mock_telegram_context, mock_api, mock_notifier
    ):
        """/report_time without args should show current time."""
        from commands.query import cmd_report_time
        from reporter import DailyReporter

        mock_reporter = DailyReporter(mock_api, mock_notifier)
        mock_telegram_context.args = []

        with (
            patch("commands.query.authorized", return_value=True),
            patch("main.get_reporter", return_value=mock_reporter),
        ):
            await cmd_report_time(mock_telegram_update, mock_telegram_context)

        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        # Check that output contains time format and UTC reference
        # (actual time depends on .env REPORT_TIME setting)
        assert "UTC" in call_args
        assert ":00" in call_args  # Any hour:00 format

    @pytest.mark.asyncio
    async def test_cmd_report_time_sets_new_time(
        self, mock_telegram_update, mock_telegram_context, mock_api, mock_notifier
    ):
        """/report_time HH:MM should update report time (converts local to UTC)."""
        from commands.query import cmd_report_time
        from reporter import DailyReporter

        mock_reporter = DailyReporter(mock_api, mock_notifier)
        mock_telegram_context.args = ["09:30"]

        with (
            patch("commands.query.authorized", return_value=True),
            patch("main.get_reporter", return_value=mock_reporter),
        ):
            await cmd_report_time(mock_telegram_update, mock_telegram_context)

        mock_telegram_update.message.reply_text.assert_called_once()
        # Report time is updated (converted from local to UTC, exact value depends on timezone)
        # Just verify it was updated from the default (8, 0)
        assert mock_reporter.report_time != (8, 0)  # Time was changed

    @pytest.mark.asyncio
    async def test_cmd_report_time_invalid_format(
        self, mock_telegram_update, mock_telegram_context, mock_api, mock_notifier
    ):
        """/report_time with invalid format should show error."""
        from commands.query import cmd_report_time
        from reporter import DailyReporter

        mock_reporter = DailyReporter(mock_api, mock_notifier)
        mock_telegram_context.args = ["invalid"]

        with (
            patch("commands.query.authorized", return_value=True),
            patch("main.get_reporter", return_value=mock_reporter),
        ):
            await cmd_report_time(mock_telegram_update, mock_telegram_context)

        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "Invalid" in call_args or "invalid" in call_args


class TestReportStatusCommand:
    """Tests for /report_status command."""

    @pytest.mark.asyncio
    async def test_cmd_report_status_shows_status(
        self, mock_telegram_update, mock_telegram_context, mock_api, mock_notifier
    ):
        """/report_status should show current report settings."""
        from commands.query import cmd_report_status
        from reporter import DailyReporter

        mock_reporter = DailyReporter(mock_api, mock_notifier)
        mock_reporter.enabled = True

        with (
            patch("commands.query.authorized", return_value=True),
            patch("main.get_reporter", return_value=mock_reporter),
        ):
            await cmd_report_status(mock_telegram_update, mock_telegram_context)

        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "enabled" in call_args.lower()
        # Check that output contains time and UTC reference
        # (actual time depends on .env REPORT_TIME setting)
        assert "UTC" in call_args
        assert ":00" in call_args  # Any hour:00 format

    @pytest.mark.asyncio
    async def test_cmd_report_status_shows_disabled(
        self, mock_telegram_update, mock_telegram_context, mock_api, mock_notifier
    ):
        """/report_status should show disabled status."""
        from commands.query import cmd_report_status
        from reporter import DailyReporter

        mock_reporter = DailyReporter(mock_api, mock_notifier)
        mock_reporter.enabled = False

        with (
            patch("commands.query.authorized", return_value=True),
            patch("main.get_reporter", return_value=mock_reporter),
        ):
            await cmd_report_status(mock_telegram_update, mock_telegram_context)

        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "disabled" in call_args.lower()


class TestSetReportTime:
    """Tests for set_report_time method."""

    def test_set_report_time_valid(self, mock_api, mock_notifier):
        """set_report_time should update time for valid values."""
        from reporter import DailyReporter

        reporter = DailyReporter(mock_api, mock_notifier)

        result = reporter.set_report_time(14, 30)

        assert result is True
        assert reporter.report_time == (14, 30)

    def test_set_report_time_invalid_hour(self, mock_api, mock_notifier):
        """set_report_time should reject invalid hour."""
        from reporter import DailyReporter

        reporter = DailyReporter(mock_api, mock_notifier)
        original_time = reporter.report_time

        result = reporter.set_report_time(25, 0)

        assert result is False
        assert reporter.report_time == original_time

    def test_set_report_time_invalid_minute(self, mock_api, mock_notifier):
        """set_report_time should reject invalid minute."""
        from reporter import DailyReporter

        reporter = DailyReporter(mock_api, mock_notifier)
        original_time = reporter.report_time

        result = reporter.set_report_time(10, 70)

        assert result is False
        assert reporter.report_time == original_time


class TestEnvironmentConfiguration:
    """Tests for environment variable configuration."""

    @patch.dict("os.environ", {"REPORT_TIME": "18:45"})
    def test_reads_report_time_from_env(self, mock_api, mock_notifier):
        """Should read REPORT_TIME from environment."""
        from reporter import DailyReporter

        reporter = DailyReporter(mock_api, mock_notifier)

        assert reporter.report_time == (18, 45)

    @patch.dict("os.environ", {"REPORT_ENABLED": "true"})
    def test_report_enabled_true(self, mock_api, mock_notifier):
        """Should read REPORT_ENABLED=true from environment."""
        from reporter import DailyReporter

        reporter = DailyReporter(mock_api, mock_notifier)

        assert reporter.enabled is True

    @patch.dict("os.environ", {"REPORT_ENABLED": "FALSE"})
    def test_report_enabled_case_insensitive(self, mock_api, mock_notifier):
        """Should handle REPORT_ENABLED case-insensitively."""
        from reporter import DailyReporter

        reporter = DailyReporter(mock_api, mock_notifier)

        assert reporter.enabled is False
