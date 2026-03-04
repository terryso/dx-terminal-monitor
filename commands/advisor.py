"""
AI Strategy Advisor Commands for Story 8-3

Commands to control the AI strategy advisor service and handle callback queries.
"""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from config import is_admin

logger = logging.getLogger(__name__)

# Will be set by main.py during initialization
_advisor_monitor = None


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


# Re-export handle_advisor_callback from advisor_monitor for convenience
async def handle_advisor_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handle inline keyboard callbacks - delegates to advisor_monitor."""
    from advisor_monitor import handle_advisor_callback as _handle
    await _handle(update, ctx)
