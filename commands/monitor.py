"""监控命令模块 - 监控服务控制命令。"""
import logging

from telegram import Update
from telegram.ext import ContextTypes

from config import is_admin

logger = logging.getLogger(__name__)

# Monitor instance (set by main.py via setter)
_monitor_instance = None


def set_monitor_instance(instance):
    """由 main.py 在 post_init 中调用，注入 monitor 实例。"""
    global _monitor_instance
    _monitor_instance = instance


async def cmd_monitor_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """查看监控服务状态。"""
    # Admin permission check
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("未授权: 仅管理员可查看监控状态")
        return

    # Check if monitor is initialized
    if _monitor_instance is None:
        await update.message.reply_text("监控服务未初始化")
        return

    # Get status
    status = "运行中" if _monitor_instance.running else "已停止"
    interval = _monitor_instance.poll_interval
    seen_count = len(_monitor_instance.seen_ids)

    await update.message.reply_text(
        f"监控服务状态\n\n"
        f"状态: {status}\n"
        f"轮询间隔: {interval} 秒\n"
        f"已处理活动: {seen_count} 个"
    )


async def cmd_monitor_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """启动监控服务。"""
    # Admin permission check
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("未授权: 仅管理员可启动监控")
        return

    # Check if monitor is initialized
    if _monitor_instance is None:
        await update.message.reply_text("监控服务未初始化，请重启 Bot")
        return

    # Check if already running
    if _monitor_instance.running:
        await update.message.reply_text("监控服务已在运行中")
        return

    # Start monitor
    await _monitor_instance.start_background()
    logger.info(f"Admin {update.effective_user.id} started activity monitor")

    await update.message.reply_text(
        f"监控服务已启动\n"
        f"轮询间隔: {_monitor_instance.poll_interval} 秒"
    )


async def cmd_monitor_stop(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """停止监控服务。"""
    # Admin permission check
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("未授权: 仅管理员可停止监控")
        return

    # Check if monitor is initialized
    if _monitor_instance is None:
        await update.message.reply_text("监控服务未初始化")
        return

    # Check if already stopped
    if not _monitor_instance.running:
        await update.message.reply_text("监控服务已处于停止状态")
        return

    # Stop monitor
    _monitor_instance.stop()
    logger.info(f"Admin {update.effective_user.id} stopped activity monitor")

    await update.message.reply_text("监控服务已停止")
