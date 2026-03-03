"""
Daily Report Module for Story 7-1

Implements scheduled daily Vault status reports.
"""

import asyncio
import logging
import os
from datetime import UTC, datetime, timedelta
from typing import Any

from api import TerminalAPI
from notifier import TelegramNotifier, format_eth, format_usd

logger = logging.getLogger(__name__)


class DailyReporter:
    """Generates and sends daily Vault status reports.

    Fetches Vault data at scheduled times and pushes formatted
    reports to configured Telegram users.

    Args:
        api: TerminalAPI instance for data fetching
        notifier: TelegramNotifier instance for sending messages
    """

    def __init__(self, api: TerminalAPI, notifier: TelegramNotifier):
        """Initialize the daily reporter.

        Args:
            api: TerminalAPI instance
            notifier: TelegramNotifier instance
        """
        self.api = api
        self.notifier = notifier
        self.report_time = self._parse_report_time()
        self.running = False
        self._task: asyncio.Task | None = None
        self.enabled = os.getenv('REPORT_ENABLED', 'true').lower() == 'true'

    def _parse_report_time(self) -> tuple[int, int]:
        """Parse REPORT_TIME env variable (HH:MM format).

        Returns:
            Tuple of (hour, minute)
        """
        time_str = os.getenv('REPORT_TIME', '08:00')
        try:
            parts = time_str.split(':')
            if len(parts) != 2:
                raise ValueError("Invalid format")
            hour, minute = int(parts[0]), int(parts[1])
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError("Hour must be 0-23, minute must be 0-59")
            return hour, minute
        except (ValueError, IndexError):
            logger.warning(f"Invalid REPORT_TIME '{time_str}', using 08:00")
            return 8, 0

    def _calculate_next_run(self) -> float:
        """Calculate seconds until next scheduled report.

        Returns:
            Seconds until next scheduled report time
        """
        now = datetime.now(UTC)
        target = now.replace(
            hour=self.report_time[0],
            minute=self.report_time[1],
            second=0,
            microsecond=0
        )
        if target <= now:
            target += timedelta(days=1)
        return (target - now).total_seconds()

    async def _gather_report_data(self) -> dict[str, Any]:
        """Fetch all data needed for daily report.

        Returns:
            Dictionary containing balance, pnl, positions, and strategies data
        """
        data = {}

        # Get positions (includes balance info)
        positions = await self.api.get_positions()
        if isinstance(positions, dict) and "error" in positions:
            logger.warning(f"Failed to get positions: {positions.get('error')}")
        else:
            data['positions'] = positions

        # Get strategies
        strategies = await self.api.get_strategies()
        if isinstance(strategies, dict) and "error" in strategies:
            logger.warning(f"Failed to get strategies: {strategies.get('error')}")
        elif isinstance(strategies, list):
            data['strategies'] = strategies
        else:
            data['strategies'] = strategies

        return data

    def _format_daily_report(self, data: dict[str, Any]) -> str:
        """Format daily report message.

        Args:
            data: Dictionary containing report data

        Returns:
            Formatted report string
        """
        today = datetime.now().strftime('%Y-%m-%d')  # Local time
        lines = [f"Daily Report - {today}\n"]

        # Balance section (from positions data)
        positions_data = data.get('positions', {})
        eth_balance = positions_data.get('ethBalance', '0')
        usd_value = positions_data.get('overallValueUsd', '0')
        lines.append(f"Available: {format_eth(eth_balance)} ETH")
        lines.append(f"Total Value: {format_usd(usd_value)}")

        # PnL section (from positions data)
        pnl_usd = positions_data.get('overallPnlUsd', '0')
        pnl_pct = positions_data.get('overallPnlPercent', '0')
        try:
            pnl_num = float(pnl_usd)
            sign = '+' if pnl_num >= 0 else ''
        except (ValueError, TypeError):
            sign = ''
        lines.append(f"24h PnL: {sign}{format_usd(pnl_usd)} ({sign}{pnl_pct}%)")

        # Positions section
        pos_items = positions_data.get('positions', [])
        lines.append(f"Positions: {len(pos_items)}")

        # Strategies section
        strategies = data.get('strategies', [])
        if isinstance(strategies, dict):
            strat_items = strategies.get('strategies', strategies.get('items', []))
        else:
            strat_items = strategies
        active_count = sum(1 for s in strat_items if s.get('active', True))
        lines.append(f"Active Strategies: {active_count}")

        return '\n'.join(lines)

    async def _send_daily_report(self):
        """Gather data and send report to all notify users."""
        if not self.notifier.notify_users:
            logger.warning("No notify users configured, skipping daily report")
            return

        data = await self._gather_report_data()
        message = self._format_daily_report(data)

        # Use notifier to send
        for user_id in self.notifier.notify_users:
            try:
                await self.notifier.bot.send_message(chat_id=user_id, text=message)
                logger.info(f"Daily report sent to user {user_id}")
            except Exception as e:
                logger.error(f"Failed to send report to user {user_id}: {e}")

    async def start(self):
        """Start the daily report scheduler.

        This method runs continuously until stop() is called.
        """
        if not self.enabled:
            logger.info("Daily reporter disabled via REPORT_ENABLED")
            return

        self.running = True
        logger.info(f"Daily reporter started (scheduled for {self.report_time[0]:02d}:{self.report_time[1]:02d} UTC)")

        while self.running:
            # Calculate time until next run
            wait_seconds = self._calculate_next_run()
            logger.info(f"Next daily report in {wait_seconds/3600:.1f} hours")

            # Wait until scheduled time
            await asyncio.sleep(wait_seconds)

            if not self.running:
                break

            # Send report
            try:
                await self._send_daily_report()
            except Exception as e:
                logger.error(f"Failed to send daily report: {e}")

        logger.info("Daily reporter stopped")

    def stop(self):
        """Stop the daily report scheduler."""
        self.running = False
        logger.info("Daily reporter stop requested")

    async def start_background(self) -> asyncio.Task:
        """Start reporter in background task.

        Returns:
            The asyncio Task running the reporter
        """
        self._task = asyncio.create_task(self.start())
        return self._task

    def set_report_time(self, hour: int, minute: int) -> bool:
        """Update report time dynamically.

        Args:
            hour: Hour (0-23)
            minute: Minute (0-59)

        Returns:
            True if updated, False if invalid
        """
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            logger.warning(f"Invalid report time: {hour:02d}:{minute:02d}")
            return False
        self.report_time = (hour, minute)
        logger.info(f"Report time updated to {hour:02d}:{minute:02d} UTC")
        return True
