import logging
import re
import time
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.error import TimedOut, NetworkError, TelegramError
from config import TELEGRAM_BOT_TOKEN, ALLOWED_USERS, is_admin
from api import TerminalAPI
from contract import VaultContract

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

api = TerminalAPI()

# Contract instance - can be mocked for testing
_contract_instance = None


def get_contract():
    """Get or create the contract instance."""
    global _contract_instance
    if _contract_instance is None:
        _contract_instance = VaultContract()
    return _contract_instance


def set_contract(instance):
    """Set contract instance (for testing)."""
    global _contract_instance
    _contract_instance = instance


# For use in command handlers - calls get_contract() lazily
contract = get_contract


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
/add_strategy <text> - Add new strategy
/disable_strategy <id> - Disable a specific strategy
/disable_all - Disable all active strategies
/pause - Pause Agent trading
/resume - Resume Agent trading
/update_settings - Update vault settings
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
        BotCommand("add_strategy", "Add new strategy"),
        BotCommand("disable_strategy", "Disable strategy"),
        BotCommand("disable_all", "Disable all strategies"),
        BotCommand("pause", "Pause agent trading"),
        BotCommand("resume", "Resume agent trading"),
        BotCommand("update_settings", "Update vault settings"),
    ]
    await app.bot.set_my_commands(commands)
    logger.info("Commands menu set")


