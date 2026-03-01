"""工具函数模块。"""
from collections.abc import Callable
from typing import Any

from telegram import Update

from .formatters import format_eth, format_percent, format_time, format_usd
from .permissions import authorized

# Type annotations for exported functions
format_eth: Callable[[str], str]
format_usd: Callable[[Any], str]
format_percent: Callable[[Any], str]
format_time: Callable[[Any], str]
authorized: Callable[[Update], bool]

__all__ = ['format_eth', 'format_usd', 'format_percent', 'format_time', 'authorized']
