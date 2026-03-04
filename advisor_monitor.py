"""
AI Strategy Advisor Monitor for Story 8-3

Periodically runs strategy analysis and pushes suggestions to users.
"""

import asyncio
import logging
import time
import uuid
from collections.abc import Callable
from datetime import datetime, timedelta

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

import config
from advisor import StrategyAdvisor, Suggestion
from advisor_history import get_view_url, mark_executed, sync_to_surge
from api import TerminalAPI
from utils.formatters import format_eth, format_usd

logger = logging.getLogger(__name__)

# Storage for pending suggestion requests
pending_requests: dict[str, dict] = {}
SUGGESTION_TTL = timedelta(minutes=config.SUGGESTION_TTL_MINUTES)


def format_suggestions_message(suggestions: list[Suggestion] | list[dict], context: dict) -> str:
    """Format suggestions into a user-friendly message.

    Args:
        suggestions: List of Suggestion objects or dicts
        context: Dict with balance, positions, strategies, pnl data

    Returns:
        Formatted message string
    """
    lines = [
        "<b>AI Strategy Analysis Suggestions</b>",
        "",
        f"Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "<b>Current Status:</b>",
        f"  Balance: {context.get('balance', 'N/A')}",
        f"  Positions: {context.get('positions', 0)} tokens",
        f"  Active Strategies: {context.get('strategies', 0)}",
        f"  Total PnL: {context.get('pnl', 'N/A')}",
        "",
        "<b>Suggestions:</b>",
    ]

    priority_labels = {0: "LOW", 1: "MEDIUM", 2: "HIGH"}

    for i, s in enumerate(suggestions, 1):
        # Handle both dict and Suggestion object
        action = s.action if hasattr(s, 'action') else s.get('action', 'add')
        content = s.content if hasattr(s, 'content') else s.get('content')
        priority = s.priority if hasattr(s, 'priority') else s.get('priority', 1)
        expiry_hours = s.expiry_hours if hasattr(s, 'expiry_hours') else s.get('expiry_hours', 0)
        reason = s.reason if hasattr(s, 'reason') else s.get('reason', '')
        strategy_id = s.strategy_id if hasattr(s, 'strategy_id') else s.get('strategy_id')

        if action == "add":
            icon = "[ADD]"
            validity = f"{expiry_hours}h" if expiry_hours else "Permanent"
            lines.extend([
                "",
                f"<b>[{i}] {icon} STRATEGY</b>",
                f'  Prompt: "{content}"',
                f"  Priority: {priority_labels.get(priority, 'MEDIUM')}",
                f"  Validity: {validity}",
                f"  Reason: {reason}",
            ])
        else:
            icon = "[DISABLE]"
            lines.extend([
                "",
                f"<b>[{i}] {icon} STRATEGY #{strategy_id}</b>",
                f"  Reason: {reason}",
            ])

    return "\n".join(lines)


def build_suggestion_keyboard(
    suggestions: list[Suggestion] | list[dict],
    request_id: str
) -> InlineKeyboardMarkup:
    """Build inline keyboard for suggestion actions.

    Args:
        suggestions: List of Suggestion objects or dicts
        request_id: Unique identifier for this suggestion batch

    Returns:
        InlineKeyboardMarkup with action buttons
    """
    buttons = []

    # Row 1: Individual execute buttons
    row = []
    for i, s in enumerate(suggestions, 1):
        # Handle both dict and Suggestion object
        action = s.action if hasattr(s, 'action') else s.get('action', 'add')
        icon = "+" if action == "add" else "-"
        row.append(InlineKeyboardButton(
            f"{icon} [{i}]",
            callback_data=f"adv:{request_id}:{i}"
        ))
    buttons.append(row)

    # Row 2: Execute All and Ignore
    buttons.append([
        InlineKeyboardButton("Execute All", callback_data=f"adv:{request_id}:all"),
        InlineKeyboardButton("Ignore", callback_data=f"adv:{request_id}:ignore"),
    ])

    return InlineKeyboardMarkup(buttons)


def _add_web_link_to_message(message: str) -> str:
    """Add web link to message if ADVISOR_HISTORY_ENABLED.

    Args:
        message: Original message text

    Returns:
        Updated message with web link if enabled, original message otherwise
    """
    if config.ADVISOR_HISTORY_ENABLED:
        sync_to_surge()
        return message + f"\n\n📎 <a href='{get_view_url()}'>查看详细分析历史</a>"
    return message


