"""
ATDD Tests for Story 4-1: Activity Monitor Service

These tests are designed to FAIL before implementation (TDD RED phase).
Run: pytest tests/unit/test_story_4_1_monitor.py -v

Generated: 2026-03-01
Story: 4-1-activity-monitor-service
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestActivityMonitorInit:
    """Tests for ActivityMonitor initialization."""

    def test_init_stores_api_instance(self):
        """API instance should be stored as instance attribute."""
        from monitor import ActivityMonitor

        mock_api = MagicMock()
        mock_callback = AsyncMock()

        monitor = ActivityMonitor(mock_api, mock_callback)

        assert monitor.api == mock_api

    def test_init_stores_callback(self):
        """Callback function should be stored as instance attribute."""
        from monitor import ActivityMonitor

        mock_api = MagicMock()
        mock_callback = AsyncMock()

        monitor = ActivityMonitor(mock_api, mock_callback)

        assert monitor.callback == mock_callback

    def test_init_seen_ids_empty_set(self):
        """seen_ids should be initialized as empty set."""
        from monitor import ActivityMonitor

        mock_api = MagicMock()
        mock_callback = AsyncMock()

        monitor = ActivityMonitor(mock_api, mock_callback)

        assert monitor.seen_ids == set()

    def test_init_running_flag_false(self):
        """running flag should be initialized to False."""
        from monitor import ActivityMonitor

        mock_api = MagicMock()
        mock_callback = AsyncMock()

        monitor = ActivityMonitor(mock_api, mock_callback)

        assert monitor.running is False

    def test_init_default_poll_interval_30(self):
        """Default poll interval should be 30 seconds."""
        from monitor import ActivityMonitor

        mock_api = MagicMock()
        mock_callback = AsyncMock()

        with patch.dict('os.environ', {}, clear=True):
            monitor = ActivityMonitor(mock_api, mock_callback)

        assert monitor.poll_interval == 30

    @patch.dict('os.environ', {'POLL_INTERVAL': '60'})
    def test_init_reads_poll_interval_from_env(self):
        """POLL_INTERVAL should be read from environment variable."""
        from monitor import ActivityMonitor

        mock_api = MagicMock()
        mock_callback = AsyncMock()

        monitor = ActivityMonitor(mock_api, mock_callback)

        assert monitor.poll_interval == 60

    @patch.dict('os.environ', {'POLL_INTERVAL': '5'})
    def test_init_enforces_minimum_10_seconds(self):
        """Poll interval should have minimum of 10 seconds."""
        from monitor import ActivityMonitor

        mock_api = MagicMock()
        mock_callback = AsyncMock()

        monitor = ActivityMonitor(mock_api, mock_callback)

        assert monitor.poll_interval == 10


class TestFilterNew:
    """Tests for _filter_new method."""

    def test_filter_new_returns_unseen_activities(self):
        """Should return only activities with unseen IDs."""
        from monitor import ActivityMonitor

        mock_api = MagicMock()
        mock_callback = AsyncMock()
        monitor = ActivityMonitor(mock_api, mock_callback)

        activities = [
            {'id': '0xnew1', 'type': 'swap'},
            {'id': '0xnew2', 'type': 'deposit'},
        ]

        result = monitor._filter_new(activities)

        assert len(result) == 2
        assert result[0]['id'] == '0xnew1'
        assert result[1]['id'] == '0xnew2'

    def test_filter_new_excludes_seen_activities(self):
        """Should exclude activities already in seen_ids."""
        from monitor import ActivityMonitor

        mock_api = MagicMock()
        mock_callback = AsyncMock()
        monitor = ActivityMonitor(mock_api, mock_callback)
        monitor.seen_ids.add('0xseen1')

        activities = [
            {'id': '0xseen1', 'type': 'swap'},
            {'id': '0xnew1', 'type': 'deposit'},
        ]

        result = monitor._filter_new(activities)

        assert len(result) == 1
        assert result[0]['id'] == '0xnew1'

    def test_filter_new_adds_ids_to_seen_set(self):
        """Should add new activity IDs to seen_ids."""
        from monitor import ActivityMonitor

        mock_api = MagicMock()
        mock_callback = AsyncMock()
        monitor = ActivityMonitor(mock_api, mock_callback)

        activities = [
            {'id': '0xnew1', 'type': 'swap'},
            {'id': '0xnew2', 'type': 'deposit'},
        ]

        monitor._filter_new(activities)

        assert '0xnew1' in monitor.seen_ids
        assert '0xnew2' in monitor.seen_ids

    def test_filter_new_handles_missing_id(self):
        """Should handle activities without id field."""
        from monitor import ActivityMonitor

        mock_api = MagicMock()
        mock_callback = AsyncMock()
        monitor = ActivityMonitor(mock_api, mock_callback)

        activities = [
            {'type': 'swap'},  # No ID
            {'id': '0xvalid', 'type': 'deposit'},
        ]

        result = monitor._filter_new(activities)

        assert len(result) == 1
        assert result[0]['id'] == '0xvalid'

    def test_filter_new_empty_list_returns_empty(self):
        """Should return empty list for empty input."""
        from monitor import ActivityMonitor

        mock_api = MagicMock()
        mock_callback = AsyncMock()
        monitor = ActivityMonitor(mock_api, mock_callback)

        result = monitor._filter_new([])

        assert result == []

    def test_filter_new_all_seen_returns_empty(self):
        """Should return empty list when all activities seen."""
        from monitor import ActivityMonitor

        mock_api = MagicMock()
        mock_callback = AsyncMock()
        monitor = ActivityMonitor(mock_api, mock_callback)
        monitor.seen_ids.add('0xa')
        monitor.seen_ids.add('0xb')

        activities = [
            {'id': '0xa', 'type': 'swap'},
            {'id': '0xb', 'type': 'deposit'},
        ]

        result = monitor._filter_new(activities)

        assert result == []


class TestMonitorStart:
    """Tests for start method."""

    @pytest.mark.asyncio
    async def test_start_sets_running_true(self):
        """start() should set running flag to True."""
        from monitor import ActivityMonitor

        mock_api = MagicMock()
        mock_api.get_activity = AsyncMock(return_value={'activities': []})
        mock_callback = AsyncMock()

        monitor = ActivityMonitor(mock_api, mock_callback)
        monitor.poll_interval = 0.1

        task = asyncio.create_task(monitor.start())
        await asyncio.sleep(0.05)

        assert monitor.running is True

        monitor.stop()
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    @pytest.mark.asyncio
    async def test_start_polls_api(self):
        """start() should poll api.get_activity()."""
        from monitor import ActivityMonitor

        mock_api = MagicMock()
        mock_api.get_activity = AsyncMock(return_value={'activities': []})
        mock_callback = AsyncMock()

        monitor = ActivityMonitor(mock_api, mock_callback)
        monitor.poll_interval = 0.1

        task = asyncio.create_task(monitor.start())
        await asyncio.sleep(0.2)

        assert mock_api.get_activity.called

        monitor.stop()
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    @pytest.mark.asyncio
    async def test_start_filters_new_activities(self):
        """start() should filter activities through _filter_new."""
        from monitor import ActivityMonitor

        mock_api = MagicMock()
        mock_api.get_activity = AsyncMock(return_value={
            'activities': [{'id': '0xtest', 'type': 'swap'}]
        })
        mock_callback = AsyncMock()

        monitor = ActivityMonitor(mock_api, mock_callback)
        monitor.poll_interval = 0.1

        task = asyncio.create_task(monitor.start())
        await asyncio.sleep(0.2)

        assert '0xtest' in monitor.seen_ids

        monitor.stop()
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    @pytest.mark.asyncio
    async def test_start_triggers_callback_for_new(self):
        """start() should trigger callback for new activities."""
        from monitor import ActivityMonitor

        mock_api = MagicMock()
        # First call is preload (returns empty), subsequent calls return new activity
        mock_api.get_activity = AsyncMock(side_effect=[
            {'items': []},  # Preload - no existing activities
            {'items': [{'id': '0xnew', 'type': 'swap'}]}  # First poll - new activity
        ])
        mock_callback = AsyncMock()

        monitor = ActivityMonitor(mock_api, mock_callback)
        monitor.poll_interval = 0.1

        task = asyncio.create_task(monitor.start())
        await asyncio.sleep(0.2)

        mock_callback.assert_called_once()

        monitor.stop()
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    @pytest.mark.asyncio
    async def test_start_no_callback_for_seen(self):
        """start() should not trigger callback for seen activities."""
        from monitor import ActivityMonitor

        mock_api = MagicMock()
        mock_api.get_activity = AsyncMock(return_value={
            'activities': [{'id': '0xseen', 'type': 'swap'}]
        })
        mock_callback = AsyncMock()

        monitor = ActivityMonitor(mock_api, mock_callback)
        monitor.seen_ids.add('0xseen')
        monitor.poll_interval = 0.1

        task = asyncio.create_task(monitor.start())
        await asyncio.sleep(0.2)

        mock_callback.assert_not_called()

        monitor.stop()
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    @pytest.mark.asyncio
    async def test_start_handles_api_error(self):
        """start() should handle API errors gracefully."""
        from monitor import ActivityMonitor

        mock_api = MagicMock()
        mock_api.get_activity = AsyncMock(return_value={'error': 'API failed'})
        mock_callback = AsyncMock()

        monitor = ActivityMonitor(mock_api, mock_callback)
        monitor.poll_interval = 0.1

        task = asyncio.create_task(monitor.start())
        await asyncio.sleep(0.2)

        # Should not crash, running flag still True
        assert monitor.running is True

        monitor.stop()
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    @pytest.mark.asyncio
    async def test_start_handles_callback_error(self):
        """start() should handle callback errors gracefully."""
        from monitor import ActivityMonitor

        mock_api = MagicMock()
        mock_api.get_activity = AsyncMock(return_value={
            'activities': [{'id': '0xtest', 'type': 'swap'}]
        })
        mock_callback = AsyncMock(side_effect=Exception('Callback failed'))

        monitor = ActivityMonitor(mock_api, mock_callback)
        monitor.poll_interval = 0.1

        task = asyncio.create_task(monitor.start())
        await asyncio.sleep(0.2)

        # Should not crash, running flag still True
        assert monitor.running is True

        monitor.stop()
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


class TestMonitorStop:
    """Tests for stop method."""

    def test_stop_sets_running_false(self):
        """stop() should set running flag to False."""
        from monitor import ActivityMonitor

        mock_api = MagicMock()
        mock_callback = AsyncMock()

        monitor = ActivityMonitor(mock_api, mock_callback)
        monitor.running = True

        monitor.stop()

        assert monitor.running is False

    @pytest.mark.asyncio
    async def test_stop_stops_loop(self):
        """stop() should cause start() loop to exit."""
        from monitor import ActivityMonitor

        mock_api = MagicMock()
        mock_api.get_activity = AsyncMock(return_value={'activities': []})
        mock_callback = AsyncMock()

        monitor = ActivityMonitor(mock_api, mock_callback)
        monitor.poll_interval = 0.1

        task = asyncio.create_task(monitor.start())
        await asyncio.sleep(0.05)

        monitor.stop()

        try:
            await asyncio.wait_for(task, timeout=1.0)
        except TimeoutError:
            task.cancel()

        assert monitor.running is False


class TestStartBackground:
    """Tests for start_background method."""

    @pytest.mark.asyncio
    async def test_start_background_creates_task(self):
        """start_background() should create asyncio Task."""
        from monitor import ActivityMonitor

        mock_api = MagicMock()
        mock_api.get_activity = AsyncMock(return_value={'activities': []})
        mock_callback = AsyncMock()

        monitor = ActivityMonitor(mock_api, mock_callback)

        task = await monitor.start_background()

        assert isinstance(task, asyncio.Task)

        monitor.stop()
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    @pytest.mark.asyncio
    async def test_start_background_sets_running(self):
        """start_background() should set running to True."""
        from monitor import ActivityMonitor

        mock_api = MagicMock()
        mock_api.get_activity = AsyncMock(return_value={'activities': []})
        mock_callback = AsyncMock()

        monitor = ActivityMonitor(mock_api, mock_callback)

        await monitor.start_background()
        await asyncio.sleep(0.05)  # Wait for start() to set running=True

        assert monitor.running is True

        monitor.stop()


class TestEnvironmentConfiguration:
    """Tests for environment variable configuration."""

    @patch.dict('os.environ', {'POLL_INTERVAL': '120'})
    def test_reads_poll_interval_from_env(self):
        """Should read POLL_INTERVAL from environment."""
        from monitor import ActivityMonitor

        mock_api = MagicMock()
        mock_callback = AsyncMock()

        monitor = ActivityMonitor(mock_api, mock_callback)

        assert monitor.poll_interval == 120

    @patch.dict('os.environ', {'POLL_INTERVAL': '0'})
    def test_minimum_poll_interval_10(self):
        """Should enforce minimum poll interval of 10 seconds."""
        from monitor import ActivityMonitor

        mock_api = MagicMock()
        mock_callback = AsyncMock()

        monitor = ActivityMonitor(mock_api, mock_callback)

        assert monitor.poll_interval == 10

    @patch.dict('os.environ', {'POLL_INTERVAL': 'invalid'})
    def test_handles_invalid_poll_interval(self):
        """Should handle invalid POLL_INTERVAL gracefully."""
        from monitor import ActivityMonitor

        mock_api = MagicMock()
        mock_callback = AsyncMock()

        # Should not crash
        try:
            monitor = ActivityMonitor(mock_api, mock_callback)
            # Falls back to default or minimum
            assert monitor.poll_interval >= 10
        except ValueError:
            pytest.fail("Should not raise ValueError for invalid input")


class TestErrorHandling:
    """Tests for error handling scenarios."""

    @pytest.mark.asyncio
    async def test_handles_api_exception(self):
        """Should handle API exceptions without crashing."""
        from monitor import ActivityMonitor

        mock_api = MagicMock()
        mock_api.get_activity = AsyncMock(side_effect=Exception('Network error'))
        mock_callback = AsyncMock()

        monitor = ActivityMonitor(mock_api, mock_callback)
        monitor.poll_interval = 0.1

        task = asyncio.create_task(monitor.start())
        await asyncio.sleep(0.2)

        # Should still be running despite exception
        assert monitor.running is True

        monitor.stop()
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    @pytest.mark.asyncio
    async def test_handles_callback_exception(self):
        """Should handle callback exceptions without stopping."""
        from monitor import ActivityMonitor

        mock_api = MagicMock()
        mock_api.get_activity = AsyncMock(return_value={
            'activities': [{'id': '0xtest', 'type': 'swap'}]
        })
        mock_callback = AsyncMock(side_effect=RuntimeError('Callback error'))

        monitor = ActivityMonitor(mock_api, mock_callback)
        monitor.poll_interval = 0.1

        task = asyncio.create_task(monitor.start())
        await asyncio.sleep(0.2)

        # Should still be running despite callback exception
        assert monitor.running is True

        monitor.stop()
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
