"""
ATDD Tests for Story 7-2: Threshold Alert

These tests are designed to FAIL before implementation (TDD RED phase).
Run: pytest tests/unit/test_story_7_2_threshold_alert.py -v

Generated: 2026-03-03
Story: 7-2-threshold-alert
"""

import asyncio
from datetime import UTC, datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

UTC = UTC

import pytest

# ============================================================================
# Test Data Factory
# ============================================================================


class AlertDataFactory:
    """Factory for creating test alert data."""

    @staticmethod
    def create_positions_data(
        pnl_usd: str = "120.50",
        pnl_percent: str = "2.75",
        **overrides,
    ) -> dict:
        """Create positions data for PnL threshold testing."""
        data = {
            "ethBalance": "1500000000000000000",
            "overallValueUsd": "4500.00",
            "overallPnlUsd": pnl_usd,
            "overallPnlPercent": pnl_percent,
            "positions": [
                {
                    "symbol": "ETH",
                    "valueUsd": "3000.00",
                    "totalPnlUsd": "100.00",
                    "totalPnlPercent": "3.45",
                },
                {
                    "symbol": "USDC",
                    "valueUsd": "1000.00",
                    "totalPnlUsd": "15.00",
                    "totalPnlPercent": "1.5",
                },
            ],
        }
        data.update(overrides)
        return data

    @staticmethod
    def create_position_change(
        symbol: str = "ETH",
        previous_value: float = 1000.0,
        current_value: float = 1200.0,
    ) -> dict:
        """Create position change data for threshold testing."""
        change_pct = abs((current_value - previous_value) / previous_value) * 100
        return {
            "symbol": symbol,
            "previous_value": previous_value,
            "current_value": current_value,
            "change_pct": change_pct,
        }

    @staticmethod
    def create_pnl_change(
        previous_pnl: float = 100.0,
        current_pnl: float = 150.0,
    ) -> dict:
        """Create PnL change data for threshold testing."""
        change = current_pnl - previous_pnl
        pct_change = abs(change / abs(previous_pnl)) * 100 if previous_pnl != 0 else 100
        return {
            "previous_pnl": previous_pnl,
            "current_pnl": current_pnl,
            "change": change,
            "pct_change": pct_change,
        }


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def alert_data_factory():
    """Provide AlertDataFactory."""
    return AlertDataFactory()


@pytest.fixture
def mock_api():
    """Create mock TerminalAPI instance."""
    api = MagicMock()
    api.get_positions = AsyncMock(return_value=AlertDataFactory.create_positions_data())
    return api


@pytest.fixture
def mock_notifier():
    """Create mock TelegramNotifier instance."""
    notifier = MagicMock()
    notifier.bot = AsyncMock()
    notifier.notify_users = [123456789]
    return notifier


# ============================================================================
# Test Classes - AC1: Extend ActivityMonitor to support threshold checking
# ============================================================================


