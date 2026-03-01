"""管理命令模块 - 需要管理员权限的写入操作。"""
import logging
import re
from telegram import Update
from telegram.ext import ContextTypes
from config import is_admin
from utils.formatters import format_eth, format_usd

logger = logging.getLogger(__name__)


def _get_api():
    """延迟导入 api 避免循环导入。"""
    from main import api
    return api


def _get_contract():
    """延迟导入 contract 避免循环导入。"""
    from main import contract
    return contract()


async def cmd_disable_strategy(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """禁用单个策略。"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("未授权: 仅管理员可禁用策略")
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
    result = await _get_contract().disable_strategy(strategy_id)
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
    """禁用所有活跃策略。"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("未授权: 仅管理员可禁用策略")
        return
    api = _get_api()
    async def get_active_count() -> int:
        data = await api.get_strategies()
        if isinstance(data, dict) and "error" in data:
            logger.warning(f"Failed to fetch strategies: {data['error']}")
            return -1
        return len(data) if data else 0
    result = await _get_contract().disable_all_strategies(get_active_count)
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
    """添加新交易策略。"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("未授权: 仅管理员可添加策略")
        return
    args = ctx.args or []
    if len(args) == 0:
        await update.message.reply_text("用法: /add_strategy <策略内容>")
        return
    content = " ".join(args)
    if not content.strip():
        await update.message.reply_text("错误: 策略内容不能为空")
        return
    MAX_STRATEGY_LENGTH = 500
    if len(content) > MAX_STRATEGY_LENGTH:
        await update.message.reply_text(f"错误: 策略内容过长（最多 {MAX_STRATEGY_LENGTH} 字符）")
        return
    logger.info(f"Admin {update.effective_user.id} adding strategy: {content[:50]}...")
    result = await _get_contract().add_strategy(content)
    if result.get("success"):
        strategy_id = result.get("strategyId")
        tx_hash = result.get("transactionHash", "")
        if strategy_id is None:
            await update.message.reply_text(
                f"策略已添加，但无法解析策略 ID\n交易哈希: {tx_hash}\n请查看交易详情获取策略 ID")
        else:
            await update.message.reply_text(f"策略已添加，ID: #{strategy_id}\n交易哈希: {tx_hash}")
    else:
        error = result.get("error", "未知错误")
        if "max" in error.lower() or "limit" in error.lower() or "8" in error:
            await update.message.reply_text("错误: 已达到策略数量上限 (最多 8 个)")
        else:
            await update.message.reply_text(f"添加失败: {error}")


async def cmd_pause(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """暂停 Agent 交易。"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("未授权: 仅管理员可暂停交易")
        return
    api = _get_api()
    vault_data = await api.get_vault()
    if isinstance(vault_data, dict) and vault_data.get("paused") is True:
        await update.message.reply_text("Agent 已经处于暂停状态")
        return
    logger.info(f"Admin {update.effective_user.id} pausing vault")
    result = await _get_contract().pause_vault(True)
    if result.get("success"):
        tx_hash = result.get("transactionHash", "")
        await update.message.reply_text(f"Agent 已暂停，将不会执行任何交易\n交易哈希: {tx_hash}")
    else:
        error = result.get("error", "未知错误")
        await update.message.reply_text(f"暂停失败: {error}")


async def cmd_resume(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """恢复 Agent 交易。"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("未授权: 仅管理员可恢复交易")
        return
    api = _get_api()
    vault_data = await api.get_vault()
    if isinstance(vault_data, dict) and vault_data.get("paused") is False:
        await update.message.reply_text("Agent 已经处于运行状态")
        return
    logger.info(f"Admin {update.effective_user.id} resuming vault")
    result = await _get_contract().pause_vault(False)
    if result.get("success"):
        tx_hash = result.get("transactionHash", "")
        await update.message.reply_text(f"Agent 已恢复，将继续执行交易\n交易哈希: {tx_hash}")
    else:
        error = result.get("error", "未知错误")
        await update.message.reply_text(f"恢复失败: {error}")


async def cmd_update_settings(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """更新 Vault 交易设置。"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("未授权: 仅管理员可更新设置")
        return
    args = ctx.args or []
    if len(args) == 0:
        await update.message.reply_text(
            "用法: /update_settings max_trade=1000 slippage=50\n"
            "参数说明:\n"
            "  max_trade: 最大交易金额 (BPS, 500-10000, 如 1000=10%)\n"
            "  slippage: 滑点容忍度 (BPS, 10-5000, 如 50=0.5%)")
        return
    params = {}
    for arg in args:
        match = re.match(r'(\w+)=(\d+)', arg)
        if match:
            key, value = match.groups()
            params[key] = int(value)
    valid_keys = {'max_trade', 'slippage'}
    invalid_keys = set(params.keys()) - valid_keys
    if invalid_keys:
        await update.message.reply_text(
            f"未知参数: {', '.join(invalid_keys)}\n支持的参数: max_trade, slippage")
        return
    if not params:
        await update.message.reply_text("请至少提供一个参数\n用法: /update_settings max_trade=1000 slippage=50")
        return
    api = _get_api()
    try:
        vault_data = await api.get_vault()
        current_max_trade = int(vault_data.get('maxTradeAmount', 1000))
        current_slippage = int(vault_data.get('slippageBps', 50))
    except Exception as e:
        logger.warning(f"Failed to fetch current settings: {e}")
        current_max_trade = 1000
        current_slippage = 50
    max_trade_bps = params.get('max_trade', current_max_trade)
    slippage_bps = params.get('slippage', current_slippage)
    logger.info(f"Admin {update.effective_user.id} updating settings: max_trade={max_trade_bps}, slippage={slippage_bps}")
    result = await _get_contract().update_settings(max_trade_bps, slippage_bps)
    if result.get("success"):
        tx_hash = result.get("transactionHash", "")
        await update.message.reply_text(
            f"设置已更新\n"
            f"max_trade: {max_trade_bps} BPS ({max_trade_bps/100:.1f}%)\n"
            f"slippage: {slippage_bps} BPS ({slippage_bps/100:.1f}%)\n"
            f"交易哈希: {tx_hash}")
    else:
        error = result.get("error", "未知错误")
        await update.message.reply_text(f"更新失败: {error}")
