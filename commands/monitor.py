"""Monitor commands module - monitoring service control commands."""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from config import is_admin
from utils.error_handler import safe_command

logger = logging.getLogger(__name__)

# Monitor instance (set by main.py via setter)
_monitor_instance = None


def set_monitor_instance(instance):
    """Set monitor instance, called by main.py in post_init."""
    global _monitor_instance
    _monitor_instance = instance


@safe_command
async def cmd_monitor_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Check monitor service status."""
    # Admin permission check
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("Unauthorized: Admin only")
        return

    # Check if monitor is initialized
    if _monitor_instance is None:
        await update.message.reply_text("Monitor not initialized")
        return

    # Get status
    status = "Running" if _monitor_instance.running else "Stopped"
    interval = _monitor_instance.poll_interval
    seen_count = len(_monitor_instance.seen_ids)

    await update.message.reply_text(
        f"Monitor Status\n\n"
        f"State: {status}\n"
        f"Poll Interval: {interval}s\n"
        f"Activities Processed: {seen_count}"
    )


@safe_command
async def cmd_monitor_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Start monitor service."""
    # Admin permission check
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("Unauthorized: Admin only")
        return

    # Check if monitor is initialized
    if _monitor_instance is None:
        await update.message.reply_text("Monitor not initialized, please restart Bot")
        return

    # Check if already running
    if _monitor_instance.running:
        await update.message.reply_text("Monitor already running")
        return

    # Start monitor
    await _monitor_instance.start_background()
    logger.info(f"Admin {update.effective_user.id} started activity monitor")

    await update.message.reply_text(
        f"Monitor started\nPoll interval: {_monitor_instance.poll_interval}s"
    )


@safe_command
async def cmd_monitor_stop(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Stop monitor service."""
    # Admin permission check
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("Unauthorized: Admin only")
        return

    # Check if monitor is initialized
    if _monitor_instance is None:
        await update.message.reply_text("Monitor not initialized")
        return

    # Check if already stopped
    if not _monitor_instance.running:
        await update.message.reply_text("Monitor already stopped")
        return

    # Stop monitor
    _monitor_instance.stop()
    logger.info(f"Admin {update.effective_user.id} stopped activity monitor")

    await update.message.reply_text("Monitor stopped")