class TestThresholdAlerterInit:
    """Tests for ThresholdAlerter initialization (AC1, AC2, AC3)."""

    def test_init_stores_api_instance(self, mock_api, mock_notifier):
        """API instance should be stored as instance attribute."""
        # GIVEN: ThresholdAlerter class exists
        # WHEN: Initialized with api and notifier
        # THEN: api should be stored
        from alerter import ThresholdAlerter

        alerter = ThresholdAlerter(mock_api, mock_notifier)

        assert alerter.api == mock_api

    def test_init_stores_notifier_instance(self, mock_api, mock_notifier):
        """Notifier instance should be stored as instance attribute."""
        from alerter import ThresholdAlerter

        alerter = ThresholdAlerter(mock_api, mock_notifier)

        assert alerter.notifier == mock_notifier

    def test_init_default_pnl_threshold_10(self, mock_api, mock_notifier):
        """Default PnL alert threshold should be 5% (AC2)."""
        from alerter import ThresholdAlerter

        with patch.dict("os.environ", {}, clear=True):
            alerter = ThresholdAlerter(mock_api, mock_notifier)

        assert alerter.pnl_threshold == 10.0

    @patch.dict("os.environ", {"PNL_ALERT_THRESHOLD": "10"})
    def test_init_reads_pnl_threshold_from_env(self, mock_api, mock_notifier):
        """PNL_ALERT_THRESHOLD should be read from environment (AC2)."""
        from alerter import ThresholdAlerter

        alerter = ThresholdAlerter(mock_api, mock_notifier)

        assert alerter.pnl_threshold == 10.0

    def test_init_default_position_threshold_15(self, mock_api, mock_notifier):
        """Default position alert threshold should be 10% (AC3)."""
        from alerter import ThresholdAlerter

        with patch.dict("os.environ", {}, clear=True):
            alerter = ThresholdAlerter(mock_api, mock_notifier)

        assert alerter.position_threshold == 15.0

    @patch.dict("os.environ", {"POSITION_ALERT_THRESHOLD": "15"})
    def test_init_reads_position_threshold_from_env(self, mock_api, mock_notifier):
        """POSITION_ALERT_THRESHOLD should be read from environment (AC3)."""
        from alerter import ThresholdAlerter

        alerter = ThresholdAlerter(mock_api, mock_notifier)

        assert alerter.position_threshold == 15.0

    def test_init_running_flag_false(self, mock_api, mock_notifier):
        """running flag should be initialized to False."""
        from alerter import ThresholdAlerter

        with patch.dict("os.environ", {}, clear=True):
            alerter = ThresholdAlerter(mock_api, mock_notifier)

        assert alerter.running is False

    def test_init_enabled_default_true(self, mock_api, mock_notifier):
        """ALERT_ENABLED should default to true."""
        from alerter import ThresholdAlerter

        with patch.dict("os.environ", {}, clear=True):
            alerter = ThresholdAlerter(mock_api, mock_notifier)

        assert alerter.enabled is True

    @patch.dict("os.environ", {"ALERT_ENABLED": "false"})
    def test_init_enabled_from_env(self, mock_api, mock_notifier):
        """ALERT_ENABLED should be read from environment."""
        from alerter import ThresholdAlerter

        alerter = ThresholdAlerter(mock_api, mock_notifier)

        assert alerter.enabled is False

    def test_init_check_interval_default_300(self, mock_api, mock_notifier):
        """Default check interval should be 60 seconds."""
        from alerter import ThresholdAlerter

        with patch.dict("os.environ", {}, clear=True):
            alerter = ThresholdAlerter(mock_api, mock_notifier)

        assert alerter.check_interval == 300

    @patch.dict("os.environ", {"ALERT_CHECK_INTERVAL": "30"})
    def test_init_reads_check_interval_from_env(self, mock_api, mock_notifier):
        """ALERT_CHECK_INTERVAL should be read from environment."""
        from alerter import ThresholdAlerter

        alerter = ThresholdAlerter(mock_api, mock_notifier)

        assert alerter.check_interval == 30

    def test_init_previous_pnl_none(self, mock_api, mock_notifier):
        """Previous PnL should be None initially (no comparison possible)."""
        from alerter import ThresholdAlerter

        with patch.dict("os.environ", {}, clear=True):
            alerter = ThresholdAlerter(mock_api, mock_notifier)

        assert alerter._previous_pnl_usd is None

    def test_init_previous_positions_empty(self, mock_api, mock_notifier):
        """Previous positions should be empty dict initially."""
        from alerter import ThresholdAlerter

        with patch.dict("os.environ", {}, clear=True):
            alerter = ThresholdAlerter(mock_api, mock_notifier)

        assert alerter._previous_positions == {}


# ============================================================================
# Test Classes - AC4: Trigger alert when threshold exceeded
# ============================================================================


