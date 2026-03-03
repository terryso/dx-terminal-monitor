"""DX Terminal Monitor Bot 入口模块。"""
import asyncio
import logging
import time

from telegram import BotCommand, Update
from telegram.error import NetworkError, TelegramError, TimedOut
from telegram.ext import Application

from api import TerminalAPI
from commands import register_handlers, set_monitor_instance
from config import AUTO_START_MONITOR, TELEGRAM_BOT_TOKEN
from contract import VaultContract
from monitor import ActivityMonitor
from notifier import TelegramNotifier

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# 全局实例
api = TerminalAPI()
_contract_instance = None
_monitor_instance = None
_notifier_instance = None


def get_contract():
    """获取或创建合约实例。"""
    global _contract_instance
    if _contract_instance is None:
        _contract_instance = VaultContract()
    return _contract_instance


def set_contract(instance):
    """设置合约实例（用于测试）。"""
    global _contract_instance
    _contract_instance = instance


# 用于命令处理器 - 延迟调用 get_contract()
contract = get_contract


async def post_init(app: Application):
    """应用初始化后的回调。"""
    commands = [
        BotCommand("start", "Help"), BotCommand("balance", "Balance"), BotCommand("pnl", "PnL"),
        BotCommand("positions", "Positions"), BotCommand("activity", "Activity"), BotCommand("swaps", "Swaps"),
        BotCommand("strategies", "Strategies"), BotCommand("vault", "Vault info"),
        BotCommand("price", "ETH price"),
        BotCommand("token", "Token details"),
        BotCommand("tokens", "Tradeable tokens"),
        BotCommand("launches", "Upcoming token launches"),
        BotCommand("leaderboard", "Vault leaderboard"),
        BotCommand("deposits", "Deposits history"),
        BotCommand("pnl_history", "PnL trend history"),
        BotCommand("deposit", "Deposit ETH to vault"),
        BotCommand("add_strategy", "Add new strategy"), BotCommand("disable_strategy", "Disable strategy"),
        BotCommand("disable_all", "Disable all strategies"), BotCommand("pause", "Pause agent trading"),
        BotCommand("resume", "Resume agent trading"), BotCommand("update_settings", "Update vault settings"),
        BotCommand("withdraw", "Withdraw ETH to wallet"), BotCommand("monitor_status", "Check monitor status"),
        BotCommand("monitor_start", "Start activity monitor"), BotCommand("monitor_stop", "Stop activity monitor"),
    ]
    await app.bot.set_my_commands(commands)
    logger.info("Commands menu set")
    global _notifier_instance, _monitor_instance
    _notifier_instance = TelegramNotifier(app.bot)
    _monitor_instance = ActivityMonitor(api, _on_new_activity)
    set_monitor_instance(_monitor_instance)
    if AUTO_START_MONITOR:
        await _monitor_instance.start_background()
        logger.info("Activity monitor auto-started")
    else:
        logger.info("Activity monitor initialized but not started")


async def _on_new_activity(activity: dict):
    """ActivityMonitor 回调 - 发送 TG 通知。"""
    if _notifier_instance:
        await _notifier_instance.send_notification(activity)


def create_app():
    """创建并配置 Telegram 应用。"""
    app = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .post_init(post_init)
        .build()
    )
    register_handlers(app)
    return app


def main():
    """Bot 主入口。"""
    if not TELEGRAM_BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not set")
        return
    retry_count, max_retries, base_delay = 0, 10, 5
    while retry_count < max_retries:
        try:
            # 创建新的事件循环以避免 "Event loop is closed" 错误
            try:
                loop = asyncio.get_running_loop()
                loop.close()
            except RuntimeError:
                pass
            asyncio.set_event_loop(asyncio.new_event_loop())

            app = create_app()
            logger.info(f"Bot starting... (attempt {retry_count + 1}/{max_retries})")
            app.run_polling(allowed_updates=Update.ALL_TYPES)
            retry_count = 0
        except (TimedOut, NetworkError) as e:
            retry_count += 1
            delay = min(base_delay * (2 ** (retry_count - 1)), 300)
            logger.error(f"Network error: {e}. Retrying in {delay}s...")
            time.sleep(delay)
        except TelegramError as e:
            retry_count += 1
            delay = min(base_delay * retry_count, 60)
            logger.error(f"Telegram error: {e}. Retrying in {delay}s...")
            time.sleep(delay)
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
            break
        except Exception as e:
            retry_count += 1
            delay = min(base_delay * retry_count, 60)
            logger.error(f"Unexpected error: {e}. Retrying in {delay}s...")
            time.sleep(delay)
    if retry_count >= max_retries:
        logger.error(f"Max retries ({max_retries}) reached. Bot stopped.")


if __name__ == "__main__":
    main()
