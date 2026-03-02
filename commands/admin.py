"""Admin commands module - write operations requiring admin privileges."""
import logging
import re

from telegram import Update
from telegram.ext import ContextTypes
from web3 import Web3

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

        # Behavior preferences (raw values)
        trading_activity = vault_data.get('tradingActivity', '?')
        risk_pref = vault_data.get('assetRiskPreference', '?')
        trade_size = vault_data.get('tradeSize', '?')
        holding_style = vault_data.get('holdingStyle', '?')
        diversification = vault_data.get('diversification', '?')

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
            f"To update:\n"
            f"  /update_settings max_trade=1000 slippage=50\n"
            f"  /update_settings activity=3 risk=2 size=3 holding=4 diversification=2")
        return

    # Parse parameters
    params = {}
    for arg in args:
        match = re.match(r'(\w+)=(\d+)', arg)
        if match:
            key, value = match.groups()
            params[key] = int(value)

    # Valid parameter keys
    valid_keys = {
        'max_trade', 'slippage',
        'activity', 'risk', 'size', 'holding', 'diversification'
    }
    invalid_keys = set(params.keys()) - valid_keys
    if invalid_keys:
        await update.message.reply_text(
            f"Unknown params: {', '.join(invalid_keys)}\n"
            f"Supported: max_trade, slippage, activity, risk, size, holding, diversification")
        return
    if not params:
        await update.message.reply_text(
            "Provide at least one parameter\n"
            "Trading: /update_settings max_trade=1000 slippage=50\n"
            "Behavior: /update_settings activity=3 risk=2 size=3 holding=4 diversification=2")
        return

    # Get current values for any unspecified params (only needed for trading settings)
    api = _get_api()
    try:
        vault_data = await api.get_vault()
    except Exception as e:
        logger.warning(f"Failed to fetch current settings: {e}")
        vault_data = {}

    # Build update params (None means don't change)
    max_trade_bps = params.get('max_trade')
    slippage_bps = params.get('slippage')
    trading_activity = params.get('activity')
    asset_risk_preference = params.get('risk')
    trade_size = params.get('size')
    holding_style = params.get('holding')
    diversification = params.get('diversification')

    # Labels for display
    logger.info(f"Admin {update.effective_user.id} updating settings: {params}")
    result = await _get_contract().update_settings(
        max_trade_bps=max_trade_bps,
        slippage_bps=slippage_bps,
        trading_activity=trading_activity,
        asset_risk_preference=asset_risk_preference,
        trade_size=trade_size,
        holding_style=holding_style,
        diversification=diversification
    )

    if result.get("success"):
        tx_hash = result.get("transactionHash", "")
        # Build response message
        lines = ["Settings updated\n"]
        if max_trade_bps:
            lines.append(f"Max Trade: {max_trade_bps} BPS ({max_trade_bps/100:.1f}%)")
        if slippage_bps:
            lines.append(f"Slippage: {slippage_bps} BPS ({slippage_bps/100:.1f}%)")
        if trading_activity:
            lines.append(f"Activity: {trading_activity}")
        if asset_risk_preference:
            lines.append(f"Risk: {asset_risk_preference}")
        if trade_size:
            lines.append(f"Size: {trade_size}")
        if holding_style:
            lines.append(f"Holding: {holding_style}")
        if diversification:
            lines.append(f"Diversification: {diversification}")
        lines.append(f"\nTX: {tx_hash}")
        await update.message.reply_text("\n".join(lines))
    else:
        error = result.get("error", "Unknown error")
        await update.message.reply_text(f"Update failed: {error}")


async def cmd_deposit(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Deposit ETH to the vault."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("Unauthorized: Admin only")
        return

    args = ctx.args or []
    if len(args) == 0:
        await update.message.reply_text("Usage: /deposit <amount>")
        return

    # Parse amount
    try:
        amount_eth = float(args[0])
        if amount_eth <= 0:
            await update.message.reply_text("Amount must be greater than 0")
            return
        # Validate precision (max 6 decimal places for ETH)
        if '.' in args[0] and len(args[0].split('.')[-1]) > 6:
            await update.message.reply_text("Amount precision too high (max 6 decimals)")
            return
    except ValueError:
        await update.message.reply_text("Invalid amount format")
        return

    # Convert to Wei
    amount_wei = Web3.to_wei(amount_eth, 'ether')

    logger.info(f"Admin {update.effective_user.id} depositing {amount_eth} ETH")

    result = await _get_contract().deposit_eth(amount_wei)

    if result.get("success"):
        tx_hash = result.get("transactionHash", "")
        await update.message.reply_text(
            f"Deposited {amount_eth} ETH to Vault\n"
            f"TX: {tx_hash}"
        )
    else:
        error = result.get("error", "Unknown error")
        await update.message.reply_text(f"Deposit failed: {error}")
