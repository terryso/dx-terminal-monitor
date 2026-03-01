"""格式化工具函数模块。"""
from datetime import datetime, timezone


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
    """格式化 Unix 时间戳为可读时间（相对时间）。"""
    try:
        ts = int(timestamp)
        dt = datetime.fromtimestamp(ts, tz=timezone.utc)
        now = datetime.now(timezone.utc)
        diff = int((now - dt).total_seconds())

        if diff < 60:
            return f"{diff}s ago"
        elif diff < 3600:
            return f"{diff // 60}m ago"
        elif diff < 86400:
            return f"{diff // 3600}h ago"
        else:
            return dt.strftime("%m-%d %H:%M")
    except (ValueError, TypeError):
        return "?"
