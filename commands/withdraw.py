"""提款命令模块 - 带对话流程的 ETH 提款功能。"""
import logging

from telegram import Update
from telegram.ext import (
    ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
)
from web3 import Web3

from config import is_admin

logger = logging.getLogger(__name__)

# Conversation states
WAITING_CONFIRMATION = 1
END = ConversationHandler.END

# Temporary storage for pending withdrawals (production should use Redis)
_pending_withdrawals = {}


def _get_api():
    """延迟导入 api 避免循环导入。"""
    from main import api
    return api


def _get_contract():
    """延迟导入 contract 避免循环导入。"""
    from main import contract
    return contract()


async def cmd_withdraw(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """提款命令入口 - 请求确认。"""
    # Admin permission check (high-risk operation)
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("未授权: 仅管理员可提取资金")
        return END

    # Parse arguments
    args = ctx.args or []
    if len(args) == 0:
        await update.message.reply_text(
            "用法: /withdraw <amount>\n"
            "示例: /withdraw 0.5\n"
            "说明: 提取指定数量的 ETH 到管理员钱包"
        )
        return END

    # Parse amount
    try:
        amount_eth = float(args[0])
        if amount_eth <= 0:
            await update.message.reply_text("金额必须大于 0")
            return END
        # Validate precision (max 6 decimal places for ETH)
        if len(args[0].split('.')[-1]) > 6 if '.' in args[0] else False:
            await update.message.reply_text("金额精度过高，最多支持 6 位小数")
            return END
    except ValueError:
        await update.message.reply_text("无效的金额格式，请输入数字如: 0.5")
        return END

    api = _get_api()

    # Get current balance for pre-check
    try:
        vault_data = await api.get_vault()
        balance_eth = float(vault_data.get('balance', 0))
    except Exception as e:
        logger.warning(f"Failed to fetch balance: {e}")
        balance_eth = None  # Cannot get balance, skip pre-check

    # Balance check
    if balance_eth is not None and amount_eth > balance_eth:
        await update.message.reply_text(
            f"余额不足，当前可用: {balance_eth:.4f} ETH\n"
            f"请求提取: {amount_eth} ETH"
        )
        return END

    # Store pending withdrawal amount
    user_id = update.effective_user.id
    _pending_withdrawals[user_id] = amount_eth

    # Confirmation
    await update.message.reply_text(
        f"确认提取 {amount_eth} ETH 到你的钱包？\n"
        f"[Y] 确认\n"
        f"[N] 取消"
    )
    return WAITING_CONFIRMATION


async def handle_withdraw_confirm(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """处理提款确认。"""
    user_id = update.effective_user.id
    response = update.message.text.strip().upper()

    if response not in ('Y', 'N', 'YES', 'NO'):
        await update.message.reply_text("请回复 Y 确认或 N 取消")
        return WAITING_CONFIRMATION

    if response in ('N', 'NO'):
        # Cancel operation
        _pending_withdrawals.pop(user_id, None)
        await update.message.reply_text("已取消提取")
        return END

    # Confirm withdrawal
    amount_eth = _pending_withdrawals.pop(user_id, None)
    if amount_eth is None:
        await update.message.reply_text("会话已过期，请重新执行 /withdraw 命令")
        return END

    # Convert to Wei
    amount_wei = int(Web3.to_wei(amount_eth, 'ether'))

    # Log admin action for audit
    logger.info(f"Admin {user_id} withdrawing {amount_eth} ETH")

    # Call contract
    result = await _get_contract().withdraw_eth(amount_wei)

    if result.get("success"):
        tx_hash = result.get("transactionHash", "")
        logger.info(f"Withdrawal confirmed: {amount_eth} ETH by user {user_id}, tx: {tx_hash}")
        await update.message.reply_text(
            f"已提取 {amount_eth} ETH\n"
            f"交易哈希: {tx_hash}"
        )
    else:
        error = result.get("error", "未知错误")
        await update.message.reply_text(f"提取失败: {error}")

    return END


async def handle_withdraw_cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """处理提款取消（通过 /cancel 命令）。"""
    user_id = update.effective_user.id
    _pending_withdrawals.pop(user_id, None)
    await update.message.reply_text("已取消提取")
    return END


def create_withdraw_handler() -> ConversationHandler:
    """创建提款对话处理器。"""
    return ConversationHandler(
        entry_points=[CommandHandler("withdraw", cmd_withdraw)],
        states={
            WAITING_CONFIRMATION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_withdraw_confirm)
            ],
        },
        fallbacks=[CommandHandler("cancel", handle_withdraw_cancel)],
    )