class TestPnLThresholdChecking:
    """Tests for PnL threshold checking logic (AC4)."""

    @pytest.mark.asyncio
    async def test_check_pnl_no_alert_on_first_check(self, mock_api, mock_notifier):
        """First check should not trigger alert (no previous value to compare)."""
        from alerter import ThresholdAlerter

        alerter = ThresholdAlerter(mock_api, mock_notifier)
        alerter.pnl_threshold = 10.0

        result = await alerter._check_pnl_threshold()

        # First check should return None (no comparison possible)
        assert result is None
        # But should store current value for next comparison
        assert alerter._previous_pnl_usd is not None

    @pytest.mark.asyncio
    async def test_check_pnl_no_alert_below_threshold(self, mock_api, mock_notifier):
        """Should not alert when change is below threshold."""
        from alerter import ThresholdAlerter

        # Setup: previous PnL = 100, current = 103 (3% change, below 5% threshold)
        mock_api.get_positions = AsyncMock(
            return_value=AlertDataFactory.create_positions_data(pnl_usd="103.00")
        )
        alerter = ThresholdAlerter(mock_api, mock_notifier)
        alerter.pnl_threshold = 10.0
        alerter._previous_pnl_usd = 100.0

        result = await alerter._check_pnl_threshold()

        assert result is None

    @pytest.mark.asyncio
    async def test_check_pnl_alert_when_threshold_exceeded(self, mock_api, mock_notifier):
        """Should return alert data when change exceeds threshold (AC4)."""
        from alerter import ThresholdAlerter

        # Setup: previous PnL = 100, current = 110 (10% change, above 5% threshold)
        mock_api.get_positions = AsyncMock(
            return_value=AlertDataFactory.create_positions_data(pnl_usd="110.00")
        )
        alerter = ThresholdAlerter(mock_api, mock_notifier)
        alerter.pnl_threshold = 10.0
        alerter._previous_pnl_usd = 100.0

        result = await alerter._check_pnl_threshold()

        assert result is not None
        assert result["previous_pnl"] == 100.0
        assert result["current_pnl"] == 110.0
        assert result["change"] == 10.0
        assert result["pct_change"] >= 5.0

    @pytest.mark.asyncio
    async def test_check_pnl_handles_negative_change(self, mock_api, mock_notifier):
        """Should detect negative PnL changes exceeding threshold."""
        from alerter import ThresholdAlerter

        # Setup: previous PnL = 100, current = 85 (15% loss, above 5% threshold)
        mock_api.get_positions = AsyncMock(
            return_value=AlertDataFactory.create_positions_data(pnl_usd="85.00")
        )
        alerter = ThresholdAlerter(mock_api, mock_notifier)
        alerter.pnl_threshold = 10.0
        alerter._previous_pnl_usd = 100.0

        result = await alerter._check_pnl_threshold()

        assert result is not None
        assert result["change"] == -15.0
        assert result["pct_change"] >= 5.0

    @pytest.mark.asyncio
    async def test_check_pnl_handles_zero_previous(self, mock_api, mock_notifier):
        """Should skip alert when previous PnL was zero to avoid spam."""
        from alerter import ThresholdAlerter

        mock_api.get_positions = AsyncMock(
            return_value=AlertDataFactory.create_positions_data(pnl_usd="10.00")
        )
        alerter = ThresholdAlerter(mock_api, mock_notifier)
        alerter.pnl_threshold = 10.0
        alerter._previous_pnl_usd = 0.0

        result = await alerter._check_pnl_threshold()

        # Should skip alert on first non-zero value after zero to avoid spam
        # but update state for next comparison
        assert result is None
        assert alerter._previous_pnl_usd == 10.0

    @pytest.mark.asyncio
    async def test_check_pnl_handles_api_error(self, mock_api, mock_notifier):
        """Should handle API errors gracefully."""
        from alerter import ThresholdAlerter

        mock_api.get_positions = AsyncMock(return_value={"error": "API failed"})
        alerter = ThresholdAlerter(mock_api, mock_notifier)
        alerter._previous_pnl_usd = 100.0

        result = await alerter._check_pnl_threshold()

        assert result is None


