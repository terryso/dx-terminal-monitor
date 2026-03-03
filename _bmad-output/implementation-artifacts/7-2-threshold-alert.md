# Story 7.2: Threshold Alert

Status: done

## Story

As a user, I want to receive alerts when PnL or position changes exceed a configured threshold, so that I can promptly respond to significant market movements.

## Acceptance Criteria

1. Extend `ActivityMonitor` to support threshold checking
2. Configuration: `PNL_ALERT_THRESHOLD` (default 5%)
3. Configuration: `POSITION_ALERT_THRESHOLD` (default 10%)
4. Trigger alert when threshold exceeded: change type, change amount, current value
5. Support dynamic configuration via commands: `/alert_pnl <percent>`, `/alert_position <percent>`
6. Add unit tests

## Tasks / Subtasks

- [x] **Task 1: Create alerter.py module structure** (AC: #1)
  - [x] Create `alerter.py` file in project root
  - [x] Import necessary modules (asyncio, logging, os)
  - [x] Define `ThresholdAlerter` class with type annotations
  - [x] Add comprehensive docstrings

- [x] **Task 2: Implement ThresholdAlerter.__init__()** (AC: #2, #3)
  - [x] Accept `TerminalAPI` instance and `TelegramNotifier` instance
  - [x] Parse `PNL_ALERT_THRESHOLD` env variable (default 5)
  - [x] Parse `POSITION_ALERT_THRESHOLD` env variable (default 10)
  - [x] Initialize `running: bool` state flag
  - [x] Store previous PnL and position values for comparison
  - [x] Store reference to notifier for alerts

- [x] **Task 3: Implement threshold checking logic** (AC: #1, #4)
  - [x] Create `_check_pnl_threshold()` method that:
    - Fetches current PnL via API
    - Compares with previous PnL
    - Calculates percentage change
    - Returns alert data if threshold exceeded
  - [x] Create `_check_position_threshold()` method that:
    - Fetches current positions via API
    - Compares with previous positions
    - Detects significant position changes
    - Returns alert data if threshold exceeded

- [x] **Task 4: Implement alert formatting** (AC: #4)
  - [x] Create `_format_pnl_alert()` method for PnL alerts
  - [x] Create `_format_position_alert()` method for position alerts
  - [x] Follow established message formatting patterns from `notifier.py`

- [x] **Task 5: Implement monitoring loop** (AC: #1)
  - [x] Create `start()` async method with periodic checking
  - [x] Use configurable check interval (default 60 seconds)
  - [x] Implement `stop()` method
  - [x] Implement `start_background()` method

- [x] **Task 6: Add command handlers** (AC: #5)
  - [x] Create `cmd_alert_pnl` in `commands/query.py`
  - [x] Create `cmd_alert_position` in `commands/query.py`
  - [x] Create `cmd_alert_status` to show current thresholds
  - [x] Register commands in bot menu
  - [x] Update `/start` help text

- [x] **Task 7: Add environment configuration** (AC: #2, #3)
  - [x] Add `PNL_ALERT_THRESHOLD` to `config.py`
  - [x] Add `POSITION_ALERT_THRESHOLD` to `config.py`
  - [x] Add `ALERT_CHECK_INTERVAL` to `config.py` (default 60 seconds)
  - [x] Update `.env.example` with documentation

- [x] **Task 8: Add unit tests** (AC: #6)
  - [x] Create `tests/unit/test_story_7_2_threshold_alert.py`
  - [x] Test `ThresholdAlerter` initialization
  - [x] Test threshold checking logic
  - [x] Test alert formatting
  - [x] Test command handlers

## Dev Notes

### Architecture Patterns

This story extends the Epic 4/7 monitoring infrastructure:
- Reuses `TerminalAPI` for data fetching
- Reuses `TelegramNotifier` from `notifier.py` for sending alerts
- Uses similar scheduling pattern as `ActivityMonitor` and `DailyReporter`
- Follows same command handler patterns established in Epic 6

### Source Tree Components to Touch

1. `/Users/nick/CascadeProjects/dx-terminal-monitor/alerter.py` - New file
2. `/Users/nick/CascadeProjects/dx-terminal-monitor/commands/query.py` - Add alert commands
3. `/Users/nick/CascadeProjects/dx-terminal-monitor/commands/__init__.py` - Register handlers
4. `/Users/nick/CascadeProjects/dx-terminal-monitor/config.py` - Add threshold configs
5. `/Users/nick/CascadeProjects/dx-terminal-monitor/main.py` - Initialize ThresholdAlerter, register commands
6. `/Users/nick/CascadeProjects/dx-terminal-monitor/.env.example` - Add configuration docs
7. `/Users/nick/CascadeProjects/dx-terminal-monitor/tests/unit/test_story_7_2_threshold_alert.py` - New test file

### Dependencies on Epic 4 and Story 7-1

**From Story 4-1 (ActivityMonitor):**
- Similar scheduling pattern with `start()`, `stop()`, `start_background()` methods
- Uses `asyncio.sleep()` for timing
- Needs to be integrated with Bot lifecycle

**From Story 4-2 (TelegramNotifier):**
- Reuse `TelegramNotifier` class for sending alerts
- Follow `format_activity_message()` patterns for alert formatting

**From Story 7-1 (DailyReporter):**
- Similar module structure and initialization patterns
- Same configuration approach via environment variables
- Same integration with main.py post_init()

### Implementation Guide

**alerter.py - ThresholdAlerter class:**
```python
"""
Threshold Alert Module for Story 7-2

Implements threshold-based alerts for PnL and position changes.
"""

import asyncio
import logging
import os
from datetime import UTC, datetime
from typing import Any

from api import TerminalAPI
from notifier import TelegramNotifier, format_eth, format_usd

logger = logging.getLogger(__name__)


class ThresholdAlerter:
    """Monitors PnL and position changes and sends alerts when thresholds exceeded.

    Args:
        api: TerminalAPI instance for data fetching
        notifier: TelegramNotifier instance for sending alerts
    """

    def __init__(self, api: TerminalAPI, notifier: TelegramNotifier):
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
            Alert data if threshold exceeded, None otherwise
        """
        positions = await self.api.get_positions()
        if isinstance(positions, dict) and "error" in positions:
            return None

        pnl_usd_str = positions.get('overallPnlUsd', '0') if isinstance(positions, dict) else '0'
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
                pct_change = 100 if change != 0 else 0

            if pct_change >= self.pnl_threshold:
                alert_data = {
                    'previous_pnl': self._previous_pnl_usd,
                    'current_pnl': current_pnl,
                    'change': change,
                    'pct_change': pct_change
                }
                self._previous_pnl_usd = current_pnl
                return alert_data

        self._previous_pnl_usd = current_pnl
        return None

    async def _check_position_threshold(self) -> list[dict[str, Any]]:
        """Check for significant position changes.

        Returns:
            List of position alerts
        """
        positions = await self.api.get_positions()
        if isinstance(positions, dict) and "error" in positions:
            return []

        pos_items = positions.get('positions', []) if isinstance(positions, dict) else []
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

        self._previous_positions = current_positions
        return alerts

    def _format_pnl_alert(self, data: dict[str, Any]) -> str:
        """Format PnL alert message."""
        now = datetime.now(UTC).strftime('%Y-%m-%d %H:%M UTC')
        change = data['change']
        sign = '+' if change >= 0 else ''

        return f"""PnL Alert - {now}

24h PnL change exceeded threshold ({self.pnl_threshold}%)

Current PnL: {sign}{format_usd(str(data['current_pnl']))}
Change: {sign}{format_usd(str(change))} ({sign}{data['pct_change']:.1f}%)
"""

    def _format_position_alert(self, data: dict[str, Any]) -> str:
        """Format position alert message."""
        now = datetime.now(UTC).strftime('%Y-%m-%d %H:%M UTC')
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
            message = self._format_pnl_alert(pnl_alert)
            for user_id in self.notifier.notify_users:
                try:
                    await self.notifier.bot.send_message(chat_id=user_id, text=message)
                    logger.info(f"PnL alert sent to user {user_id}")
                except Exception as e:
                    logger.error(f"Failed to send PnL alert: {e}")

        # Check position thresholds
        position_alerts = await self._check_position_threshold()
        for alert in position_alerts:
            message = self._format_position_alert(alert)
            for user_id in self.notifier.notify_users:
                try:
                    await self.notifier.bot.send_message(chat_id=user_id, text=message)
                    logger.info(f"Position alert sent to user {user_id}")
                except Exception as e:
                    logger.error(f"Failed to send position alert: {e}")

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

    def set_pnl_threshold(self, value: float):
        """Update PnL threshold dynamically."""
        self.pnl_threshold = value
        logger.info(f"PnL threshold updated to {value}%")

    def set_position_threshold(self, value: float):
        """Update position threshold dynamically."""
        self.position_threshold = value
        logger.info(f"Position threshold updated to {value}%")
```

**config.py additions:**
```python
# Threshold Alert Configuration
PNL_ALERT_THRESHOLD = float(os.getenv('PNL_ALERT_THRESHOLD', '5'))
POSITION_ALERT_THRESHOLD = float(os.getenv('POSITION_ALERT_THRESHOLD', '10'))
ALERT_CHECK_INTERVAL = int(os.getenv('ALERT_CHECK_INTERVAL', '60'))
ALERT_ENABLED = os.getenv('ALERT_ENABLED', 'true').lower() == 'true'
```

**Command handlers in commands/query.py:**
```python
async def cmd_alert_pnl(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Set PnL alert threshold."""
    if not authorized(update):
        return

    if not ctx.args:
        # Show current threshold
        from main import alerter
        if alerter:
            await update.message.reply_text(
                f"Current PnL alert threshold: {alerter.pnl_threshold}%\n"
                f"Usage: /alert_pnl <percent>"
            )
        else:
            await update.message.reply_text("Alert system not initialized")
        return

    try:
        threshold = float(ctx.args[0])
        if threshold <= 0 or threshold > 100:
            raise ValueError("Must be 1-100")

        from main import alerter
        if alerter:
            alerter.set_pnl_threshold(threshold)
            await update.message.reply_text(f"PnL alert threshold set to {threshold}%")
        else:
            await update.message.reply_text("Alert system not initialized")
    except ValueError:
        await update.message.reply_text("Invalid value. Usage: /alert_pnl <percent> (1-100)")

async def cmd_alert_position(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Set position alert threshold."""
    if not authorized(update):
        return

    if not ctx.args:
        from main import alerter
        if alerter:
            await update.message.reply_text(
                f"Current position alert threshold: {alerter.position_threshold}%\n"
                f"Usage: /alert_position <percent>"
            )
        else:
            await update.message.reply_text("Alert system not initialized")
        return

    try:
        threshold = float(ctx.args[0])
        if threshold <= 0 or threshold > 100:
            raise ValueError("Must be 1-100")

        from main import alerter
        if alerter:
            alerter.set_position_threshold(threshold)
            await update.message.reply_text(f"Position alert threshold set to {threshold}%")
        else:
            await update.message.reply_text("Alert system not initialized")
    except ValueError:
        await update.message.reply_text("Invalid value. Usage: /alert_position <percent> (1-100)")

async def cmd_alert_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Show current alert settings."""
    if not authorized(update):
        return

    from main import alerter
    if alerter:
        status = "enabled" if alerter.enabled else "disabled"
        await update.message.reply_text(
            f"Alert System Status: {status}\n"
            f"PnL Threshold: {alerter.pnl_threshold}%\n"
            f"Position Threshold: {alerter.position_threshold}%\n"
            f"Check Interval: {alerter.check_interval}s"
        )
    else:
        await update.message.reply_text("Alert system not initialized")
```

### Message Format (from epics.md)

```
PnL Alert

24h PnL change exceeded threshold (5%)

Current PnL: -$250.00 (-4.2%)
Change: -$180.00 (from yesterday)
```

### Project Structure Notes

- New module `alerter.py` follows same patterns as `monitor.py` and `reporter.py`
- Commands added to existing `commands/query.py`
- Configuration integrated into `config.py`
- Test file naming: `test_story_7_2_threshold_alert.py`

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-7.2]
- [Source: _bmad-output/project-context.md#Telegram-Bot-命令结构]
- [Source: monitor.py - ActivityMonitor patterns]
- [Source: reporter.py - DailyReporter patterns]
- [Source: notifier.py - TelegramNotifier and formatting patterns]
- [Source: config.py - Environment variable patterns]

### Previous Story Intelligence (Story 7-1: Daily Report)

Key patterns established:
1. Module structure with `start()`, `stop()`, `start_background()` methods
2. Configuration via environment variables parsed in `__init__`
3. Use `TelegramNotifier` for sending messages to notify_users
4. Lazy import pattern in command handlers: `from main import alerter`
5. Register command in two places: `main.py` post_init() and `commands/__init__.py`
6. Update `/start` help text for new commands
7. Test file naming follows `test_story_X_Y_description.py` pattern
8. Handle both dict and list responses from API

### Git Intelligence (Recent Commits)

- `7869dcb` - docs: Add BMAD artifacts for Story 7-1
- `28eb7b3` - feat: Add daily report push feature (Story 7-1)
- `57cbaff` - feat: Add /tweets command for token-related tweets (Story 6-6)

Key learnings:
- DailyReporter pattern with scheduling and background tasks
- Environment variable configuration with defaults
- Integration with TelegramNotifier for message delivery
- Command handlers with threshold configuration

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List
