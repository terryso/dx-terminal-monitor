"""Commands module - centralized export of all command handlers and registration."""
from telegram.ext import CommandHandler

from .admin import (
    cmd_add_strategy,
    cmd_deposit,
    cmd_disable_all,
    cmd_disable_strategy,
    cmd_pause,
    cmd_resume,
    cmd_update_settings,
)
from .monitor import cmd_monitor_start, cmd_monitor_status, cmd_monitor_stop, set_monitor_instance
from .query import (
    cmd_activity,
    cmd_balance,
    cmd_deposits,
    cmd_pnl,
    cmd_pnl_history,
    cmd_positions,
    cmd_price,
    cmd_start,
    cmd_strategies,
    cmd_swaps,
    cmd_vault,
)
from .withdraw import create_withdraw_handler


def register_handlers(app):
    """Register all command handlers to Application."""
    # Query commands
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_start))
    app.add_handler(CommandHandler("balance", cmd_balance))
    app.add_handler(CommandHandler("positions", cmd_positions))
    app.add_handler(CommandHandler("pnl", cmd_pnl))
    app.add_handler(CommandHandler("activity", cmd_activity))
    app.add_handler(CommandHandler("swaps", cmd_swaps))
    app.add_handler(CommandHandler("strategies", cmd_strategies))
    app.add_handler(CommandHandler("vault", cmd_vault))
    app.add_handler(CommandHandler("deposits", cmd_deposits))
    app.add_handler(CommandHandler("pnl_history", cmd_pnl_history))
    app.add_handler(CommandHandler("price", cmd_price))

    # Admin commands
    app.add_handler(CommandHandler("add_strategy", cmd_add_strategy))
    app.add_handler(CommandHandler("deposit", cmd_deposit))
    app.add_handler(CommandHandler("disable_strategy", cmd_disable_strategy))
    app.add_handler(CommandHandler("disable_all", cmd_disable_all))
    app.add_handler(CommandHandler("pause", cmd_pause))
    app.add_handler(CommandHandler("resume", cmd_resume))
    app.add_handler(CommandHandler("update_settings", cmd_update_settings))

    # Monitor commands
    app.add_handler(CommandHandler("monitor_status", cmd_monitor_status))
    app.add_handler(CommandHandler("monitor_start", cmd_monitor_start))
    app.add_handler(CommandHandler("monitor_stop", cmd_monitor_stop))

    # Withdraw conversation handler
    app.add_handler(create_withdraw_handler())


__all__ = [
    'register_handlers',
    'set_monitor_instance',
    # Query commands
    'cmd_start',
    'cmd_balance',
    'cmd_positions',
    'cmd_pnl',
    'cmd_activity',
    'cmd_swaps',
    'cmd_strategies',
    'cmd_vault',
    'cmd_deposits',
    'cmd_pnl_history',
    'cmd_price',
    # Admin commands
    'cmd_add_strategy',
    'cmd_deposit',
    'cmd_disable_strategy',
    'cmd_disable_all',
    'cmd_pause',
    'cmd_resume',
    'cmd_update_settings',
    # Monitor commands
    'cmd_monitor_status',
    'cmd_monitor_start',
    'cmd_monitor_stop',
]