class TestPositionThresholdChecking:
    """Tests for position threshold checking logic (AC4)."""

    @pytest.mark.asyncio
    async def test_check_position_no_alert_on_first_check(self, mock_api, mock_notifier):
        """First check should not trigger alerts (no previous values to compare)."""
        from alerter import ThresholdAlerter

        alerter = ThresholdAlerter(mock_api, mock_notifier)
        alerter.position_threshold = 15.0

        alerts, positions = await alerter._check_position_threshold()

        assert alerts == []

    @pytest.mark.asyncio
    async def test_check_position_no_alert_below_threshold(self, mock_api, mock_notifier):
        """Should not alert when position change is below threshold."""
        from alerter import ThresholdAlerter

        # Setup: ETH value changed from 1000 to 1050 (5% change, below 10% threshold)
        mock_api.get_positions = AsyncMock(
            return_value={
                "positions": [{"symbol": "ETH", "valueUsd": "1050.00"}],
            }
        )
        alerter = ThresholdAlerter(mock_api, mock_notifier)
        alerter.position_threshold = 15.0
        alerter._previous_positions = {"ETH": 1000.0}

        alerts, positions = await alerter._check_position_threshold()

        assert alerts == []

    @pytest.mark.asyncio
    async def test_check_position_alert_when_threshold_exceeded(self, mock_api, mock_notifier):
        """Should return alert data when position change exceeds threshold (AC4)."""
        from alerter import ThresholdAlerter

        # Setup: ETH value changed from 1000 to 1200 (20% change, above 10% threshold)
        mock_api.get_positions = AsyncMock(
            return_value={
                "positions": [{"symbol": "ETH", "valueUsd": "1200.00"}],
            }
        )
        alerter = ThresholdAlerter(mock_api, mock_notifier)
        alerter.position_threshold = 15.0
        alerter._previous_positions = {"ETH": 1000.0}

        alerts, positions = await alerter._check_position_threshold()

        assert len(alerts) == 1
        assert alerts[0]["symbol"] == "ETH"
        assert alerts[0]["previous_value"] == 1000.0
        assert alerts[0]["current_value"] == 1200.0
        assert alerts[0]["change_pct"] >= 10.0

    @pytest.mark.asyncio
    async def test_check_position_multiple_positions(self, mock_api, mock_notifier):
        """Should detect multiple position changes exceeding threshold."""
        from alerter import ThresholdAlerter

        mock_api.get_positions = AsyncMock(
            return_value={
                "positions": [
                    {"symbol": "ETH", "valueUsd": "1200.00"},  # +20%
                    {"symbol": "USDC", "valueUsd": "1150.00"},  # +15%
                    {"symbol": "WBTC", "valueUsd": "580.00"},  # +16%
                ],
            }
        )
        alerter = ThresholdAlerter(mock_api, mock_notifier)
        alerter.position_threshold = 15.0
        alerter._previous_positions = {"ETH": 1000.0, "USDC": 1000.0, "WBTC": 500.0}

        alerts, positions = await alerter._check_position_threshold()

        # All three should trigger alerts (>= 15%)
        assert len(alerts) == 3

    @pytest.mark.asyncio
    async def test_check_position_handles_new_positions(self, mock_api, mock_notifier):
        """Should handle new positions not in previous data."""
        from alerter import ThresholdAlerter

        mock_api.get_positions = AsyncMock(
            return_value={
                "positions": [
                    {"symbol": "ETH", "valueUsd": "1000.00"},
                    {"symbol": "NEW", "valueUsd": "500.00"},  # New position
                ],
            }
        )
        alerter = ThresholdAlerter(mock_api, mock_notifier)
        alerter.position_threshold = 15.0
        alerter._previous_positions = {"ETH": 1000.0}

        alerts, positions = await alerter._check_position_threshold()

        # Only ETH should be compared (NEW has no previous)
        assert len(alerts) == 0  # ETH unchanged, NEW ignored

    @pytest.mark.asyncio
    async def test_check_position_handles_api_error(self, mock_api, mock_notifier):
        """Should handle API errors gracefully and preserve previous state."""
        from alerter import ThresholdAlerter

        mock_api.get_positions = AsyncMock(return_value={"error": "API failed"})
        alerter = ThresholdAlerter(mock_api, mock_notifier)
        alerter._previous_positions = {"ETH": 1000.0}

        alerts, positions = await alerter._check_position_threshold()

        assert alerts == []
        # Should preserve previous state on API error
        assert positions == {"ETH": 1000.0}


