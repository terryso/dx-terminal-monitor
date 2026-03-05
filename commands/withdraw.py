"""Withdraw command module - ETH withdrawal with confirmation flow."""

import logging

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters
from web3 import Web3

from config import is_admin
from utils.error_handler import safe_command

logger = logging.getLogger(__name__)

# Conversation states
WAITING_CONFIRMATION = 1
END = ConversationHandler.END

# Temporary storage for pending withdrawals (production should use Redis)
_pending_withdrawals = {}


def _get_api():
    """Lazy import api to avoid circular imports."""
    from main import api

    return api


def _get_contract():
    """Lazy import contract to avoid circular imports."""
    from main import contract

    return contract()


@safe_command
async def cmd_withdraw(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Withdraw command entry - request confirmation."""
    # Admin permission check (high-risk operation)
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("Unauthorized: Admin only")
        return END

    # Parse arguments
    args = ctx.args or []
    if len(args) == 0:
        await update.message.reply_text(
            "Usage: /withdraw <amount>\n"
            "Example: /withdraw 0.5\n"
            "Info: Withdraw specified ETH amount to admin wallet"
        )
        return END

    # Parse amount
    try:
        amount_eth = float(args[0])
        if amount_eth <= 0:
            await update.message.reply_text("Amount must be greater than 0")
            return END
        # Validate precision (max 6 decimal places for ETH)
        if len(args[0].split(".")[-1]) > 6 if "." in args[0] else False:
            await update.message.reply_text("Amount precision too high (max 6 decimals)")
            return END
    except ValueError:
        await update.message.reply_text("Invalid amount format. Enter a number like: 0.5")
        return END

    api = _get_api()

    # Get current balance for pre-check
    try:
        vault_data = await api.get_vault()
        balance_eth = float(vault_data.get("balance", 0))
    except Exception as e:
        logger.warning(f"Failed to fetch balance: {e}")
        balance_eth = None  # Cannot get balance, skip pre-check

    # Balance check
    if balance_eth is not None and amount_eth > balance_eth:
        await update.message.reply_text(
            f"Insufficient balance. Available: {balance_eth:.4f} ETH\nRequested: {amount_eth} ETH"
        )
        return END

    # Store pending withdrawal amount
    user_id = update.effective_user.id
    _pending_withdrawals[user_id] = amount_eth

    # Confirmation
    await update.message.reply_text(
        f"Confirm withdrawal of {amount_eth} ETH to your wallet?\n[Y] Confirm\n[N] Cancel"
    )
    return WAITING_CONFIRMATION


@safe_command
async def handle_withdraw_confirm(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handle withdrawal confirmation."""
    user_id = update.effective_user.id
    response = update.message.text.strip().upper()

    if response not in ("Y", "N", "YES", "NO"):
        await update.message.reply_text("Please reply Y to confirm or N to cancel")
        return WAITING_CONFIRMATION

    if response in ("N", "NO"):
        # Cancel operation
        _pending_withdrawals.pop(user_id, None)
        await update.message.reply_text("Withdrawal cancelled")
        return END

    # Confirm withdrawal
    amount_eth = _pending_withdrawals.pop(user_id, None)
    if amount_eth is None:
        await update.message.reply_text("Session expired. Please run /withdraw again")
        return END

    # Convert to Wei
    amount_wei = int(Web3.to_wei(amount_eth, "ether"))

    # Log admin action for audit
    logger.info(f"Admin {user_id} withdrawing {amount_eth} ETH")

    # Call contract
    result = await _get_contract().withdraw_eth(amount_wei)

    if result.get("success"):
        tx_hash = result.get("transactionHash", "")
        logger.info(f"Withdrawal confirmed: {amount_eth} ETH by user {user_id}, tx: {tx_hash}")
        await update.message.reply_text(f"Withdrawn {amount_eth} ETH\nTX: {tx_hash}")
    else:
        error = result.get("error", "Unknown error")
        await update.message.reply_text(f"Withdrawal failed: {error}")

    return END


@safe_command
async def handle_withdraw_cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handle withdrawal cancellation via /cancel command."""
    user_id = update.effective_user.id
    _pending_withdrawals.pop(user_id, None)
    await update.message.reply_text("Withdrawal cancelled")
    return END


def create_withdraw_handler() -> ConversationHandler:
    """Create withdrawal conversation handler."""
    return ConversationHandler(
        entry_points=[CommandHandler("withdraw", cmd_withdraw)],
        states={
            WAITING_CONFIRMATION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_withdraw_confirm)
            ],
        },
        fallbacks=[CommandHandler("cancel", handle_withdraw_cancel)],
    )