async def cmd_disable_strategy(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not authorized(update):
        await update.message.reply_text("未授权")
        return

    args = ctx.args or []
    if len(args) == 0:
        await update.message.reply_text("用法: /disable_strategy <id>")
        return

    try:
        strategy_id = int(args[0])
    except ValueError:
        await update.message.reply_text("错误: 策略 ID 必须是数字")
        return

    result = await contract().disable_strategy(strategy_id)

    if result.get("success"):
        tx_hash = result.get("transactionHash", "")
        await update.message.reply_text(f"策略 #{strategy_id} 已禁用，交易哈希: {tx_hash}")
    else:
        error = result.get("error", "未知错误")
        if "doesn't exist" in error.lower() or "not active" in error.lower():
            await update.message.reply_text(f"策略 #{strategy_id} 不存在或已禁用")
        else:
            await update.message.reply_text(f"交易失败: {error}")


async def cmd_disable_all(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Disable all active strategies."""
    if not authorized(update):
        await update.message.reply_text("未授权")
        return

    # Define callback to get active strategy count from API
    async def get_active_count() -> int:
        data = await api.get_strategies()
        if isinstance(data, dict) and "error" in data:
            logger.warning(f"Failed to fetch strategies: {data['error']}")
            return -1
        return len(data) if data else 0

    result = await contract().disable_all_strategies(get_active_count)

    if result.get("success"):
        disabled_count = result.get("disabledCount", -1)
        if result.get("message") == "no_active_strategies" or disabled_count == 0:
            await update.message.reply_text("没有活跃策略")
        elif disabled_count == -1:
            tx_hash = result.get("transactionHash", "")
            await update.message.reply_text(f"已禁用所有策略，交易哈希: {tx_hash}")
        else:
            tx_hash = result.get("transactionHash", "")
            await update.message.reply_text(f"已禁用 {disabled_count} 个策略，交易哈希: {tx_hash}")
    else:
        error = result.get("error", "未知错误")
        await update.message.reply_text(f"交易失败: {error}")


async def cmd_add_strategy(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Add a new trading strategy."""
    # Admin permission check (high-risk operation)
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("未授权: 仅管理员可添加策略")
        return

    # Parse arguments
    args = ctx.args or []
    if len(args) == 0:
        await update.message.reply_text("用法: /add_strategy <策略内容>")
        return

    # Join all arguments as strategy content
    content = " ".join(args)

    # Input validation: check for empty content
    if not content.strip():
        await update.message.reply_text("错误: 策略内容不能为空")
        return

    # Input validation: check content length limit
    MAX_STRATEGY_LENGTH = 500
    if len(content) > MAX_STRATEGY_LENGTH:
        await update.message.reply_text(f"错误: 策略内容过长（最多 {MAX_STRATEGY_LENGTH} 字符）")
        return

    # Log admin action for audit
    logger.info(f"Admin {update.effective_user.id} adding strategy: {content[:50]}...")

    # Call contract (using default parameters: expiry=0, priority=1)
    result = await contract().add_strategy(content)

    # Handle response
    if result.get("success"):
        strategy_id = result.get("strategyId")
        tx_hash = result.get("transactionHash", "")
        # Handle case where strategyId parsing failed
        if strategy_id is None:
            await update.message.reply_text(
                f"策略已添加，但无法解析策略 ID\n交易哈希: {tx_hash}\n请查看交易详情获取策略 ID"
            )
        else:
            await update.message.reply_text(
                f"策略已添加，ID: #{strategy_id}\n交易哈希: {tx_hash}"
            )
    else:
        error = result.get("error", "未知错误")
        # Check if it's a strategy limit error
        if "max" in error.lower() or "limit" in error.lower() or "8" in error:
            await update.message.reply_text("错误: 已达到策略数量上限 (最多 8 个)")
        else:
            await update.message.reply_text(f"添加失败: {error}")


async def cmd_pause(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Pause agent trading."""
    # Admin permission check (high-risk operation)
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("未授权: 仅管理员可暂停交易")
        return

    # Pre-check: verify vault is not already paused
    vault_data = await api.get_vault()
    if isinstance(vault_data, dict) and vault_data.get("paused") is True:
        await update.message.reply_text("Agent 已经处于暂停状态")
        return

    # Log admin action for audit
    logger.info(f"Admin {update.effective_user.id} pausing vault")

    # Call contract
    result = await contract().pause_vault(True)

    # Handle response
    if result.get("success"):
        tx_hash = result.get("transactionHash", "")
        await update.message.reply_text(
            f"⏸️ Agent 已暂停，将不会执行任何交易\n交易哈希: {tx_hash}"
        )
    else:
        error = result.get("error", "未知错误")
        await update.message.reply_text(f"暂停失败: {error}")


async def cmd_resume(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Resume agent trading."""
    # Admin permission check (high-risk operation)
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("未授权: 仅管理员可恢复交易")
        return

    # Pre-check: verify vault is currently paused
    vault_data = await api.get_vault()
    if isinstance(vault_data, dict) and vault_data.get("paused") is False:
        await update.message.reply_text("Agent 已经处于运行状态")
        return

    # Log admin action for audit
    logger.info(f"Admin {update.effective_user.id} resuming vault")

    # Call contract
    result = await contract().pause_vault(False)

    # Handle response
    if result.get("success"):
        tx_hash = result.get("transactionHash", "")
        await update.message.reply_text(
            f"▶️ Agent 已恢复，将继续执行交易\n交易哈希: {tx_hash}"
        )
    else:
        error = result.get("error", "未知错误")
        await update.message.reply_text(f"恢复失败: {error}")


async def cmd_update_settings(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Update vault trading settings."""
    # Admin permission check (high-risk operation)
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("未授权: 仅管理员可更新设置")
        return

    # Parse arguments
    args = ctx.args or []
    if len(args) == 0:
        await update.message.reply_text(
            "用法: /update_settings max_trade=1000 slippage=50\n"
            "参数说明:\n"
            "  max_trade: 最大交易金额 (BPS, 500-10000, 如 1000=10%)\n"
            "  slippage: 滑点容忍度 (BPS, 10-5000, 如 50=0.5%)"
        )
        return

    # Parse key=value parameters
    params = {}
    for arg in args:
        match = re.match(r'(\w+)=(\d+)', arg)
        if match:
            key, value = match.groups()
            params[key] = int(value)

    # Validate supported parameters
    valid_keys = {'max_trade', 'slippage'}
    invalid_keys = set(params.keys()) - valid_keys
    if invalid_keys:
        await update.message.reply_text(
            f"未知参数: {', '.join(invalid_keys)}\n"
            f"支持的参数: max_trade, slippage"
        )
        return

    # Check if at least one parameter is provided
    if not params:
        await update.message.reply_text(
            "请至少提供一个参数\n用法: /update_settings max_trade=1000 slippage=50"
        )
        return

    # Get current settings (as default values for unspecified parameters)
    try:
        vault_data = await api.get_vault()
        current_max_trade = int(vault_data.get('maxTradeAmount', 1000))
        current_slippage = int(vault_data.get('slippageBps', 50))
    except Exception as e:
        logger.warning(f"Failed to fetch current settings: {e}")
        # Use default values
        current_max_trade = 1000
        current_slippage = 50

    # Use provided or current values
    max_trade_bps = params.get('max_trade', current_max_trade)
    slippage_bps = params.get('slippage', current_slippage)

    # Log admin action for audit
    logger.info(
        f"Admin {update.effective_user.id} updating settings: "
        f"max_trade={max_trade_bps}, slippage={slippage_bps}"
    )

    # Call contract
    result = await contract().update_settings(max_trade_bps, slippage_bps)

    # Handle response
    if result.get("success"):
        tx_hash = result.get("transactionHash", "")
        await update.message.reply_text(
            f"✅ 设置已更新\n"
            f"max_trade: {max_trade_bps} BPS ({max_trade_bps/100:.1f}%)\n"
            f"slippage: {slippage_bps} BPS ({slippage_bps/100:.1f}%)\n"
            f"交易哈希: {tx_hash}"
        )
    else:
        error = result.get("error", "未知错误")
        await update.message.reply_text(f"更新失败: {error}")


def create_app():
    """Create and configure the Telegram application."""
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
    app.add_handler(CommandHandler("add_strategy", cmd_add_strategy))
    app.add_handler(CommandHandler("disable_strategy", cmd_disable_strategy))
    app.add_handler(CommandHandler("disable_all", cmd_disable_all))
    app.add_handler(CommandHandler("pause", cmd_pause))
    app.add_handler(CommandHandler("resume", cmd_resume))
    app.add_handler(CommandHandler("update_settings", cmd_update_settings))
    return app


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

    # 带自动重试的运行循环
    retry_count = 0
    max_retries = 10
    base_delay = 5  # 基础延迟秒数

    while retry_count < max_retries:
        try:
            # 每次重试都创建新的 Application 实例，避免事件循环已关闭的问题
            app = create_app()
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