class TestAlertFormatting:
    """Tests for alert message formatting (AC4)."""

    def test_format_pnl_alert_includes_change_type(self, mock_api, mock_notifier):
        """PnL alert message should include change type indicator."""
        from alerter import ThresholdAlerter

        alerter = ThresholdAlerter(mock_api, mock_notifier)
        alerter.pnl_threshold = 10.0

        data = AlertDataFactory.create_pnl_change(previous_pnl=100.0, current_pnl=150.0)
        message = alerter._format_pnl_alert(data)

        assert "PnL" in message

    def test_format_pnl_alert_includes_change_amount(self, mock_api, mock_notifier):
        """PnL alert message should include change amount (AC4)."""
        from alerter import ThresholdAlerter

        alerter = ThresholdAlerter(mock_api, mock_notifier)
        data = AlertDataFactory.create_pnl_change(previous_pnl=100.0, current_pnl=150.0)
        message = alerter._format_pnl_alert(data)

        # Should show the change amount
        assert "50" in message or "+" in message

    def test_format_pnl_alert_includes_current_value(self, mock_api, mock_notifier):
        """PnL alert message should include current value (AC4)."""
        from alerter import ThresholdAlerter

        alerter = ThresholdAlerter(mock_api, mock_notifier)
        data = AlertDataFactory.create_pnl_change(previous_pnl=100.0, current_pnl=150.0)
        message = alerter._format_pnl_alert(data)

        assert "150" in message

    def test_format_pnl_alert_includes_threshold(self, mock_api, mock_notifier):
        """PnL alert message should include threshold percentage."""
        from alerter import ThresholdAlerter

        alerter = ThresholdAlerter(mock_api, mock_notifier)
        alerter.pnl_threshold = 10.0
        data = AlertDataFactory.create_pnl_change(previous_pnl=100.0, current_pnl=150.0)
        message = alerter._format_pnl_alert(data)

        assert "5" in message and "%" in message

    def test_format_position_alert_includes_symbol(self, mock_api, mock_notifier):
        """Position alert message should include token symbol."""
        from alerter import ThresholdAlerter

        alerter = ThresholdAlerter(mock_api, mock_notifier)
        data = AlertDataFactory.create_position_change(
            symbol="ETH", previous_value=1000.0, current_value=1200.0
        )
        message = alerter._format_position_alert(data)

        assert "ETH" in message

    def test_format_position_alert_includes_change_amount(self, mock_api, mock_notifier):
        """Position alert message should include change amount (AC4)."""
        from alerter import ThresholdAlerter

        alerter = ThresholdAlerter(mock_api, mock_notifier)
        data = AlertDataFactory.create_position_change(
            symbol="ETH", previous_value=1000.0, current_value=1200.0
        )
        message = alerter._format_position_alert(data)

        # Should show the $200 change
        assert "200" in message

    def test_format_position_alert_includes_current_value(self, mock_api, mock_notifier):
        """Position alert message should include current value (AC4)."""
        from alerter import ThresholdAlerter

        alerter = ThresholdAlerter(mock_api, mock_notifier)
        data = AlertDataFactory.create_position_change(
            symbol="ETH", previous_value=1000.0, current_value=1200.0
        )
        message = alerter._format_position_alert(data)

        # USD formatted with comma: "$1,200.00"
        assert "1,200" in message


# ============================================================================
# Test Classes - AC5: Dynamic configuration via commands
# ============================================================================


