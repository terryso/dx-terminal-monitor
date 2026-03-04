"""DX Terminal Monitor Bot 入口模块。"""
import asyncio
import logging
import time

from telegram import BotCommand, Update
from telegram.error import NetworkError, TelegramError, TimedOut
from telegram.ext import Application

from advisor import StrategyAdvisor
from advisor_monitor import AdvisorMonitor
from api import TerminalAPI
from commands import register_handlers, set_monitor_instance
from config import (
    ADMIN_USERS,
    ADVISOR_ENABLED,
    ADVISOR_INTERVAL_HOURS,
    ALERT_ENABLED,
    AUTO_START_MONITOR,
    REPORT_ENABLED,
    TELEGRAM_BOT_TOKEN,
)
from contract import VaultContract
from llm import LLMClient
from monitor import ActivityMonitor
from notifier import TelegramNotifier
from reporter import DailyReporter

# Import alerter conditionally to avoid issues during testing
try:
    from alerter import ThresholdAlerter
except ImportError:
    ThresholdAlerter = None

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# 全局实例
api = TerminalAPI()
_contract_instance = None
_monitor_instance = None
_notifier_instance = None
_reporter_instance = None
_alerter_instance = None
_advisor_monitor_instance = None


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


def get_reporter():
    """获取 DailyReporter 实例。"""
    return _reporter_instance


def get_alerter():
    """获取 ThresholdAlerter 实例。"""
    return _alerter_instance


# 用于命令处理器 - 延迟调用 get_contract()
contract = get_contract


async def post_init(app: Application):
    """应用初始化后的回调。"""
    commands = [
        BotCommand("start", "Help"), BotCommand("balance", "Balance"), BotCommand("pnl", "PnL"),
        BotCommand("positions", "Positions"), BotCommand("activity", "Activity"), BotCommand("swaps", "Swaps"),
        BotCommand("strategies", "Strategies"), BotCommand("vault", "Vault info"),
        BotCommand("price", "ETH price"), BotCommand("token", "Token details"),
        BotCommand("tokens", "Tradeable tokens"), BotCommand("launches", "Upcoming token launches"),
        BotCommand("leaderboard", "Vault leaderboard"), BotCommand("tweets", "Token-related tweets"),
        BotCommand("deposits", "Deposits history"), BotCommand("pnl_history", "PnL trend history"),
        BotCommand("deposit", "Deposit ETH to vault"), BotCommand("add_strategy", "Add new strategy"),
        BotCommand("disable_strategy", "Disable strategy"), BotCommand("disable_all", "Disable all strategies"),
        BotCommand("pause", "Pause agent trading"), BotCommand("resume", "Resume agent trading"),
        BotCommand("update_settings", "Update vault settings"), BotCommand("withdraw", "Withdraw ETH to wallet"),
        BotCommand("monitor_status", "Check monitor status"), BotCommand("monitor_start", "Start activity monitor"),
        BotCommand("monitor_stop", "Stop activity monitor"), BotCommand("report_on", "Enable daily report"),
        BotCommand("report_off", "Disable daily report"), BotCommand("report_time", "Set report time"),
        BotCommand("report_status", "Show report settings"),
        BotCommand("alert_pnl", "Set PnL alert threshold"),
        BotCommand("alert_position", "Set position alert threshold"),
        BotCommand("alert_status", "Show alert settings"),
        BotCommand("advisor_on", "Enable AI advisor"),
        BotCommand("advisor_off", "Disable AI advisor"),
        BotCommand("advisor_status", "AI advisor status"),
    ]
    await app.bot.set_my_commands(commands)
    logger.info("Commands menu set")
    global _notifier_instance, _monitor_instance, _reporter_instance, _alerter_instance, _advisor_monitor_instance
    _notifier_instance = TelegramNotifier(app.bot)
    _monitor_instance = ActivityMonitor(api, _on_new_activity)
    set_monitor_instance(_monitor_instance)
    if AUTO_START_MONITOR:
        await _monitor_instance.start_background()
        logger.info("Activity monitor auto-started")
    _reporter_instance = DailyReporter(api, _notifier_instance)
    if REPORT_ENABLED:
        await _reporter_instance.start_background()
        logger.info(f"Daily reporter started ({_reporter_instance.report_time[0]:02d}:{_reporter_instance.report_time[1]:02d} UTC)")
    # Initialize threshold alerter
    if ThresholdAlerter is not None:
        _alerter_instance = ThresholdAlerter(api, _notifier_instance)
        if ALERT_ENABLED:
            await _alerter_instance.start_background()
            logger.info(f"Threshold alerter started (PnL: {_alerter_instance.pnl_threshold}%, Position: {_alerter_instance.position_threshold}%)")
    # Initialize AI strategy advisor
    if ADVISOR_ENABLED:
        from telegram.ext import CallbackQueryHandler

        from advisor_monitor import push_suggestions
        from commands.advisor import set_advisor_monitor

        llm = LLMClient()
        advisor = StrategyAdvisor(llm, api)
        admin_chat_id = ADMIN_USERS[0] if ADMIN_USERS else None
        if admin_chat_id:
            _advisor_monitor_instance = AdvisorMonitor(
                advisor, api, push_suggestions, admin_chat_id, ADVISOR_INTERVAL_HOURS
            )
            set_advisor_monitor(_advisor_monitor_instance)
            # Register callback handler for inline keyboard
            from commands.advisor import handle_advisor_callback
            app.add_handler(CallbackQueryHandler(handle_advisor_callback, pattern=r"^adv:"))
            await _advisor_monitor_instance.start_background()
            logger.info(f"Advisor monitor started ({ADVISOR_INTERVAL_HOURS}h interval)")


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
            try:
                asyncio.get_running_loop().close()
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
        except (TelegramError, Exception) as e:
            retry_count += 1
            delay = min(base_delay * retry_count, 60)
            logger.error(f"Error: {e}. Retrying in {delay}s...")
            time.sleep(delay)
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
            break
    if retry_count >= max_retries:
        logger.error(f"Max retries ({max_retries}) reached. Bot stopped.")


if __name__ == "__main__":
    main()
