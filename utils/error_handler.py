"""Error handling utilities for command handlers."""

import logging
from collections.abc import Callable
from functools import wraps

logger = logging.getLogger(__name__)

# Import END for ConversationHandler compatibility
try:
    from telegram.ext import ConversationHandler

    _END = ConversationHandler.END
except ImportError:
    _END = None


def safe_command(func: Callable) -> Callable:
    """Decorator to catch command exceptions and reply to user.

    Ensures that users always get feedback, even when commands fail.
    Logs the full exception for debugging.

    Args:
        func: Async command handler function

    Returns:
        Wrapped function with error handling

    Example:
        @safe_command
        async def cmd_balance(update, ctx):
            data = await api.get_positions()
            await update.message.reply_text(f"Balance: {data}")
    """

    @wraps(func)
    async def wrapper(update, ctx):
        try:
            return await func(update, ctx)
        except Exception as e:
            # Log full exception with traceback
            logger.error(
                "Command %s failed for user %s: %s",
                func.__name__,
                update.effective_user.id if update.effective_user else "unknown",
                e,
                exc_info=True,
            )
            # Try to notify user
            try:
                if update.message:
                    await update.message.reply_text(f"Command execution failed: {e}")
            except Exception as reply_error:
                logger.error("Failed to send error reply: %s", reply_error)
            # Return END for ConversationHandler compatibility
            return _END

    return wrapper