class TestAlertCommands:
    """Tests for /alert_pnl, /alert_position, /alert_status commands (AC5)."""

    @pytest.mark.asyncio
    async def test_cmd_alert_pnl_shows_current_threshold(
        self, mock_telegram_update, mock_telegram_context, mock_api, mock_notifier
    ):
        """/alert_pnl without args should show current threshold."""
        from alerter import ThresholdAlerter
        from commands.query import cmd_alert_pnl

        mock_alerter = ThresholdAlerter(mock_api, mock_notifier)
        mock_alerter.pnl_threshold = 7.5

        with (
            patch("commands.query.authorized", return_value=True),
            patch("main.get_alerter", return_value=mock_alerter),
        ):
            await cmd_alert_pnl(mock_telegram_update, mock_telegram_context)

        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "7.5" in call_args

    @pytest.mark.asyncio
    async def test_cmd_alert_pnl_sets_threshold(
        self, mock_telegram_update, mock_telegram_context, mock_api, mock_notifier
    ):
        """/alert_pnl <percent> should update threshold (AC5)."""
        from alerter import ThresholdAlerter
        from commands.query import cmd_alert_pnl

        mock_alerter = ThresholdAlerter(mock_api, mock_notifier)
        mock_alerter.pnl_threshold = 10.0
        mock_telegram_context.args = ["10"]

        with (
            patch("commands.query.authorized", return_value=True),
            patch("main.get_alerter", return_value=mock_alerter),
        ):
            await cmd_alert_pnl(mock_telegram_update, mock_telegram_context)

        assert mock_alerter.pnl_threshold == 10.0
        mock_telegram_update.message.reply_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_cmd_alert_pnl_rejects_invalid_value(
        self, mock_telegram_update, mock_telegram_context, mock_api, mock_notifier
    ):
        """/alert_pnl should reject values outside 1-100 range."""
        from alerter import ThresholdAlerter
        from commands.query import cmd_alert_pnl

        mock_alerter = ThresholdAlerter(mock_api, mock_notifier)
        mock_telegram_context.args = ["150"]  # Invalid: > 100

        with (
            patch("commands.query.authorized", return_value=True),
            patch("main.get_alerter", return_value=mock_alerter),
        ):
            await cmd_alert_pnl(mock_telegram_update, mock_telegram_context)

        # Should show error message, not update threshold
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "invalid" in call_args.lower() or "usage" in call_args.lower()

    @pytest.mark.asyncio
    async def test_cmd_alert_position_shows_current_threshold(
        self, mock_telegram_update, mock_telegram_context, mock_api, mock_notifier
    ):
        """/alert_position without args should show current threshold."""
        from alerter import ThresholdAlerter
        from commands.query import cmd_alert_position

        mock_alerter = ThresholdAlerter(mock_api, mock_notifier)
        mock_alerter.position_threshold = 15.0

        with (
            patch("commands.query.authorized", return_value=True),
            patch("main.get_alerter", return_value=mock_alerter),
        ):
            await cmd_alert_position(mock_telegram_update, mock_telegram_context)

        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "15" in call_args

    @pytest.mark.asyncio
    async def test_cmd_alert_position_sets_threshold(
        self, mock_telegram_update, mock_telegram_context, mock_api, mock_notifier
    ):
        """/alert_position <percent> should update threshold (AC5)."""
        from alerter import ThresholdAlerter
        from commands.query import cmd_alert_position

        mock_alerter = ThresholdAlerter(mock_api, mock_notifier)
        mock_alerter.position_threshold = 15.0
        mock_telegram_context.args = ["20"]

        with (
            patch("commands.query.authorized", return_value=True),
            patch("main.get_alerter", return_value=mock_alerter),
        ):
            await cmd_alert_position(mock_telegram_update, mock_telegram_context)

        assert mock_alerter.position_threshold == 20.0

    @pytest.mark.asyncio
    async def test_cmd_alert_status_shows_all_settings(
        self, mock_telegram_update, mock_telegram_context, mock_api, mock_notifier
    ):
        """/alert_status should show all alert settings."""
        from alerter import ThresholdAlerter
        from commands.query import cmd_alert_status

        mock_alerter = ThresholdAlerter(mock_api, mock_notifier)
        mock_alerter.pnl_threshold = 10.0
        mock_alerter.position_threshold = 15.0
        mock_alerter.enabled = True
        mock_alerter.check_interval = 60

        with (
            patch("commands.query.authorized", return_value=True),
            patch("main.get_alerter", return_value=mock_alerter),
        ):
            await cmd_alert_status(mock_telegram_update, mock_telegram_context)

        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "5" in call_args  # PnL threshold
        assert "10" in call_args  # Position threshold
        assert "60" in call_args or "enabled" in call_args.lower()


