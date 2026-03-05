"""格式化工具函数模块。"""
from datetime import UTC, datetime


def format_eth(wei: str) -> str:
    """将 Wei 转换为 ETH 字符串。"""
    try:
        return f"{float(wei) / 1e18:.6f}"
    except (ValueError, TypeError):
        return wei


def format_usd(value) -> str:
    """格式化 USD 金额。"""
    try:
        return f"${float(value):.2f}"
    except (ValueError, TypeError):
        return str(value)


def format_percent(value) -> str:
    """格式化百分比，带正负号。"""
    try:
        v = float(value)
        sign = "+" if v > 0 else ""
        return f"{sign}{v:.2f}%"
    except (ValueError, TypeError):
        return str(value)


def format_time(timestamp) -> str:
    """格式化 Unix 时间戳为可读时间（带时区）。"""
    try:
        ts = int(timestamp)
        dt = datetime.fromtimestamp(ts, tz=UTC)
        return dt.strftime("%Y-%m-%d %H:%M UTC")
    except (ValueError, TypeError):
        return "?"


def format_large_number(value) -> str:
    """Format large numbers with B/M/K suffix."""
    try:
        v = float(value)
        if v >= 1e9:
            return f"${v/1e9:.1f}B"
        elif v >= 1e6:
            return f"${v/1e6:.1f}M"
        elif v >= 1e3:
            return f"${v/1e3:.1f}K"
        return f"${v:.2f}"
    except (ValueError, TypeError):
        return str(value)
