"""
Integration tests for monitor commands module (AC 5, AC 10)

Tests for: commands/monitor.py command handlers

RED PHASE: These tests will FAIL until commands/monitor.py is created.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# =============================================================================
# Tests for cmd_monitor_status (AC 5, AC 10)
# =============================================================================


class TestCmdMonitorStatusRefactored:
    """Tests for /monitor_status command after refactoring."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_monitor_status_shows_running_state(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /monitor_status shows running state (AC 5)."""
        # Given
        from commands.monitor import cmd_monitor_status, set_monitor_instance

        mock_monitor = MagicMock()
        mock_monitor.running = True
        mock_monitor.poll_interval = 30
        mock_monitor.seen_ids = set()
        set_monitor_instance(mock_monitor)

        with patch("commands.monitor.is_admin", return_value=True):
            # When
            await cmd_monitor_status(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "Running" in call_args

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_monitor_status_shows_stopped_state(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /monitor_status shows stopped state (AC 5)."""
        # Given
        from commands.monitor import cmd_monitor_status, set_monitor_instance

        mock_monitor = MagicMock()
        mock_monitor.running = False
        mock_monitor.poll_interval = 30
        mock_monitor.seen_ids = set()
        set_monitor_instance(mock_monitor)

        with patch("commands.monitor.is_admin", return_value=True):
            # When
            await cmd_monitor_status(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "Stopped" in call_args

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_monitor_status_not_initialized(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /monitor_status when _monitor_instance is None (AC 10)."""
        # Given
        from commands.monitor import cmd_monitor_status, set_monitor_instance

        set_monitor_instance(None)

        with patch("commands.monitor.is_admin", return_value=True):
            # When
            await cmd_monitor_status(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "未初始化" in call_args or "not initialized" in call_args.lower()


# =============================================================================
# Tests for cmd_monitor_start (AC 5)
# =============================================================================


class TestCmdMonitorStartRefactored:
    """Tests for /monitor_start command after refactoring."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_monitor_start_starts_monitor(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /monitor_start starts the monitor (AC 5)."""
        # Given
        from commands.monitor import cmd_monitor_start, set_monitor_instance

        mock_monitor = MagicMock()
        mock_monitor.running = False  # Not already running
        mock_monitor.poll_interval = 30
        mock_monitor.start_background = AsyncMock()
        set_monitor_instance(mock_monitor)

        with patch("commands.monitor.is_admin", return_value=True):
            # When
            await cmd_monitor_start(mock_telegram_update, mock_telegram_context)

        # Then
        mock_monitor.start_background.assert_called_once()
        mock_telegram_update.message.reply_text.assert_called_once()

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_monitor_start_non_admin_rejected(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /monitor_start rejects non-admin users."""
        # Given
        from commands.monitor import cmd_monitor_start

        with patch("commands.monitor.is_admin", return_value=False):
            # When
            await cmd_monitor_start(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "Unauthorized" in call_args or "unauthorized" in call_args.lower()


# =============================================================================
# Tests for cmd_monitor_stop (AC 5)
# =============================================================================


class TestCmdMonitorStopRefactored:
    """Tests for /monitor_stop command after refactoring."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_monitor_stop_stops_monitor(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /monitor_stop stops the monitor (AC 5)."""
        # Given
        from commands.monitor import cmd_monitor_stop, set_monitor_instance

        mock_monitor = MagicMock()
        mock_monitor.running = True  # Currently running
        mock_monitor.stop = MagicMock()
        set_monitor_instance(mock_monitor)

        with patch("commands.monitor.is_admin", return_value=True):
            # When
            await cmd_monitor_stop(mock_telegram_update, mock_telegram_context)

        # Then
        mock_monitor.stop.assert_called_once()
        mock_telegram_update.message.reply_text.assert_called_once()

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_monitor_stop_non_admin_rejected(
        self,
        mock_telegram_update: MagicMock,
        mock_telegram_context: MagicMock,
    ) -> None:
        """Test /monitor_stop rejects non-admin users."""
        # Given
        from commands.monitor import cmd_monitor_stop

        with patch("commands.monitor.is_admin", return_value=False):
            # When
            await cmd_monitor_stop(mock_telegram_update, mock_telegram_context)

        # Then
        mock_telegram_update.message.reply_text.assert_called_once()
        call_args = mock_telegram_update.message.reply_text.call_args[0][0]
        assert "Unauthorized" in call_args or "unauthorized" in call_args.lower()


# =============================================================================
# Tests for set_monitor_instance (Dependency Injection)
# =============================================================================


class TestSetMonitorInstance:
    """Tests for set_monitor_instance dependency injection."""

    @pytest.mark.integration
    def test_set_monitor_instance_sets_global(self) -> None:
        """Test set_monitor_instance correctly sets global variable."""
        # Given
        from commands.monitor import set_monitor_instance

        mock_monitor = MagicMock()

        # When
        set_monitor_instance(mock_monitor)

        # Then - verify it was set (need to re-import to check)
        import commands.monitor as monitor_module

        assert monitor_module._monitor_instance is mock_monitor

    @pytest.mark.integration
    def test_set_monitor_instance_can_be_none(self) -> None:
        """Test set_monitor_instance can be called with None."""
        # Given
        from commands.monitor import set_monitor_instance

        # When
        set_monitor_instance(None)

        # Then - should not raise
        import commands.monitor as monitor_module

        assert monitor_module._monitor_instance is None