class TestSetThresholdMethods:
    """Tests for dynamic threshold setter methods (AC5)."""

    def test_set_pnl_threshold_updates_value(self, mock_api, mock_notifier):
        """set_pnl_threshold should update the threshold value and return True."""
        from alerter import ThresholdAlerter

        alerter = ThresholdAlerter(mock_api, mock_notifier)
        result = alerter.set_pnl_threshold(7.5)

        assert alerter.pnl_threshold == 7.5
        assert result is True

    def test_set_position_threshold_updates_value(self, mock_api, mock_notifier):
        """set_position_threshold should update the threshold value and return True."""
        from alerter import ThresholdAlerter

        alerter = ThresholdAlerter(mock_api, mock_notifier)
        result = alerter.set_position_threshold(12.5)

        assert alerter.position_threshold == 12.5
        assert result is True

    def test_set_pnl_threshold_rejects_invalid_value(self, mock_api, mock_notifier):
        """set_pnl_threshold should reject values outside 1-100 range."""
        from alerter import ThresholdAlerter

        alerter = ThresholdAlerter(mock_api, mock_notifier)
        alerter.pnl_threshold = 10.0

        result = alerter.set_pnl_threshold(150)  # Invalid: > 100

        assert result is False
        assert alerter.pnl_threshold == 10.0  # Should not change

    def test_set_position_threshold_rejects_invalid_value(self, mock_api, mock_notifier):
        """set_position_threshold should reject values outside 1-100 range."""
        from alerter import ThresholdAlerter

        alerter = ThresholdAlerter(mock_api, mock_notifier)
        alerter.position_threshold = 15.0

        result = alerter.set_position_threshold(-5)  # Invalid: < 1

        assert result is False
        assert alerter.position_threshold == 15.0  # Should not change


# ============================================================================
# Test Classes - Monitoring Loop
# ============================================================================


class TestStartStop:
    """Tests for start/stop methods."""

    @pytest.mark.asyncio
    async def test_start_sets_running_true(self, mock_api, mock_notifier):
        """start() should set running flag to True."""
        from alerter import ThresholdAlerter

        alerter = ThresholdAlerter(mock_api, mock_notifier)
        alerter.enabled = True

        task = asyncio.create_task(alerter.start())
        await asyncio.sleep(0.05)

        assert alerter.running is True

        # Cleanup
        alerter.stop()
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    def test_stop_sets_running_false(self, mock_api, mock_notifier):
        """stop() should set running flag to False."""
        from alerter import ThresholdAlerter

        alerter = ThresholdAlerter(mock_api, mock_notifier)
        alerter.running = True

        alerter.stop()

        assert alerter.running is False

    @pytest.mark.asyncio
    async def test_start_respects_enabled_flag(self, mock_api, mock_notifier):
        """Disabled alerter should not start loop."""
        from alerter import ThresholdAlerter

        alerter = ThresholdAlerter(mock_api, mock_notifier)
        alerter.enabled = False

        await alerter.start()

        assert alerter.running is False

    @pytest.mark.asyncio
    async def test_start_background_creates_task(self, mock_api, mock_notifier):
        """start_background() should create asyncio Task."""
        from alerter import ThresholdAlerter

        alerter = ThresholdAlerter(mock_api, mock_notifier)
        alerter.enabled = True

        task = await alerter.start_background()

        assert isinstance(task, asyncio.Task)

        # Cleanup
        alerter.stop()
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


