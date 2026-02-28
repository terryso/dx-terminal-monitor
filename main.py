import asyncio
import logging
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes
from config import TELEGRAM_BOT_TOKEN, ALLOWED_USERS
from api import TerminalAPI

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

api = TerminalAPI()


def format_eth(wei: str) -> str:
    """将 Wei 转换为 ETH"""
    try:
        return f"{float(wei) / 1e18:.6f}"
    except:
        return wei


def format_usd(value) -> str:
    """格式化 USD"""
    try:
        return f"${float(value):.2f}"
    except:
        return str(value)


def format_percent(value) -> str:
    """格式化百分比"""
    try:
        sign = "+" if float(value) > 0 else ""
        return f"{sign}{float(value):.2f}%"
    except:
        return str(value)


def authorized(update: Update) -> bool:
    """检查用户是否有权限"""
    if not ALLOWED_USERS:
        return True
    return update.effective_user.id in ALLOWED_USERS


async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """显示帮助信息"""
    if not authorized(update):
        await update.message.reply_text("Unauthorized")
        return

    help_text = """
Terminal Markets Monitor

Commands:
/balance - 查看余额和持仓
/pnl - 查看 PnL 汇总
/positions - 查看持仓详情
/activity - 查看最近活动
/swaps - 查看最近交易
/strategies - 查看活跃策略
/vault - 查看 Vault 信息
/refresh - 刷新所有数据
"""
    await update.message.reply_text(help_text)


