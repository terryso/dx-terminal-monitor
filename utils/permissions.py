"""权限检查工具函数模块。"""

from telegram import Update

from config import ALLOWED_USERS


def authorized(update: Update) -> bool:
    """检查用户是否在允许列表中。"""
    if not ALLOWED_USERS:
        return True
    return update.effective_user.id in ALLOWED_USERS