async def push_suggestions(
    chat_id: int,
    suggestions: list[Suggestion] | list[dict],
    context: dict,
    bot: Bot,
    record_id: str | None = None
) -> str:
    """Push suggestions to user with interactive buttons.

    Args:
        chat_id: Telegram chat ID to send to
        suggestions: List of Suggestion objects or dicts
        context: Context data for message formatting
        bot: Telegram Bot instance
        record_id: Optional record ID from advisor history (for execution tracking)

    Returns:
        request_id for this batch
    """
    request_id = uuid.uuid4().hex[:8]

    # Store pending request
    pending_requests[request_id] = {
        "suggestions": suggestions,
        "created_at": datetime.now(),
        "context": context,
        "executed": False,
        "record_id": record_id,  # Story 8-6: Link to analysis history
    }

    # Build message and keyboard
    message = format_suggestions_message(suggestions, context)
    keyboard = build_suggestion_keyboard(suggestions, request_id)

    # Add web link if history is enabled (Story 8-6)
    if config.ADVISOR_HISTORY_ENABLED:
        sync_to_surge()
        message += f"\n\n📎 <a href='{get_view_url()}'>查看详细分析历史</a>"

    # Send message
    await bot.send_message(
        chat_id,
        text=message,
        reply_markup=keyboard,
        parse_mode="HTML",
        disable_web_page_preview=True
    )

    logger.info(f"Pushed {len(suggestions)} suggestions (request_id={request_id})")
    return request_id


class AdvisorMonitor:
    """Periodically analyzes strategies and pushes suggestions to users.

    Args:
        advisor: StrategyAdvisor instance for analysis
        api: TerminalAPI instance for data fetching
        callback: Async function to call with suggestions
        admin_chat_id: Chat ID to send suggestions to
        interval_hours: Hours between analysis runs

    Example:
        advisor = StrategyAdvisor(llm, api)
        monitor = AdvisorMonitor(advisor, api, push_suggestions, chat_id)
        await monitor.start_background()
    """

    def __init__(
        self,
        advisor: StrategyAdvisor,
        api: TerminalAPI,
        callback: Callable,
        admin_chat_id: int,
        bot: Bot,
        interval_hours: int = 2
    ):
        self.advisor = advisor
        self.api = api
        self.callback = callback
        self.admin_chat_id = admin_chat_id
        self.bot = bot
        self.interval_seconds = interval_hours * 3600
        self.running = False
        self._task: asyncio.Task | None = None
        self.last_analysis: datetime | None = None

    async def start(self):
        """Start the periodic analysis loop."""
        self.running = True
        logger.info(f"Advisor monitor started (interval: {self.interval_seconds}s)")

        while self.running:
            # Wait for interval before first/next analysis
            await asyncio.sleep(self.interval_seconds)

            try:
                # Analyze
                suggestions = await self.advisor.analyze()
                self.last_analysis = datetime.now()

                if suggestions:
                    # Get context for message
                    context = await self._build_context()
                    # Push to callback
                    await self.callback(
                        self.admin_chat_id,
                        suggestions,
                        context,
                        self.bot,
                        record_id=self.advisor.last_record_id
                    )
                else:
                    logger.info("No actionable suggestions from AI analysis")

            except Exception as e:
                logger.error("Advisor analysis failed: %s", e)

    async def _build_context(self) -> dict:
        """Build context dict for message formatting."""
        import time

        balance = "N/A"
        pnl = "N/A"
        token_count = 0
        strategy_count = 0

        try:
            positions = await self.api.get_positions()

            # Check for valid positions response (not error dict)
            if positions and not (isinstance(positions, dict) and "error" in positions):
                # Use format_eth to convert Wei to ETH
                raw_balance = positions.get('ethBalance', 0)
                formatted = format_eth(str(raw_balance))
                balance = f"{formatted} ETH"
                logger.info("Balance: %s -> %s ETH", raw_balance, formatted)
                # Use format_usd for PnL
                raw_pnl = positions.get('overallPnlUsd', 0)
                pnl = format_usd(raw_pnl)
                # Get positions list
                token_count = len(positions.get('positions', []))
            else:
                logger.warning("Positions API returned error or empty: %s", positions)

        except Exception as e:
            logger.error("Failed to get positions: %s", e)

        try:
            strategies = await self.api.get_strategies()
            # Check for valid strategies response and filter non-expired
            current_time = int(time.time())
            if strategies and not (isinstance(strategies, dict) and "error" in strategies):
                # Count active, non-expired strategies
                active_strategies = [
                    s for s in strategies
                    if s.get('active', True) and (s.get('expiry', 0) == 0 or s.get('expiry', 0) > current_time)
                ]
                strategy_count = len(active_strategies)
        except Exception as e:
            logger.error("Failed to get strategies: %s", e)

        return {
            "balance": balance,
            "positions": token_count,
            "strategies": strategy_count,
            "pnl": pnl,
        }

    def stop(self):
        """Stop the monitor loop."""
        self.running = False
        logger.info("Advisor monitor stop requested")

    async def start_background(self) -> asyncio.Task:
        """Start monitor in background task.

        Returns:
            The asyncio.Task running the monitor
        """
        self._task = asyncio.create_task(self.start())
        return self._task


