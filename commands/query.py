"""Query commands module - read-only data query commands."""
from datetime import UTC

from telegram import Update
from telegram.ext import ContextTypes

from utils.formatters import (
    format_eth,
    format_large_number,
    format_percent,
    format_time,
    format_usd,
)
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
/pnl_history [days] - PnL trend history
/positions - View positions
/activity - Recent activity
/swaps - Recent swaps
/strategies - Active strategies
/vault - Vault info
/price - ETH price
/tokens - Tradeable tokens list
/token <symbol> - Token details
/deposits [limit] - Deposits/withdrawals history
/deposit <amount> - Deposit ETH to vault
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

    # Behavior preferences (raw values)
    trading_activity = data.get('tradingActivity', '?')
    risk_pref = data.get('assetRiskPreference', '?')
    trade_size = data.get('tradeSize', '?')
    holding_style = data.get('holdingStyle', '?')
    diversification = data.get('diversification', '?')

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


async def cmd_deposits(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Query deposits/withdrawals history."""
    if not authorized(update):
        return

    # Parse optional limit argument
    limit = 10
    if ctx.args and ctx.args[0].isdigit():
        limit = int(ctx.args[0])

    # Call API
    api = _get_api()
    data = await api.get_deposits_withdrawals(limit)

    # Handle API error
    if "error" in data:
        await update.message.reply_text(f"Error: {data['error']}")
        return

    # Get items list
    items = data.get("items", [])
    if not items:
        await update.message.reply_text("No deposit/withdrawal records")
        return

    # Format output (API returns: amount, type, blockNumber, transactionHash)
    lines = [f"Deposit/Withdrawal History (Last {len(items)}):\n"]
    for item in items:
        t = item.get("type", "?")
        amt = format_eth(item.get("amount", "0"))
        tx_hash = item.get("transactionHash", "")
        block = item.get("blockNumber", "?")

        if t == "deposit":
            lines.append(f"Deposit {amt} ETH")
        elif t == "withdrawal":
            lines.append(f"Withdraw {amt} ETH")
        else:
            lines.append(f"{t.upper()} {amt} ETH")

        lines.append(f"  Block: {block}")
        if tx_hash:
            lines.append(f"  Tx: {tx_hash[:16]}...\n")
        else:
            lines.append("")

    await update.message.reply_text("\n".join(lines))


async def cmd_pnl_history(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Query PnL trend history grouped by day."""
    if not authorized(update):
        return

    # Parse optional days argument (default 7, max 90 to avoid Telegram message limit)
    MAX_DAYS = 90
    days = 7
    if ctx.args and ctx.args[0].isdigit():
        requested = int(ctx.args[0])
        if requested > 0:
            days = min(requested, MAX_DAYS)

    # Call API
    api = _get_api()
    data = await api.get_pnl_history()

    # Handle API error
    if isinstance(data, dict) and "error" in data:
        await update.message.reply_text(f"Error: {data['error']}")
        return

    # Validate response type
    if not isinstance(data, list):
        await update.message.reply_text("Error: Unexpected API response format")
        return

    # Handle no records
    if not data:
        await update.message.reply_text("No PnL history available")
        return

    # Group records by day, taking the last record of each day (highest timestamp)
    from datetime import datetime

    daily_records = {}  # date_key -> (timestamp, item)
    for item in data:
        ts = item.get("timestamp")
        if ts is None:
            continue
        # Parse timestamp (Unix timestamp or ISO string)
        if isinstance(ts, (int, float)):
            dt = datetime.fromtimestamp(ts, tz=UTC)
        else:
            dt = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        date_key = dt.strftime("%Y-%m-%d")
        # Keep the record with highest timestamp for each day
        if date_key not in daily_records or ts > daily_records[date_key][0]:
            daily_records[date_key] = (ts, item)

    # Sort by date descending (newest first) and take last N days
    sorted_dates = sorted(daily_records.keys(), reverse=True)[:days]

    if not sorted_dates:
        await update.message.reply_text("No PnL history available")
        return

    # Format output
    lines = [f"PnL Trend (Last {len(sorted_dates)} days):\n"]

    for date_key in sorted_dates:
        _, item = daily_records[date_key]
        pnl_usd_val = item.get("pnlUsd", 0)
        pnl_eth_val = item.get("pnlEth", 0)

        # Handle both string and numeric values
        pnl_usd = format_usd(str(float(pnl_usd_val) if pnl_usd_val else 0))
        pnl_eth = format_eth(str(int(float(pnl_eth_val) if pnl_eth_val else 0)))

        lines.append(f"[{date_key}] {pnl_usd}")
        lines.append(f"  ETH: {pnl_eth}")

    # Show latest PnL as summary (first item = newest)
    _, latest = daily_records[sorted_dates[0]]
    latest_usd = format_usd(str(float(latest.get("pnlUsd", 0) or 0)))
    latest_eth = format_eth(str(int(float(latest.get("pnlEth", 0) or 0))))
    lines.append(f"\nLatest: {latest_usd}")
    lines.append(f"ETH: {latest_eth}")

    await update.message.reply_text("\n".join(lines))


async def cmd_price(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Query ETH price."""
    if not authorized(update):
        return
    api = _get_api()
    data = await api.get_eth_price()
    if "error" in data:
        await update.message.reply_text(f"Error: {data['error']}")
        return

    price = format_usd(data.get("priceUsd", "0"))

    msg = f"""
ETH Price

Current: {price}
"""
    await update.message.reply_text(msg)


async def cmd_tokens(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Query tradeable tokens list."""
    if not authorized(update):
        return

    # Parse optional page argument (default 1)
    page = 1
    if ctx.args and ctx.args[0].isdigit():
        page = max(1, int(ctx.args[0]))  # Ensure page >= 1

    # Call API
    api = _get_api()
    data = await api.get_tokens(page)

    # Handle API error
    if isinstance(data, dict) and "error" in data:
        await update.message.reply_text(f"Error: {data['error']}")
        return

    # Get items list - API may return list directly or dict with items
    if isinstance(data, list):
        items = data
        total = len(items)
    else:
        items = data.get("items", [])
        total = data.get("total", len(items))

    if not items:
        await update.message.reply_text("No tokens available")
        return

    # Calculate display range
    limit = 10
    start_num = (page - 1) * limit + 1
    end_num = min(page * limit, total)

    # Format output
    lines = [f"Tradeable Tokens ({start_num}-{end_num})\n"]
    for i, token in enumerate(items, 1):
        symbol = token.get("symbol", "?")
        name = token.get("name", "?")
        token_type = token.get("type", "unknown").replace("_", " ").title()
        lines.append(f"{i}. ${symbol} - {name}")
        lines.append(f"   Type: {token_type}\n")

    await update.message.reply_text("\n".join(lines))


async def cmd_token(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Query token details."""
    if not authorized(update):
        return

    # Check required argument
    if not ctx.args:
        await update.message.reply_text("Usage: /token <symbol>")
        return

    address = ctx.args[0]

    # Call API
    api = _get_api()
    data = await api.get_token(address)

    # Handle API error
    if "error" in data:
        await update.message.reply_text(f"Error: {data['error']}")
        return

    # Format output using actual API fields
    symbol = data.get("symbol", "?")
    name = data.get("name", "?")
    token_address = data.get("tokenAddress", "?")
    token_type = data.get("type", "unknown").replace("_", " ").title()
    description = data.get("description", "")[:100]
    if len(data.get("description", "")) > 100:
        description += "..."
    total_supply = format_large_number(data.get("totalSupply", "0"))

    msg = f"""
Token Details: ${symbol}

Name: {name}
Contract: {token_address}
Type: {token_type}
Total Supply: {total_supply}

{description}
"""
    await update.message.reply_text(msg)
