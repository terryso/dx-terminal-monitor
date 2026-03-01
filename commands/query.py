"""Query commands module - read-only data query commands."""
from telegram import Update
from telegram.ext import ContextTypes

from utils.formatters import format_eth, format_percent, format_time, format_usd
from utils.permissions import authorized


def _get_api():
    """Lazy import api to avoid circular imports."""
    from main import api
    return api


async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Show help information."""
    if not authorized(update):
        await update.message.reply_text("Unauthorized")
        return
    help_text = """
Terminal Markets Monitor

Commands:
/balance - View balance
/pnl - View PnL
/positions - View positions
/activity - Recent activity
/swaps - Recent swaps
/strategies - Active strategies
/vault - Vault info
/add_strategy <text> - Add new strategy
/disable_strategy <id> - Disable a specific strategy
/disable_all - Disable all active strategies
/pause - Pause Agent trading
/resume - Resume Agent trading
/update_settings - Update vault settings
/withdraw <amount> - Withdraw ETH to wallet
/monitor_status - Check monitor status
/monitor_start - Start activity monitor
/monitor_stop - Stop activity monitor
"""
    await update.message.reply_text(help_text)


async def cmd_balance(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Query balance."""
    if not authorized(update):
        return
    api = _get_api()
    data = await api.get_positions()
    if "error" in data:
        await update.message.reply_text(f"Error: {data['error']}")
        return
    eth = format_eth(data.get("ethBalance", "0"))
    value = format_usd(data.get("overallValueUsd", "0"))
    pnl = format_usd(data.get("overallPnlUsd", "0"))
    pct = format_percent(data.get("overallPnlPercent", "0"))
    msg = f"""
Balance Summary

ETH: {eth} ETH
Total Value: {value}
Total PnL: {pnl} ({pct})
"""
    await update.message.reply_text(msg)