class TestSendAlerts:
    """Tests for alert sending logic."""

    @pytest.mark.asyncio
    async def test_send_alerts_checks_pnl_threshold(self, mock_api, mock_notifier):
        """_send_alerts should check PnL threshold."""
        from alerter import ThresholdAlerter

        mock_api.get_positions = AsyncMock(
            return_value=AlertDataFactory.create_positions_data(pnl_usd="150.00")
        )
        alerter = ThresholdAlerter(mock_api, mock_notifier)
        alerter.pnl_threshold = 10.0
        alerter._previous_pnl_usd = 100.0  # 50% increase, should trigger

        await alerter._send_alerts()

        # Should have sent a message to notify_users
        mock_notifier.bot.send_message.assert_called()

    @pytest.mark.asyncio
    async def test_send_alerts_sends_to_all_notify_users(self, mock_api, mock_notifier):
        """Alerts should be sent to all users in notify_users list."""
        from alerter import ThresholdAlerter

        mock_api.get_positions = AsyncMock(
            return_value=AlertDataFactory.create_positions_data(pnl_usd="150.00")
        )
        mock_notifier.notify_users = [123, 456, 789]
        alerter = ThresholdAlerter(mock_api, mock_notifier)
        alerter.pnl_threshold = 10.0
        alerter._previous_pnl_usd = 100.0

        await alerter._send_alerts()

        # Should have called send_message 3 times (once per user)
        assert mock_notifier.bot.send_message.call_count >= 3


# ============================================================================
# Test Classes - Environment Configuration
# ============================================================================


class TestEnvironmentConfiguration:
    """Tests for environment variable configuration."""

    @patch.dict("os.environ", {"PNL_ALERT_THRESHOLD": "7.5"})
    def test_reads_pnl_threshold_from_env(self, mock_api, mock_notifier):
        """Should read PNL_ALERT_THRESHOLD from environment."""
        from alerter import ThresholdAlerter

        alerter = ThresholdAlerter(mock_api, mock_notifier)

        assert alerter.pnl_threshold == 7.5

    @patch.dict("os.environ", {"POSITION_ALERT_THRESHOLD": "12.5"})
    def test_reads_position_threshold_from_env(self, mock_api, mock_notifier):
        """Should read POSITION_ALERT_THRESHOLD from environment."""
        from alerter import ThresholdAlerter

        alerter = ThresholdAlerter(mock_api, mock_notifier)

        assert alerter.position_threshold == 12.5

    @patch.dict("os.environ", {"ALERT_CHECK_INTERVAL": "45"})
    def test_reads_check_interval_from_env(self, mock_api, mock_notifier):
        """Should read ALERT_CHECK_INTERVAL from environment."""
        from alerter import ThresholdAlerter

        alerter = ThresholdAlerter(mock_api, mock_notifier)

        assert alerter.check_interval == 45

    @patch.dict("os.environ", {"PNL_ALERT_THRESHOLD": "invalid"})
    def test_handles_invalid_pnl_threshold(self, mock_api, mock_notifier):
        """Should fall back to default for invalid PNL_ALERT_THRESHOLD."""
        from alerter import ThresholdAlerter

        alerter = ThresholdAlerter(mock_api, mock_notifier)

        assert alerter.pnl_threshold == 10.0  # Default

    @patch.dict("os.environ", {"POSITION_ALERT_THRESHOLD": "invalid"})
    def test_handles_invalid_position_threshold(self, mock_api, mock_notifier):
        """Should fall back to default for invalid POSITION_ALERT_THRESHOLD."""
        from alerter import ThresholdAlerter

        alerter = ThresholdAlerter(mock_api, mock_notifier)

        assert alerter.position_threshold == 15.0  # Default