async def execute_suggestion(suggestion: Suggestion | dict) -> str:
    """Execute a single suggestion.

    Args:
        suggestion: Suggestion object or dict to execute

    Returns:
        Result message string
    """
    # Import here to avoid circular dependency
    from main import get_contract

    try:
        contract = get_contract()

        # Handle both dict and Suggestion object
        action = suggestion.action if hasattr(suggestion, 'action') else suggestion.get('action', 'add')
        content = suggestion.content if hasattr(suggestion, 'content') else suggestion.get('content')
        priority = suggestion.priority if hasattr(suggestion, 'priority') else suggestion.get('priority', 1)
        expiry_hours = suggestion.expiry_hours if hasattr(suggestion, 'expiry_hours') else suggestion.get('expiry_hours', 0)
        strategy_id = suggestion.strategy_id if hasattr(suggestion, 'strategy_id') else suggestion.get('strategy_id')

        if action == "add":
            # Convert expiry_hours to timestamp
            if expiry_hours and expiry_hours > 0:
                expiry = int(time.time()) + (expiry_hours * 3600)
            else:
                expiry = 0

            result = await contract.add_strategy(
                content=content,
                expiry=expiry,
                priority=priority
            )

            if result.get("success"):
                tx_hash = result.get("transactionHash", "")
                strategy_id = result.get("strategyId", "?")
                return f"Strategy #{strategy_id} added (TX: {tx_hash[:10]}...)"
            else:
                return f"Failed: {result.get('error', 'Unknown error')}"

        elif action == "disable":
            result = await contract.disable_strategy(strategy_id)

            if result.get("success"):
                tx_hash = result.get("transactionHash", "")
                return f"Strategy #{strategy_id} disabled (TX: {tx_hash[:10]}...)"
            else:
                return f"Failed: {result.get('error', 'Unknown error')}"

        else:
            return f"Unknown action: {action}"

    except Exception as e:
        logger.error("Failed to execute suggestion: %s", e)
        return f"Error: {str(e)}"


async def handle_advisor_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handle inline keyboard callbacks from advisor suggestions.

    Callback data format: adv:{request_id}:{choice}
    - choice = number (1, 2, etc.) for individual suggestion
    - choice = "all" to execute all suggestions
    - choice = "ignore" to dismiss
    """
    from config import is_admin

    query = update.callback_query
    await query.answer()

    # Check admin permission
    if not is_admin(update.effective_user.id):
        await query.edit_message_text("Unauthorized: Admin only")
        return

    # Parse callback data
    data = query.data.split(":")
    if len(data) != 3:
        await query.edit_message_text("Invalid callback data")
        return

    _, request_id, choice = data

    # Validate request exists
    if request_id not in pending_requests:
        await query.edit_message_text("This suggestion has expired")
        return

    request = pending_requests[request_id]

    # Check expiration
    created_at = request.get("created_at")
    if created_at and datetime.now() - created_at > SUGGESTION_TTL:
        del pending_requests[request_id]
        await query.edit_message_text("This suggestion has expired")
        return

    # Check duplicate execution
    if request.get("executed"):
        await query.edit_message_text("This suggestion has already been executed")
        return

    suggestions = request.get("suggestions", [])

    # Handle ignore
    if choice == "ignore":
        del pending_requests[request_id]
        await query.edit_message_text(
            query.message.text + "\n\n<i>Ignored</i>",
            parse_mode="HTML"
        )
        return

    # Mark as executed to prevent duplicates
    request["executed"] = True

    # Handle execute all
    if choice == "all":
        results = []
        for i, s in enumerate(suggestions, 1):
            result = await execute_suggestion(s)
            results.append(f"[{i}] {result}")

        # Fix: mark record as executed
        record_id = request.get("record_id")
        if record_id:
            mark_executed(record_id)

        del pending_requests[request_id]
        await query.edit_message_text(
            query.message.text + "\n\n<b>Executed All:</b>\n" + "\n".join(results),
            parse_mode="HTML"
        )
        return

    # Handle single execution
    try:
        idx = int(choice) - 1
        if idx < 0 or idx >= len(suggestions):
            await query.edit_message_text(f"Invalid suggestion index: {choice}")
            return

        suggestion = suggestions[idx]
        result = await execute_suggestion(suggestion)

        # Fix: mark record as executed
        record_id = request.get("record_id")
        if record_id:
            mark_executed(record_id)

        del pending_requests[request_id]
        await query.edit_message_text(
            query.message.text + f"\n\n<b>Executed [{choice}]:</b> {result}",
            parse_mode="HTML"
        )

    except ValueError:
        await query.edit_message_text(f"Invalid choice: {choice}")
