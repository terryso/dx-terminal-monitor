"""
Telegram 通知模块 for Story 4-2

实现活动消息格式化和 Telegram 推送功能。
"""

import logging
from datetime import datetime
from typing import Dict, Any, List

from telegram import Bot

from config import ADMIN_USERS, ALLOWED_USERS, CHAIN_ID, NOTIFY_USERS

logger = logging.getLogger(__name__)

# Etherscan 基础 URL (根据链 ID)
ETHERSCAN_BASE_URLS = {
    1: "https://etherscan.io/tx",
    11155111: "https://sepolia.etherscan.io/tx",
    17000: "https://holesky.etherscan.io/tx",
}


def format_eth(wei: str) -> str:
    """将 Wei 格式化为 ETH。

    Args:
        wei: Wei 数量的字符串表示

    Returns:
        格式化的 ETH 字符串 (6 位小数)
    """
    try:
        return f"{float(wei) / 1e18:.6f}"
    except (ValueError, TypeError):
        return wei


def format_usd(value: str | float) -> str:
    """将数值格式化为 USD。

    Args:
        value: 数值 (字符串或数字)

    Returns:
        格式化的 USD 字符串 (带千位分隔符)
    """
    try:
        return f"${float(value):,.2f}"
    except (ValueError, TypeError):
        return str(value)


def format_timestamp(ts: str) -> str:
    """格式化 ISO 时间戳为可读格式。

    Args:
        ts: ISO 格式时间戳字符串

    Returns:
        格式化的时间字符串 (YYYY-MM-DD HH:MM:SS)
    """
    try:
        dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        return ts


def get_tx_url(tx_hash: str) -> str:
    """生成交易浏览器链接。

    根据配置的 CHAIN_ID 生成对应链的交易链接。

    Args:
        tx_hash: 交易哈希

    Returns:
        Etherscan 交易链接
    """
    base_url = ETHERSCAN_BASE_URLS.get(CHAIN_ID, ETHERSCAN_BASE_URLS[1])
    return f"{base_url}/{tx_hash}"


def format_activity_message(activity: Dict[str, Any]) -> str:
    """格式化活动为 Telegram 消息。

    支持 Swap/Deposit/Withdrawal 三种活动类型。

    Args:
        activity: 活动字典，包含 type, timestamp, id 等字段

    Returns:
        格式化的 Telegram 消息字符串
    """
    activity_type = activity.get('type', 'unknown')
    timestamp = format_timestamp(activity.get('timestamp', ''))
    activity_id = activity.get('id', '')

    lines = [
        "🔔 Agent 操作通知\n",
        f"类型: {activity_type.upper()}",
        f"时间: {timestamp}",
    ]

    if activity_type == 'swap':
        swap = activity.get('swap', {})
        side = swap.get('side', '?').upper()
        token = swap.get('tokenSymbol', '?')
        eth_amt = format_eth(swap.get('ethAmount', '0'))
        price = format_usd(swap.get('effectivePriceUsd', '0'))

        lines.extend([
            f"方向: {side}",
            f"代币: {token}",
            f"数量: {eth_amt} ETH",
            f"价格: {price}",
        ])

    elif activity_type == 'deposit':
        deposit = activity.get('deposit', {})
        amt = format_eth(deposit.get('amountWei', '0'))
        lines.append(f"金额: {amt} ETH")

    elif activity_type == 'withdrawal':
        withdrawal = activity.get('withdrawal', {})
        amt = format_eth(withdrawal.get('amountWei', '0'))
        lines.append(f"金额: {amt} ETH")

    # 添加交易链接
    if activity_id:
        lines.append(f"查看: {get_tx_url(activity_id)}")

    return '\n'.join(lines)


class TelegramNotifier:
    """Telegram 通知推送器。

    将活动消息推送到授权用户的 Telegram。

    Attributes:
        bot: Telegram Bot 实例
        notify_users: 接收通知的用户 ID 列表
    """

    def __init__(self, bot: Bot, notify_users: List[int] = None):
        """初始化通知器。

        Args:
            bot: Telegram Bot 实例
            notify_users: 接收通知的用户 ID 列表，默认使用 NOTIFY_USERS 配置
        """
        self.bot = bot
        self.notify_users = notify_users or []

        # 如果没有指定用户，使用配置中的用户 (优先级: NOTIFY_USERS > ADMIN_USERS > ALLOWED_USERS)
        if not self.notify_users:
            self.notify_users = NOTIFY_USERS if NOTIFY_USERS else (ADMIN_USERS if ADMIN_USERS else ALLOWED_USERS)

        logger.info(f"TelegramNotifier initialized for users: {self.notify_users}")

    async def send_notification(self, activity: Dict[str, Any]) -> None:
        """发送活动通知到所有授权用户。

        Args:
            activity: 活动字典
        """
        if not self.notify_users:
            logger.warning("No notify users configured, skipping notification")
            return

        # 格式化消息
        message = format_activity_message(activity)

        # 发送到每个用户
        for user_id in self.notify_users:
            try:
                await self.bot.send_message(chat_id=user_id, text=message)
                logger.info(f"Notification sent to user {user_id} for activity {activity.get('id')}")
            except Exception as e:
                logger.error(f"Failed to send notification to user {user_id}: {e}")
