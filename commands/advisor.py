"""
AI Strategy Advisor Commands for Story 8-3

Commands to control the AI strategy advisor service and handle callback queries.
"""

import logging
from datetime import datetime, timedelta

from telegram import Update
from telegram.ext import ContextTypes

from config import is_admin

logger = logging.getLogger(__name__)

# Will be set by main.py during initialization
_advisor_monitor = None

# Cooldown tracking for manual analysis (Story 8-5)
_last_manual_analysis: dict[int, datetime] = {}
MANUAL_ANALYSIS_COOLDOWN = timedelta(minutes=5)


def set_advisor_monitor(monitor):
    """Set the advisor monitor instance."""
    global _advisor_monitor
    _advisor_monitor = monitor


async def cmd_advisor_on(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Enable AI strategy advisor."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("Unauthorized: Admin only")
        return

    if _advisor_monitor is None:
        await update.message.reply_text("Advisor monitor not initialized")
        return

    if _advisor_monitor.running:
        await update.message.reply_text("Advisor is already running")
        return

    await _advisor_monitor.start_background()
    logger.info(f"Admin {update.effective_user.id} started AI advisor")
    await update.message.reply_text("AI Strategy Advisor enabled")


async def cmd_advisor_off(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Disable AI strategy advisor."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("Unauthorized: Admin only")
        return

    if _advisor_monitor is None:
        await update.message.reply_text("Advisor monitor not initialized")
        return

    if not _advisor_monitor.running:
        await update.message.reply_text("Advisor is not running")
        return

    _advisor_monitor.stop()
    logger.info(f"Admin {update.effective_user.id} stopped AI advisor")
    await update.message.reply_text("AI Strategy Advisor disabled")


async def cmd_advisor_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Show AI strategy advisor status."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("Unauthorized: Admin only")
        return

    if _advisor_monitor is None:
        await update.message.reply_text("Advisor monitor not initialized")
        return

    status = "Running" if _advisor_monitor.running else "Stopped"
    interval = _advisor_monitor.interval_seconds // 3600
    last = _advisor_monitor.last_analysis
    last_str = last.strftime("%Y-%m-%d %H:%M") if last else "Never"

    await update.message.reply_text(
        f"AI Strategy Advisor Status\n\n"
        f"State: {status}\n"
        f"Interval: {interval}h\n"
        f"Last Analysis: {last_str}"
    )


async def cmd_advisor_analyze(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Manually trigger AI strategy analysis (Story 8-5).

    Flow:
    1. Check admin permission
    2. Check cooldown (prevents spam even when monitor unavailable)
    3. Check monitor initialization
    4. Execute analysis and push results

    Note: Cooldown is recorded on:
    - Successful analysis with suggestions
    - Successful analysis with no suggestions
    - Monitor not initialized (prevents spam while system recovers)
    Cooldown is NOT recorded on:
    - Permission failure (user should not retry anyway)
    - Analysis exceptions (user may want to retry)
    """
    logger.info("cmd_advisor_analyze called")
    user_id = update.effective_user.id
    logger.info(f"User ID: {user_id}, admin check: {is_admin(user_id)}")

    # Check admin permission
    if not is_admin(user_id):
        await update.message.reply_text("Unauthorized: Admin only")
        return

    # Check cooldown FIRST (before monitor check) to prevent spam
    # even when monitor is unavailable
    last_time = _last_manual_analysis.get(user_id)
    if last_time and datetime.now() - last_time < MANUAL_ANALYSIS_COOLDOWN:
        remaining = MANUAL_ANALYSIS_COOLDOWN - (datetime.now() - last_time)
        await update.message.reply_text(
            f"Please wait {int(remaining.total_seconds() // 60)} min before next analysis"
        )
        return

    # Check advisor monitor initialized
    if _advisor_monitor is None:
        # Record cooldown even on monitor init failure to prevent spam
        # while system is recovering
        _last_manual_analysis[user_id] = datetime.now()
        await update.message.reply_text("Advisor monitor not initialized")
        return

    # Send status message
    status_msg = await update.message.reply_text("Analyzing your portfolio...")

    try:
        # Execute analysis
        suggestions = await _advisor_monitor.advisor.analyze()

        # Handle no suggestions
        if not suggestions:
            await status_msg.edit_text("No suggestions at this time. Your portfolio looks good!")
            _last_manual_analysis[user_id] = datetime.now()
            return

        # Collect context and push suggestions
        collected = await _advisor_monitor.advisor.collector.collect()

        # Build context with proper formatting
        from utils.formatters import format_eth, format_usd

        balance = "N/A"
        pnl = "N/A"
        token_count = 0
        strategy_count = 0

        if collected.positions and "error" not in collected.positions:
            raw_balance = collected.positions.get('ethBalance', 0)
            balance = f"{format_eth(str(raw_balance))} ETH"
            raw_pnl = collected.positions.get('overallPnlUsd', collected.positions.get('totalPnlUsd', 0))
            pnl = format_usd(raw_pnl)
            token_count = len(collected.positions.get('positions', collected.positions.get('tokens', [])))

        if collected.strategies and not (isinstance(collected.strategies, dict) and "error" in collected.strategies):
            import time
            current_time = int(time.time())
            active_strategies = [
                s for s in collected.strategies
                if s.get('active', True) and (s.get('expiry', 0) == 0 or s.get('expiry', 0) > current_time)
            ]
            strategy_count = len(active_strategies)

        context = {
            'balance': balance,
            'positions': token_count,
            'strategies': strategy_count,
            'pnl': pnl,
        }

        # Import push_suggestions here to avoid circular dependency
        from advisor_monitor import push_suggestions

        request_id = await push_suggestions(
            chat_id=update.effective_chat.id,
            suggestions=suggestions,
            context=context,
            bot=ctx.bot
        )

        # Update status message
        await status_msg.edit_text(f"Analysis complete! {len(suggestions)} suggestion(s) generated.")

        # Record call time
        _last_manual_analysis[user_id] = datetime.now()
        logger.info(f"Manual analysis completed by admin {user_id} (request_id={request_id})")

    except Exception as e:
        logger.error(f"Manual analysis failed: {e}")
        await status_msg.edit_text(f"Analysis failed: {str(e)}")
        # Note: Cooldown NOT recorded on exception - user may want to retry
        # after fixing the underlying issue


# Re-export handle_advisor_callback from advisor_monitor for convenience
async def handle_advisor_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handle inline keyboard callbacks - delegates to advisor_monitor."""
    from advisor_monitor import handle_advisor_callback as _handle
    await _handle(update, ctx)
