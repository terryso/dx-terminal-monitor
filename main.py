import logging
import time
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.error import TimedOut, NetworkError, TelegramError
from config import TELEGRAM_BOT_TOKEN, ALLOWED_USERS
from api import TerminalAPI

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

api = TerminalAPI()


def format_eth(wei: str) -> str:
    try:
        return f"{float(wei) / 1e18:.6f}"
    except (ValueError, TypeError):
        return wei


def format_usd(value) -> str:
    try:
        return f"${float(value):.2f}"
    except (ValueError, TypeError):
        return str(value)


def format_percent(value) -> str:
    try:
        sign = "+" if float(value) > 0 else ""
        return f"{sign}{float(value):.2f}%"
    except (ValueError, TypeError):
        return str(value)


def authorized(update: Update) -> bool:
    if not ALLOWED_USERS:
        return True
    return update.effective_user.id in ALLOWED_USERS


async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
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
"""
    await update.message.reply_text(help_text)


async def cmd_balance(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not authorized(update):
        return
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
        sym = p.get("tokenSymbol", "?")
        val = format_usd(p.get("currentValueUsd", "0"))
        pnl = format_usd(p.get("totalPnlUsd", "0"))
        pct = format_percent(p.get("totalPnlPercent", "0"))
        lines.append(f"{sym}: {val}")
        lines.append(f"  PnL: {pnl} ({pct})\n")
    await update.message.reply_text("\n".join(lines))


async def cmd_pnl(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not authorized(update):
        return
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
        if t == "swap":
            s = item.get("swap", {})
            sym = s.get("tokenSymbol", "?")
            side = s.get("side", "?").upper()
            eth = format_eth(s.get("ethAmount", "0"))
            lines.append(f"[Swap] {side} {sym}: {eth} ETH")
        elif t == "deposit":
            d = item.get("deposit", {})
            amt = format_eth(d.get("amountWei", "0"))
            lines.append(f"[Deposit] {amt} ETH")
        elif t == "withdrawal":
            w = item.get("withdrawal", {})
            amt = format_eth(w.get("amountWei", "0"))
            lines.append(f"[Withdraw] {amt} ETH")
    await update.message.reply_text("\n".join(lines))


async def cmd_swaps(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
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
        sym = s.get("tokenSymbol", "?")
        side = s.get("side", "?").upper()
        eth = format_eth(s.get("ethAmount", "0"))
        price = s.get("effectivePriceUsd", "?")
        lines.append(f"{side} {sym}")
        lines.append(f"  ETH: {eth}")
        lines.append(f"  Price: ${price}\n")
    await update.message.reply_text("\n".join(lines))


async def cmd_strategies(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
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
        prio = s.get("strategyPriority", "?").upper()
        content = s.get("content", "")[:100]
        lines.append(f"#{sid} [{prio}]")
        lines.append(f"  {content}...\n")
    await update.message.reply_text("\n".join(lines))


async def cmd_vault(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
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


async def post_init(app: Application):
    commands = [
        BotCommand("start", "Help"),
        BotCommand("balance", "Balance"),
        BotCommand("pnl", "PnL"),
        BotCommand("positions", "Positions"),
        BotCommand("activity", "Activity"),
        BotCommand("swaps", "Swaps"),
        BotCommand("strategies", "Strategies"),
        BotCommand("vault", "Vault info"),
    ]
    await app.bot.set_my_commands(commands)
    logger.info("Commands menu set")


def main():
    import os
    # 禁用代理
    os.environ.pop('HTTP_PROXY', None)
    os.environ.pop('HTTPS_PROXY', None)
    os.environ.pop('ALL_PROXY', None)
    os.environ.pop('http_proxy', None)
    os.environ.pop('https_proxy', None)
    os.environ.pop('all_proxy', None)

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

    # 带自动重试的运行循环
    retry_count = 0
    max_retries = 10
    base_delay = 5  # 基础延迟秒数

    while retry_count < max_retries:
        try:
            logger.info(f"Bot starting... (attempt {retry_count + 1}/{max_retries})")
            app.run_polling(allowed_updates=Update.ALL_TYPES)
            # 如果正常退出，重置重试计数
            retry_count = 0
        except (TimedOut, NetworkError) as e:
            retry_count += 1
            delay = min(base_delay * (2 ** (retry_count - 1)), 300)  # 指数退避，最大5分钟
            logger.error(f"Network error: {e}. Retrying in {delay}s... ({retry_count}/{max_retries})")
            time.sleep(delay)
        except TelegramError as e:
            retry_count += 1
            delay = min(base_delay * retry_count, 60)
            logger.error(f"Telegram error: {e}. Retrying in {delay}s... ({retry_count}/{max_retries})")
            time.sleep(delay)
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
            break
        except Exception as e:
            retry_count += 1
            delay = min(base_delay * retry_count, 60)
            logger.error(f"Unexpected error: {e}. Retrying in {delay}s... ({retry_count}/{max_retries})")
            time.sleep(delay)

    if retry_count >= max_retries:
        logger.error(f"Max retries ({max_retries}) reached. Bot stopped.")


if __name__ == "__main__":
    main()
