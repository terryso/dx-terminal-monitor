"""
Threshold Alert Module for Story 7-2

Implements threshold-based alerts for PnL and position changes.
"""

import asyncio
import datetime
import logging
import os
from datetime import UTC as datetime_utc
from typing import Any

from api import TerminalAPI
from notifier import TelegramNotifier, format_usd

logger = logging.getLogger(__name__)



class ThresholdAlerter:
    """Monitors PnL and position changes and sends alerts when thresholds exceeded.

    Args:
        api: TerminalAPI instance for data fetching
        notifier: TelegramNotifier instance for sending alerts
    """

    def __init__(self, api: TerminalAPI, notifier: TelegramNotifier):
        """Initialize the threshold alerter.

        Args:
            api: TerminalAPI instance
            notifier: TelegramNotifier instance
        """
        self.api = api
        self.notifier = notifier
        self.pnl_threshold = self._get_pnl_threshold()
        self.position_threshold = self._get_position_threshold()
        self.check_interval = self._get_check_interval()
        self.running = False
        self._task: asyncio.Task | None = None
        self.enabled = os.getenv('ALERT_ENABLED', 'true').lower() == 'true'

        # Previous values for comparison
        self._previous_pnl_usd: float | None = None
        self._previous_positions: dict[str, float] = {}
        # Cooldown tracking to prevent repeated alerts
        self._last_pnl_alert_time: datetime | None = None
        self._pnl_cooldown_minutes = self._get_pnl_cooldown_minutes()

    def _get_pnl_cooldown_minutes(self) -> int:
        """Get PnL alert cooldown from env (default 5 minutes)."""
        try:
            return max(int(os.getenv('PNL_ALERT_COOLDOWN_MINUTES', '5')), 1)
        except ValueError:
            return 5

    def _get_pnl_threshold(self) -> float:
        """Get PnL alert threshold from env (default 5%)."""
        try:
            return float(os.getenv('PNL_ALERT_THRESHOLD', '5'))
        except ValueError:
            return 5.0

    def _get_position_threshold(self) -> float:
        """Get position alert threshold from env (default 10%)."""
        try:
            return float(os.getenv('POSITION_ALERT_THRESHOLD', '10'))
        except ValueError:
            return 10.0

    def _get_check_interval(self) -> int:
        """Get check interval from env (default 60 seconds)."""
        try:
            return max(int(os.getenv('ALERT_CHECK_INTERVAL', '60')), 30)
        except ValueError:
            return 60

    async def _check_pnl_threshold(self) -> dict[str, Any] | None:
        """Check if PnL change exceeds threshold.

        Returns:
            Alert data if threshold exceeded, None otherwise.
            Does NOT update state - caller must call _confirm_pnl_state() after successful send.
        """
        positions = await self.api.get_positions()
        if not isinstance(positions, dict) or "error" in positions:
            return None

        pnl_usd_str = positions.get('overallPnlUsd', '0')
        try:
            current_pnl = float(pnl_usd_str)
        except (ValueError, TypeError):
            return None

        if self._previous_pnl_usd is not None:
            change = current_pnl - self._previous_pnl_usd
            # Calculate percentage relative to absolute previous value
            if self._previous_pnl_usd != 0:
                pct_change = abs(change / abs(self._previous_pnl_usd)) * 100
            else:
                # Skip alert on first non-zero value after zero to avoid spam
                self._previous_pnl_usd = current_pnl
                return None

            if pct_change >= self.pnl_threshold:
                return {
                    'previous_pnl': self._previous_pnl_usd,
                    'current_pnl': current_pnl,
                    'change': change,
                    'pct_change': pct_change
                }

        # Always update previous value to prevent repeated alerts
        self._previous_pnl_usd = current_pnl
        return None

    def _confirm_pnl_state(self, current_pnl: float):
        """Confirm PnL state update after successful alert send."""
        self._previous_pnl_usd = current_pnl
        self._last_pnl_alert_time = datetime.datetime.now(datetime_utc)

    async def _check_position_threshold(self) -> tuple[list[dict[str, Any]], dict[str, float]]:
        """Check for significant position changes.

        Returns:
            Tuple of (list of position alerts, current positions dict).
            Does NOT update state - caller must call _confirm_position_state() after successful send.
        """
        positions = await self.api.get_positions()
        if not isinstance(positions, dict) or "error" in positions:
            # Return empty alerts but preserve previous state on API error
            return [], self._previous_positions.copy()

        pos_items = positions.get('positions', [])
        if not isinstance(pos_items, list):
            logger.warning("Unexpected positions format in API response")
            return [], self._previous_positions.copy()

        alerts = []
        current_positions = {}

        for pos in pos_items:
            symbol = pos.get('symbol', pos.get('tokenSymbol', 'Unknown'))
            try:
                value = float(pos.get('valueUsd', pos.get('value', '0')))
            except (ValueError, TypeError):
                continue

            current_positions[symbol] = value

            if symbol in self._previous_positions:
                prev_value = self._previous_positions[symbol]
                if prev_value > 0:
                    change_pct = abs((value - prev_value) / prev_value) * 100
                    if change_pct >= self.position_threshold:
                        alerts.append({
                            'symbol': symbol,
                            'previous_value': prev_value,
                            'current_value': value,
                            'change_pct': change_pct
                        })

        return alerts, current_positions

    def _confirm_position_state(self, current_positions: dict[str, float]):
        """Confirm position state update after successful alert send."""
        self._previous_positions = current_positions

    def _format_pnl_alert(self, data: dict[str, Any]) -> str:
        """Format PnL alert message."""
        now = datetime.datetime.now(datetime_utc).strftime('%Y-%m-%d %H:%M UTC')
        change = data['change']
        sign = '+' if change >= 0 else ''

        return f"""PnL Alert - {now}

24h PnL change exceeded threshold ({self.pnl_threshold}%)

Current PnL: {sign}{format_usd(str(data['current_pnl']))}
Change: {sign}{format_usd(str(change))} ({sign}{data['pct_change']:.1f}%)
"""

    def _format_position_alert(self, data: dict[str, Any]) -> str:
        """Format position alert message."""
        now = datetime.datetime.now(datetime_utc).strftime('%Y-%m-%d %H:%M UTC')
        change = data['current_value'] - data['previous_value']
        sign = '+' if change >= 0 else ''

        return f"""Position Alert - {now}

{data['symbol']} position change exceeded threshold ({self.position_threshold}%)

Previous: {format_usd(str(data['previous_value']))}
Current: {format_usd(str(data['current_value']))}
Change: {sign}{format_usd(str(abs(change)))} ({sign}{data['change_pct']:.1f}%)
"""

    async def _send_alerts(self):
        """Check thresholds and send alerts if needed."""
        # Check PnL threshold
        pnl_alert = await self._check_pnl_threshold()
        if pnl_alert:
            # Check cooldown - skip if we sent alert recently
            if self._last_pnl_alert_time is not None:
                time_since_alert = datetime.datetime.now(datetime_utc) - self._last_pnl_alert_time
                cooldown_delta = time_since_alert.total_seconds()
                if cooldown_delta < self._pnl_cooldown_minutes * 60:
                    logger.debug(f"PnL alert skipped due to cooldown ({cooldown_delta:.0f}s < {self._pnl_cooldown_minutes * 60}s)")
                    return

                # Not in cooldown, proceed with alert
            message = self._format_pnl_alert(pnl_alert)
            send_success = False
            for user_id in self.notifier.notify_users:
                try:
                    await self.notifier.bot.send_message(chat_id=user_id, text=message)
                    logger.info(f"PnL alert sent to user {user_id}")
                    send_success = True
                except Exception as e:
                    logger.error(f"Failed to send PnL alert: {e}")
            # Only update state if at least one send succeeded
            if send_success:
                self._confirm_pnl_state(pnl_alert['current_pnl'])

        # Check position thresholds
        position_alerts, current_positions = await self._check_position_threshold()
        for alert in position_alerts:
            message = self._format_position_alert(alert)
            for user_id in self.notifier.notify_users:
                try:
                    await self.notifier.bot.send_message(chat_id=user_id, text=message)
                    logger.info(f"Position alert sent to user {user_id}")
                except Exception as e:
                    logger.error(f"Failed to send position alert: {e}")
        # Update position state regardless - we don't want to re-alert on same positions
        self._confirm_position_state(current_positions)

    async def start(self):
        """Start the threshold monitoring loop."""
        if not self.enabled:
            logger.info("Threshold alerter disabled via ALERT_ENABLED")
            return

        self.running = True
        logger.info(f"Threshold alerter started (PnL: {self.pnl_threshold}%, Position: {self.position_threshold}%)")

        while self.running:
            try:
                await self._send_alerts()
            except Exception as e:
                logger.error(f"Alert check error: {e}")

            await asyncio.sleep(self.check_interval)

        logger.info("Threshold alerter stopped")

    def stop(self):
        """Stop the threshold monitoring loop."""
        self.running = False
        logger.info("Threshold alerter stop requested")

    async def start_background(self) -> asyncio.Task:
        """Start alerter in background task."""
        self._task = asyncio.create_task(self.start())
        return self._task

    def set_pnl_threshold(self, value: float) -> bool:
        """Update PnL threshold dynamically.

        Args:
            value: New threshold percentage (1-100)

        Returns:
            True if updated, False if invalid value
        """
        if not (1 <= value <= 100):
            logger.warning(f"Invalid PnL threshold value: {value} (must be 1-100)")
            return False
        self.pnl_threshold = value
        logger.info(f"PnL threshold updated to {value}%")
        return True

    def set_position_threshold(self, value: float) -> bool:
        """Update position threshold dynamically.

        Args:
            value: New threshold percentage (1-100)

        Returns:
            True if updated, False if invalid value
        """
        if not (1 <= value <= 100):
            logger.warning(f"Invalid position threshold value: {value} (must be 1-100)")
            return False
        self.position_threshold = value
        logger.info(f"Position threshold updated to {value}%")
        return True
