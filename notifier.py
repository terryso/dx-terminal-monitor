"""
Telegram Notification Module for Story 4-2

Implements activity message formatting and Telegram push functionality.
"""

import logging
from datetime import datetime
from typing import Any

from telegram import Bot

from config import ADMIN_USERS, ALLOWED_USERS, CHAIN_ID, NOTIFY_USERS

logger = logging.getLogger(__name__)

# Etherscan base URLs (by chain ID)
ETHERSCAN_BASE_URLS = {
    1: "https://etherscan.io/tx",
    11155111: "https://sepolia.etherscan.io/tx",
    17000: "https://holesky.etherscan.io/tx",
}


def format_eth(wei: str) -> str:
    """Convert Wei to ETH string.

    Args:
        wei: Wei amount as string

    Returns:
        Formatted ETH string (6 decimal places)
    """
    try:
        return f"{float(wei) / 1e18:.6f}"
    except (ValueError, TypeError):
        return wei


def format_usd(value: str | float) -> str:
    """Format value as USD string.

    Args:
        value: Numeric value (string or number)

    Returns:
        Formatted USD string (with appropriate decimal places)
    """
    try:
        num = float(value)
        # For very small values, use more decimal places or scientific notation
        if num == 0:
            return "$0.00"
        elif num < 0.01:
            # Use scientific notation for very small values
            return f"${num:.6f}".rstrip('0').rstrip('.')
        else:
            return f"${num:,.2f}"
    except (ValueError, TypeError):
        return str(value)


def format_token_amount(amount: str, decimals: int = 18) -> str:
    """Format token amount from wei-like string to human readable.

    Args:
        amount: Token amount in smallest unit (wei-like) or already formatted
        decimals: Token decimals (default 18 for most ERC20)

    Returns:
        Formatted token amount string
    """
    try:
        num = float(amount)
        # If already a small number or contains decimal point, assume it's already formatted
        if '.' in str(amount) or num < 1e15:
            # Already formatted, just apply K/M suffix if needed
            if num >= 1_000_000:
                return f"{num / 1_000_000:.2f}M"
            elif num >= 1_000:
                return f"{num / 1_000:.2f}K"
            elif num >= 1:
                return f"{num:.2f}"
            elif num > 0:
                return f"{num:.6f}".rstrip('0').rstrip('.')
            else:
                return "0"
        else:
            # Wei-like format, need to divide by decimals
            num = num / (10 ** decimals)
            if num >= 1_000_000:
                return f"{num / 1_000_000:.2f}M"
            elif num >= 1_000:
                return f"{num / 1_000:.2f}K"
            elif num >= 1:
                return f"{num:.2f}"
            elif num > 0:
                return f"{num:.6f}".rstrip('0').rstrip('.')
            else:
                return "0"
    except (ValueError, TypeError):
        return str(amount)


def format_timestamp(ts: str | int) -> str:
    """Format timestamp to readable format.

    Args:
        ts: ISO format timestamp string or Unix timestamp (seconds)

    Returns:
        Formatted time string (YYYY-MM-DD HH:MM:SS UTC)
    """
    try:
        # Handle Unix timestamp (integer or numeric string)
        if isinstance(ts, int) or (isinstance(ts, str) and ts.isdigit()):
            dt = datetime.utcfromtimestamp(int(ts))
            return dt.strftime('%Y-%m-%d %H:%M:%S') + ' UTC'
        # Handle ISO format string
        dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S') + ' UTC'
    except Exception:
        return str(ts)


def get_tx_url(tx_hash: str) -> str:
    """Generate transaction explorer URL.

    Args:
        tx_hash: Transaction hash

    Returns:
        Etherscan transaction URL
    """
    base_url = ETHERSCAN_BASE_URLS.get(CHAIN_ID, ETHERSCAN_BASE_URLS[1])
    return f"{base_url}/{tx_hash}"


def format_activity_message(activity: dict[str, Any]) -> str:
    """Format activity as Telegram message.

    Supports Swap/Deposit/Withdrawal activity types.

    Args:
        activity: Activity dict with type, timestamp, id fields

    Returns:
        Formatted Telegram message string
    """
    activity_type = activity.get('type', 'unknown')
    timestamp = format_timestamp(activity.get('timestamp', ''))
    activity_id = activity.get('id', '')

    lines = [
        "🔔 Agent Activity Notification\n",
        f"Type: {activity_type.upper()}",
        f"Time: {timestamp}",
    ]

    if activity_type == 'swap':
        swap = activity.get('swap', {})
        side = swap.get('side', '?').upper()
        token = swap.get('tokenSymbol', '?')
        eth_amt = format_eth(swap.get('ethAmount', '0'))

        # Try multiple price fields: effectivePriceUsd, priceUsd, avgPriceUsd
        price_val = (
            swap.get('effectivePriceUsd') or
            swap.get('priceUsd') or
            swap.get('avgPriceUsd') or
            '0'
        )
        price = format_usd(price_val)

        # Try to get token quantity if available
        token_qty_raw = swap.get('tokenAmount') or swap.get('quantity')
        token_qty = format_token_amount(token_qty_raw) if token_qty_raw else None

        lines.extend([
            f"Side: {side}",
            f"Token: {token}",
            f"ETH Amount: {eth_amt} ETH",
        ])

        # Add token quantity if available
        if token_qty:
            lines.append(f"Token Qty: {token_qty}")

        lines.append(f"Price: {price}")

    elif activity_type == 'deposit':
        deposit = activity.get('deposit', {})
        amt = format_eth(deposit.get('amountWei', '0'))
        lines.append(f"Amount: {amt} ETH")

    elif activity_type == 'withdrawal':
        withdrawal = activity.get('withdrawal', {})
        amt = format_eth(withdrawal.get('amountWei', '0'))
        lines.append(f"Amount: {amt} ETH")

    # Add transaction link
    if activity_id:
        lines.append(f"View: {get_tx_url(activity_id)}")

    return '\n'.join(lines)


class TelegramNotifier:
    """Telegram notification sender.

    Pushes activity messages to authorized users via Telegram.

    Attributes:
        bot: Telegram Bot instance
        notify_users: List of user IDs to receive notifications
    """

    def __init__(self, bot: Bot, notify_users: list[int] = None):
        """Initialize notifier.

        Args:
            bot: Telegram Bot instance
            notify_users: List of user IDs to notify, defaults to NOTIFY_USERS config
        """
        self.bot = bot
        self.notify_users = notify_users or []

        # If no users specified, use config (priority: NOTIFY_USERS > ADMIN_USERS > ALLOWED_USERS)
        if not self.notify_users:
            self.notify_users = NOTIFY_USERS if NOTIFY_USERS else (ADMIN_USERS if ADMIN_USERS else ALLOWED_USERS)

        logger.info(f"TelegramNotifier initialized for users: {self.notify_users}")

    async def send_notification(self, activity: dict[str, Any]) -> None:
        """Send activity notification to all authorized users.

        Args:
            activity: Activity dictionary
        """
        if not self.notify_users:
            logger.warning("No notify users configured, skipping notification")
            return

        # Format message
        message = format_activity_message(activity)

        # Send to each user
        for user_id in self.notify_users:
            try:
                await self.bot.send_message(chat_id=user_id, text=message)
                logger.info(f"Notification sent to user {user_id} for activity {activity.get('id')}")
            except Exception as e:
                logger.error(f"Failed to send notification to user {user_id}: {e}")