async def cmd_positions(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Query positions."""
    if not authorized(update):
        return
    api = _get_api()
    data = await api.get_positions()
    if "error" in data:
        await update.message.reply_text(f"Error: {data['error']}")
        return
    positions = data.get("positions", [])
    if not positions:
        await update.message.reply_text("No positions")
        return
    lines = ["Positions:\n"]
    for p in positions:
        sym = p.get("tokenSymbol", "?")
        val = format_usd(p.get("currentValueUsd", "0"))
        pnl = format_usd(p.get("totalPnlUsd", "0"))
        pct = format_percent(p.get("totalPnlPercent", "0"))
        lines.append(f"{sym}: {val}")
        lines.append(f"  PnL: {pnl} ({pct})\n")
    await update.message.reply_text("\n".join(lines))


async def cmd_pnl(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Query PnL."""
    if not authorized(update):
        return
    api = _get_api()
    data = await api.get_positions()
    if "error" in data:
        await update.message.reply_text(f"Error: {data['error']}")
        return
    total = format_usd(data.get("overallPnlUsd", "0"))
    pct = format_percent(data.get("overallPnlPercent", "0"))
    eth = format_eth(data.get("overallPnlEth", "0"))
    lines = [f"PnL Summary\n\nTotal: {total} ({pct})\nETH: {eth}\n\nBreakdown:"]
    for p in data.get("positions", []):
        sym = p.get("tokenSymbol", "?")
        pnl = format_usd(p.get("totalPnlUsd", "0"))
        pnl_pct = format_percent(p.get("totalPnlPercent", "0"))
        realized = format_usd(p.get("realizedPnlUsd", "0"))
        unrealized = format_usd(p.get("unrealizedPnlUsd", "0"))
        lines.append(f"\n{sym}:")
        lines.append(f"  Total: {pnl} ({pnl_pct})")
        lines.append(f"  Realized: {realized}")
        lines.append(f"  Unrealized: {unrealized}")
    await update.message.reply_text("\n".join(lines))


async def cmd_activity(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Query recent activity."""
    if not authorized(update):
        return
    api = _get_api()
    data = await api.get_activity(10)
    if "error" in data:
        await update.message.reply_text(f"Error: {data['error']}")
        return
    items = data.get("items", [])
    if not items:
        await update.message.reply_text("No recent activity")
        return
    lines = ["Recent Activity:\n"]
    for item in items[:5]:
        t = item.get("type", "?")
        ts = format_time(item.get("timestamp"))
        if t == "swap":
            s = item.get("swap", {})
            sym = s.get("tokenSymbol", "?")
            side = s.get("side", "?").upper()
            eth = format_eth(s.get("ethAmount", "0"))
            lines.append(f"[{ts}] Swap {side} {sym}: {eth} ETH")
        elif t == "deposit":
            d = item.get("deposit", {})
            amt = format_eth(d.get("amountWei", "0"))
            lines.append(f"[{ts}] Deposit {amt} ETH")
        elif t == "withdrawal":
            w = item.get("withdrawal", {})
            amt = format_eth(w.get("amountWei", "0"))
            lines.append(f"[{ts}] Withdraw {amt} ETH")
        elif t == "vault_summary":
            lines.append(f"[{ts}] Vault Summary")
    await update.message.reply_text("\n".join(lines))


async def cmd_swaps(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Query recent swaps."""
    if not authorized(update):
        return
    api = _get_api()
    data = await api.get_swaps(5)
    if "error" in data:
        await update.message.reply_text(f"Error: {data['error']}")
        return
    items = data.get("items", [])
    if not items:
        await update.message.reply_text("No swaps")
        return
    lines = ["Recent Swaps:\n"]
    for s in items:
        ts = format_time(s.get("timestamp"))
        sym = s.get("tokenSymbol", "?")
        side = s.get("side", "?").upper()
        eth = format_eth(s.get("ethAmount", "0"))
        price = s.get("effectivePriceUsd", "?")
        lines.append(f"[{ts}] {side} {sym}")
        lines.append(f"  ETH: {eth}")
        lines.append(f"  Price: ${price}\n")
    await update.message.reply_text("\n".join(lines))


async def cmd_strategies(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Query active strategies."""
    if not authorized(update):
        return
    api = _get_api()
    data = await api.get_strategies()
    if isinstance(data, dict) and "error" in data:
        await update.message.reply_text(f"Error: {data['error']}")
        return
    if not data:
        await update.message.reply_text("No active strategies")
        return
    lines = ["Active Strategies:\n"]
    for s in data:
        sid = s.get("strategyId", "?")
        prio = s.get("strategyPriority", "?").upper()
        content = s.get("content", "")[:100]
        lines.append(f"#{sid} [{prio}]")
        lines.append(f"  {content}...\n")
    await update.message.reply_text("\n".join(lines))


async def cmd_vault(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Query Vault info."""
    if not authorized(update):
        return
    api = _get_api()
    data = await api.get_vault()
    if "error" in data:
        await update.message.reply_text(f"Error: {data['error']}")
        return

    # Trading settings
    max_trade = int(data.get('maxTradeAmount', 0))
    slippage = int(data.get('slippageBps', 0))

    # Behavior preferences (0-4 scale labels)
    activity_labels = {0: "Very Low", 1: "Low", 2: "Medium", 3: "High", 4: "Very High"}
    risk_labels = {0: "Conservative", 1: "Moderate", 2: "Balanced", 3: "Growth", 4: "Aggressive"}
    size_labels = {0: "Tiny", 1: "Small", 2: "Medium", 3: "Large", 4: "Huge"}
    style_labels = {0: "Scalper", 1: "Day Trader", 2: "Swing", 3: "Position", 4: "HODL"}
    diversify_labels = {0: "Concentrated", 1: "Focused", 2: "Balanced", 3: "Diversified", 4: "Wide"}

    trading_activity = activity_labels.get(data.get('tradingActivity', 2), "Medium")
    risk_pref = risk_labels.get(data.get('assetRiskPreference', 2), "Balanced")
    trade_size = size_labels.get(data.get('tradeSize', 2), "Medium")
    holding_style = style_labels.get(data.get('holdingStyle', 2), "Swing")
    diversification = diversify_labels.get(data.get('diversification', 2), "Balanced")

    msg = f"""
Vault Info

Address: {data.get('vaultAddress', '?')}
NFT: #{data.get('nftId', '?')} {data.get('nftName', '')}
Owner: {data.get('ownerAddress', '?')}
State: {data.get('state', '?')}
Paused: {data.get('paused', False)}

Trading Settings:
  Max Trade: {max_trade} BPS ({max_trade/100:.1f}%)
  Slippage: {slippage} BPS ({slippage/100:.1f}%)

Behavior Preferences:
  Trading Activity: {trading_activity}
  Risk Preference: {risk_pref}
  Trade Size: {trade_size}
  Holding Style: {holding_style}
  Diversification: {diversification}
"""
    await update.message.reply_text(msg)