async def cmd_balance(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """查看余额"""
    if not authorized(update):
        return

    data = await api.get_positions()
    if "error" in data:
        await update.message.reply_text(f"Error: {data['error']}")
        return

    eth_balance = format_eth(data.get("ethBalance", "0"))
    total_value_usd = format_usd(data.get("overallValueUsd", "0"))
    total_pnl_usd = format_usd(data.get("overallPnlUsd", "0"))
    total_pnl_pct = format_percent(data.get("overallPnlPercent", "0"))

    msg = f"""
Balance Summary

ETH: {eth_balance} ETH
Total Value: {total_value_usd}
Total PnL: {total_pnl_usd} ({total_pnl_pct})
"""
    await update.message.reply_text(msg)


async def cmd_positions(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """查看持仓详情"""
    if not authorized(update):
        return

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
        symbol = p.get("tokenSymbol", "?")
        value_usd = format_usd(p.get("currentValueUsd", "0"))
        pnl_usd = format_usd(p.get("totalPnlUsd", "0"))
        pnl_pct = format_percent(p.get("totalPnlPercent", "0"))

        lines.append(f"{symbol}: {value_usd}")
        lines.append(f"  PnL: {pnl_usd} ({pnl_pct})\n")

    await update.message.reply_text("\n".join(lines))


async def cmd_pnl(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """查看 PnL"""
    if not authorized(update):
        return

    data = await api.get_positions()
    if "error" in data:
        await update.message.reply_text(f"Error: {data['error']}")
        return

    total_pnl_eth = format_eth(data.get("overallPnlEth", "0"))
    total_pnl_usd = format_usd(data.get("overallPnlUsd", "0"))
    total_pnl_pct = format_percent(data.get("overallPnlPercent", "0"))

    lines = [f"PnL Summary\n\nTotal: {total_pnl_usd} ({total_pnl_pct})\nETH: {total_pnl_eth} ETH\n\nBreakdown:"]

    for p in data.get("positions", []):
        symbol = p.get("tokenSymbol", "?")
        pnl_usd = format_usd(p.get("totalPnlUsd", "0"))
        pnl_pct = format_percent(p.get("totalPnlPercent", "0"))
        realized = format_usd(p.get("realizedPnlUsd", "0"))
        unrealized = format_usd(p.get("unrealizedPnlUsd", "0"))

        lines.append(f"\n{symbol}:")
        lines.append(f"  Total: {pnl_usd} ({pnl_pct})")
        lines.append(f"  Realized: {realized}")
        lines.append(f"  Unrealized: {unrealized}")

    await update.message.reply_text("\n".join(lines))


async def cmd_activity(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """查看最近活动"""
    if not authorized(update):
        return

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
        ts = item.get("timestamp", 0)

        if t == "swap":
            swap = item.get("swap", {})
            symbol = swap.get("tokenSymbol", "?")
            side = swap.get("side", "?")
            eth = format_eth(swap.get("ethAmount", "0"))
            lines.append(f"[Swap] {side.upper()} {symbol}: {eth} ETH")
        elif t == "deposit":
            dep = item.get("deposit", {})
            amt = format_eth(dep.get("amountWei", "0"))
            lines.append(f"[Deposit] {amt} ETH")
        elif t == "withdrawal":
            wit = item.get("withdrawal", {})
            amt = format_eth(wit.get("amountWei", "0"))
            lines.append(f"[Withdraw] {amt} ETH")

    await update.message.reply_text("\n".join(lines))


async def cmd_swaps(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """查看最近交易"""
    if not authorized(update):
        return

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
        symbol = s.get("tokenSymbol", "?")
        side = s.get("side", "?")
        eth = format_eth(s.get("ethAmount", "0"))
        price = s.get("effectivePriceUsd", "?")
        lines.append(f"{side.upper()} {symbol}")
        lines.append(f"  ETH: {eth}")
        lines.append(f"  Price: ${price}\n")

    await update.message.reply_text("\n".join(lines))


async def cmd_strategies(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """查看活跃策略"""
    if not authorized(update):
        return

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
        prio = s.get("strategyPriority", "?")
        content = s.get("content", "")[:100]

        lines.append(f"#{sid} [{prio.upper()}]")
        lines.append(f"  {content}...\n")

    await update.message.reply_text("\n".join(lines))


async def cmd_vault(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """查看 Vault 信息"""
    if not authorized(update):
        return

    data = await api.get_vault()
    if "error" in data:
        await update.message.reply_text(f"Error: {data['error']}")
        return

    msg = f"""
Vault Info

Address: {data.get('vaultAddress', '?')}
NFT: #{data.get('nftId', '?')} {data.get('nftName', '')}
Owner: {data.get('ownerAddress', '?')}
State: {data.get('state', '?')}
Paused: {data.get('paused', False)}

Settings:
  Max Trade: {int(data.get('maxTradeAmount', 0)) / 100}%
  Slippage: {int(data.get('slippageBps', 0)) / 100}%
"""
    await update.message.reply_text(msg)


async def cmd_refresh(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """刷新数据"""
    if not authorized(update):
        return

    await update.message.reply_text("Refreshing...")

    await cmd_balance(update, ctx)
    await cmd_pnl(update, ctx)


async def post_init(app: Application):
    """设置命令菜单"""
    commands = [
        BotCommand("start", "显示帮助"),
        BotCommand("balance", "查看余额"),
        BotCommand("pnl", "查看盈亏"),
        BotCommand("positions", "查看持仓"),
        BotCommand("activity", "最近活动"),
        BotCommand("swaps", "最近交易"),
        BotCommand("strategies", "活跃策略"),
        BotCommand("vault", "Vault 信息"),
        BotCommand("refresh", "刷新数据"),
    ]
    await app.bot.set_my_commands(commands)
    logger.info("Commands menu set")


def main():
    if not TELEGRAM_BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not set")
        return

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).post_init(post_init).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_start))
    app.add_handler(CommandHandler("balance", cmd_balance))
    app.add_handler(CommandHandler("pnl", cmd_pnl))
    app.add_handler(CommandHandler("positions", cmd_positions))
    app.add_handler(CommandHandler("activity", cmd_activity))
    app.add_handler(CommandHandler("swaps", cmd_swaps))
    app.add_handler(CommandHandler("strategies", cmd_strategies))
    app.add_handler(CommandHandler("vault", cmd_vault))
    app.add_handler(CommandHandler("refresh", cmd_refresh))

    logger.info("Bot starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
