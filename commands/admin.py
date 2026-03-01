"""Admin commands module - write operations requiring admin privileges."""
import logging
import re

from telegram import Update
from telegram.ext import ContextTypes

from config import is_admin

logger = logging.getLogger(__name__)


def _get_api():
    """Lazy import api to avoid circular imports."""
    from main import api
    return api


def _get_contract():
    """Lazy import contract to avoid circular imports."""
    from main import contract
    return contract()


async def cmd_disable_strategy(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Disable a single strategy."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("Unauthorized: Admin only")
        return
    args = ctx.args or []
    if len(args) == 0:
        await update.message.reply_text("Usage: /disable_strategy <id>")
        return
    try:
        strategy_id = int(args[0])
    except ValueError:
        await update.message.reply_text("Error: Strategy ID must be a number")
        return
    result = await _get_contract().disable_strategy(strategy_id)
    if result.get("success"):
        tx_hash = result.get("transactionHash", "")
        await update.message.reply_text(f"Strategy #{strategy_id} disabled\nTX: {tx_hash}")
    else:
        error = result.get("error", "Unknown error")
        if "doesn't exist" in error.lower() or "not active" in error.lower():
            await update.message.reply_text(f"Strategy #{strategy_id} not found or already disabled")
        else:
            await update.message.reply_text(f"Transaction failed: {error}")


async def cmd_disable_all(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Disable all active strategies."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("Unauthorized: Admin only")
        return
    api = _get_api()
    async def get_active_count() -> int:
        data = await api.get_strategies()
        if isinstance(data, dict) and "error" in data:
            logger.warning(f"Failed to fetch strategies: {data['error']}")
            return -1
        return len(data) if data else 0
    result = await _get_contract().disable_all_strategies(get_active_count)
    if result.get("success"):
        disabled_count = result.get("disabledCount", -1)
        if result.get("message") == "no_active_strategies" or disabled_count == 0:
            await update.message.reply_text("No active strategies")
        elif disabled_count == -1:
            tx_hash = result.get("transactionHash", "")
            await update.message.reply_text(f"All strategies disabled\nTX: {tx_hash}")
        else:
            tx_hash = result.get("transactionHash", "")
            await update.message.reply_text(f"Disabled {disabled_count} strategies\nTX: {tx_hash}")
    else:
        error = result.get("error", "Unknown error")
        await update.message.reply_text(f"Transaction failed: {error}")


async def cmd_add_strategy(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Add a new trading strategy."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("Unauthorized: Admin only")
        return
    args = ctx.args or []
    if len(args) == 0:
        await update.message.reply_text("Usage: /add_strategy <strategy_content>")
        return
    content = " ".join(args)
    if not content.strip():
        await update.message.reply_text("Error: Strategy content cannot be empty")
        return
    MAX_STRATEGY_LENGTH = 500
    if len(content) > MAX_STRATEGY_LENGTH:
        await update.message.reply_text(f"Error: Strategy too long (max {MAX_STRATEGY_LENGTH} chars)")
        return
    logger.info(f"Admin {update.effective_user.id} adding strategy: {content[:50]}...")
    result = await _get_contract().add_strategy(content)
    if result.get("success"):
        strategy_id = result.get("strategyId")
        tx_hash = result.get("transactionHash", "")
        if strategy_id is None:
            await update.message.reply_text(
                f"Strategy added but could not parse ID\nTX: {tx_hash}\nCheck transaction for strategy ID")
        else:
            await update.message.reply_text(f"Strategy added, ID: #{strategy_id}\nTX: {tx_hash}")
    else:
        error = result.get("error", "Unknown error")
        if "max" in error.lower() or "limit" in error.lower() or "8" in error:
            await update.message.reply_text("Error: Strategy limit reached (max 8)")
        else:
            await update.message.reply_text(f"Failed to add: {error}")


async def cmd_pause(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Pause Agent trading."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("Unauthorized: Admin only")
        return
    api = _get_api()
    vault_data = await api.get_vault()
    if isinstance(vault_data, dict) and vault_data.get("paused") is True:
        await update.message.reply_text("Agent is already paused")
        return
    logger.info(f"Admin {update.effective_user.id} pausing vault")
    result = await _get_contract().pause_vault(True)
    if result.get("success"):
        tx_hash = result.get("transactionHash", "")
        await update.message.reply_text(f"Agent paused, no trades will execute\nTX: {tx_hash}")
    else:
        error = result.get("error", "Unknown error")
        await update.message.reply_text(f"Pause failed: {error}")


async def cmd_resume(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Resume Agent trading."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("Unauthorized: Admin only")
        return
    api = _get_api()
    vault_data = await api.get_vault()
    if isinstance(vault_data, dict) and vault_data.get("paused") is False:
        await update.message.reply_text("Agent is already running")
        return
    logger.info(f"Admin {update.effective_user.id} resuming vault")
    result = await _get_contract().pause_vault(False)
    if result.get("success"):
        tx_hash = result.get("transactionHash", "")
        await update.message.reply_text(f"Agent resumed, trading enabled\nTX: {tx_hash}")
    else:
        error = result.get("error", "Unknown error")
        await update.message.reply_text(f"Resume failed: {error}")


async def cmd_update_settings(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """View or update Vault trading settings."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("Unauthorized: Admin only")
        return
    args = ctx.args or []
    api = _get_api()

    # No args: show current settings
    if len(args) == 0:
        vault_data = await api.get_vault()
        if "error" in vault_data:
            await update.message.reply_text(f"Error: {vault_data['error']}")
            return

        # Trading settings
        max_trade = int(vault_data.get('maxTradeAmount', 0))
        slippage = int(vault_data.get('slippageBps', 0))

        # Behavior preferences labels
        activity_labels = {0: "Very Low", 1: "Low", 2: "Medium", 3: "High", 4: "Very High"}
        risk_labels = {0: "Conservative", 1: "Moderate", 2: "Balanced", 3: "Growth", 4: "Aggressive"}
        size_labels = {0: "Tiny", 1: "Small", 2: "Medium", 3: "Large", 4: "Huge"}
        style_labels = {0: "Scalper", 1: "Day Trader", 2: "Swing", 3: "Position", 4: "HODL"}
        diversify_labels = {0: "Concentrated", 1: "Focused", 2: "Balanced", 3: "Diversified", 4: "Wide"}

        trading_activity = activity_labels.get(vault_data.get('tradingActivity', 2), "Medium")
        risk_pref = risk_labels.get(vault_data.get('assetRiskPreference', 2), "Balanced")
        trade_size = size_labels.get(vault_data.get('tradeSize', 2), "Medium")
        holding_style = style_labels.get(vault_data.get('holdingStyle', 2), "Swing")
        diversification = diversify_labels.get(vault_data.get('diversification', 2), "Balanced")

        await update.message.reply_text(
            f"Current Settings\n\n"
            f"Trading Settings:\n"
            f"  Max Trade: {max_trade} BPS ({max_trade/100:.1f}%)\n"
            f"  Slippage: {slippage} BPS ({slippage/100:.1f}%)\n\n"
            f"Behavior Preferences:\n"
            f"  Trading Activity: {trading_activity}\n"
            f"  Risk Preference: {risk_pref}\n"
            f"  Trade Size: {trade_size}\n"
            f"  Holding Style: {holding_style}\n"
            f"  Diversification: {diversification}\n\n"
            f"To update trading: /update_settings max_trade=1000 slippage=50")
        return
    params = {}
    for arg in args:
        match = re.match(r'(\w+)=(\d+)', arg)
        if match:
            key, value = match.groups()
            params[key] = int(value)
    valid_keys = {'max_trade', 'slippage'}
    invalid_keys = set(params.keys()) - valid_keys
    if invalid_keys:
        await update.message.reply_text(
            f"Unknown params: {', '.join(invalid_keys)}\nSupported: max_trade, slippage")
        return
    if not params:
        await update.message.reply_text("Provide at least one parameter\nUsage: /update_settings max_trade=1000 slippage=50")
        return
    api = _get_api()
    try:
        vault_data = await api.get_vault()
        current_max_trade = int(vault_data.get('maxTradeAmount', 1000))
        current_slippage = int(vault_data.get('slippageBps', 50))
    except Exception as e:
        logger.warning(f"Failed to fetch current settings: {e}")
        current_max_trade = 1000
        current_slippage = 50
    max_trade_bps = params.get('max_trade', current_max_trade)
    slippage_bps = params.get('slippage', current_slippage)
    logger.info(f"Admin {update.effective_user.id} updating settings: max_trade={max_trade_bps}, slippage={slippage_bps}")
    result = await _get_contract().update_settings(max_trade_bps, slippage_bps)
    if result.get("success"):
        tx_hash = result.get("transactionHash", "")
        await update.message.reply_text(
            f"Settings updated\n"
            f"max_trade: {max_trade_bps} BPS ({max_trade_bps/100:.1f}%)\n"
            f"slippage: {slippage_bps} BPS ({slippage_bps/100:.1f}%)\n"
            f"TX: {tx_hash}")
    else:
        error = result.get("error", "Unknown error")
        await update.message.reply_text(f"Update failed: {error}")
