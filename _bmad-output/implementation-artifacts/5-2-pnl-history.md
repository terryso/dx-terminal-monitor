# Story 5.2: PnL 趋势历史查询

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

作为**用户**,我需要**通过 `/pnl_history` 命令查看 PnL 变化趋势**,以便**分析盈亏历史**。

## Acceptance Criteria

1. 在 `commands/query.py` 添加 `cmd_pnl_history` 命令处理函数
2. 调用现有 `api.get_pnl_history()` 方法
3. 格式化输出: 时间、PnL USD、PnL ETH、变化百分比
4. 默认显示最近 7 天数据
5. 支持参数指定天数: `/pnl_history 30`
6. 添加单元测试

## Tasks / Subtasks

- [x] **Task 1: 实现 cmd_pnl_history 命令处理函数** (AC: #1, #2, #3, #4, #5)
  - [x] 在 `commands/query.py` 中添加 `cmd_pnl_history` 异步函数
  - [x] 使用 `authorized()` 检查用户权限
  - [x] 解析可选参数 `ctx.args` 获取天数 (默认 7)
  - [x] 调用 `api.get_pnl_history()` 获取数据
  - [x] 处理 API 错误响应
  - [x] 格式化输出消息:
    - 时间戳 (使用 `format_time`)
    - PnL USD (使用 `format_usd`)
    - PnL ETH (使用 `format_eth`)
    - 变化百分比 (使用 `format_percent`)
  - [x] 处理无记录的情况
  - [x] 计算并显示总计

- [x] **Task 2: 更新命令注册和菜单** (AC: #1)
  - [x] 在 `commands/__init__.py` 中导出 `cmd_pnl_history`
  - [x] 在 `register_handlers()` 中添加 `CommandHandler("pnl_history", cmd_pnl_history)`
  - [x] 在 `main.py` 的 `post_init()` 中添加 `BotCommand("pnl_history", "PnL trend history")`
  - [x] 在 `cmd_start` 帮助文本中添加 `/pnl_history` 命令说明

- [x] **Task 3: 添加单元测试** (AC: #6)
  - [x] 创建 `tests/unit/test_story_5_2_pnl_history.py`
  - [x] 测试正常查询 (默认 7 天)
  - [x] 测试自定义天数查询
  - [x] 测试无记录情况
  - [x] 测试 API 错误处理
  - [x] 测试未授权用户拒绝

## Dev Notes

### 技术栈要求

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | >=3.12 | 主要开发语言 |
| python-telegram-bot | >=21.0 | Telegram Bot API |
| pytest | >=8.0 | 测试框架 |
| pytest-asyncio | >=0.23 | 异步测试支持 |

### 现有代码依赖

**api.py - get_pnl_history (已实现):**
```python
# api.py:27-29
async def get_pnl_history(self) -> list:
    """获取 PnL 历史"""
    return await self._get(f"/pnl-history/{self.vault}")
```

**utils/formatters.py (已实现):**
```python
# 格式化函数
def format_eth(wei: str | int) -> str  # Wei 转 ETH
def format_time(timestamp: str) -> str  # ISO 时间转可读格式
def format_usd(value: str) -> str       # USD 格式化
def format_percent(value) -> str        # 百分比格式化（带正负号）
```

**utils/permissions.py (已实现):**
```python
def authorized(update: Update) -> bool  # 检查用户是否在允许列表中
```

### 新增代码实现指南

**commands/query.py - cmd_pnl_history 命令:**
```python
async def cmd_pnl_history(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """查询 PnL 趋势历史。"""
    if not authorized(update):
        return

    # 解析可选参数（天数）
    days = 7
    if ctx.args and ctx.args[0].isdigit():
        days = int(ctx.args[0])

    # 调用 API
    api = _get_api()
    data = await api.get_pnl_history()

    # 错误处理
    if isinstance(data, dict) and "error" in data:
        await update.message.reply_text(f"Error: {data['error']}")
        return

    # 获取记录列表
    if not data:
        await update.message.reply_text("No PnL history available")
        return

    # 限制显示天数
    items = data[:days] if len(data) > days else data

    # 格式化输出
    lines = [f"PnL Trend (Last {len(items)} days):\n"]

    total_usd = 0.0
    total_eth = 0.0

    for item in items:
        ts = format_time(item.get("timestamp"))
        pnl_usd = format_usd(item.get("pnlUsd", "0"))
        pnl_eth = format_eth(item.get("pnlEth", "0"))
        pnl_pct = format_percent(item.get("pnlPercent", "0"))

        lines.append(f"[{ts}] {pnl_usd} ({pnl_pct})")
        lines.append(f"  ETH: {pnl_eth}")

        # 累计总计
        try:
            total_usd += float(item.get("pnlUsd", 0))
            total_eth += float(item.get("pnlEth", 0)) / 1e18  # 如果是 wei
        except (ValueError, TypeError):
            pass

    # 添加总计
    total_pct = format_percent((total_usd / 10000) * 100) if total_usd else "0.00%"  # 假设基准
    lines.append(f"\nTotal: {format_usd(str(total_usd))} ({total_pct})")
    lines.append(f"ETH: {format_eth(str(int(total_eth * 1e18)))}")

    await update.message.reply_text("\n".join(lines))
```

**commands/__init__.py - 更新导出:**
```python
from .query import (
    cmd_activity,
    cmd_balance,
    cmd_deposits,
    cmd_pnl,
    cmd_pnl_history,  # 新增
    cmd_positions,
    cmd_start,
    cmd_strategies,
    cmd_swaps,
    cmd_vault,
)

def register_handlers(app):
    # Query commands
    # ...existing handlers...
    app.add_handler(CommandHandler("pnl_history", cmd_pnl_history))  # 新增

__all__ = [
    # ...
    'cmd_pnl_history',  # 新增
]
```

**main.py - post_init 更新:**
```python
async def post_init(app: Application):
    commands = [
        # ...existing commands...
        BotCommand("pnl_history", "PnL trend history"),  # 新增
    ]
```

**commands/query.py - cmd_start 更新:**
```python
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    help_text = """
Terminal Markets Monitor

Commands:
/balance - View balance
/pnl - View PnL
/pnl_history [days] - PnL trend history  # 新增
/positions - View positions
/activity - Recent activity
/swaps - Recent swaps
/strategies - Active strategies
/vault - Vault info
/deposits [limit] - Deposits history
...
"""
```

### Project Structure Notes

**修改文件:**
```
dx-terminal-monitor/
├── main.py              # 修改 - 添加 BotCommand
└── commands/
    ├── __init__.py      # 修改 - 导出和注册 cmd_pnl_history
    └── query.py         # 修改 - 添加 cmd_pnl_history 函数
```

**新增测试文件:**
```
tests/
└── unit/
    └── test_story_5_2_pnl_history.py  # 新增
```

### 与其他 Story 的关系

**前置依赖:**
- **api.py** - 提供了 `get_pnl_history()` 方法
- **utils/formatters.py** - 提供了 `format_eth()`, `format_usd()`, `format_percent()`, `format_time()` 格式化函数
- **utils/permissions.py** - 提供了 `authorized()` 权限检查

**功能关系:**
```
Epic 5: 资金查询与历史数据
    ├── Story 5.1: 存取款历史查询 - 仅依赖 api.py (已完成)
    ├── Story 5.2: PnL 趋势历史 (本 Story) - 仅依赖 api.py
    └── Story 5.3: 存入 ETH - 依赖 Epic 1 (contract.py)
```

### API 响应格式参考

根据 Terminal Markets API，`/pnl-history/{vault}` 返回格式:
```json
[
    {
        "timestamp": "1709251200",
        "pnlUsd": "120.50",
        "pnlEth": "40000000000000000",
        "pnlPercent": "2.1"
    },
    {
        "timestamp": "1709164800",
        "pnlUsd": "-45.20",
        "pnlEth": "-15000000000000000",
        "pnlPercent": "-0.8"
    }
]
```

### 测试策略

**单元测试覆盖:**
```python
# tests/unit/test_story_5_2_pnl_history.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from commands.query import cmd_pnl_history


@pytest.fixture
def mock_update():
    update = MagicMock()
    update.effective_user.id = 123456
    update.message.reply_text = AsyncMock()
    return update


@pytest.fixture
def mock_context():
    return MagicMock()


@pytest.mark.asyncio
async def test_cmd_pnl_history_success(mock_update, mock_context):
    """测试正常查询"""
    with patch('commands.query._get_api') as mock_get_api:
        with patch('commands.query.authorized', return_value=True):
            mock_api = MagicMock()
            mock_api.get_pnl_history = AsyncMock(return_value=[
                {
                    "timestamp": "1709251200",
                    "pnlUsd": "120.50",
                    "pnlEth": "40000000000000000",
                    "pnlPercent": "2.1"
                }
            ])
            mock_get_api.return_value = mock_api

            await cmd_pnl_history(mock_update, mock_context)

            call_args = mock_update.message.reply_text.call_args[0][0]
            assert "PnL Trend" in call_args


@pytest.mark.asyncio
async def test_cmd_pnl_history_with_days(mock_update, mock_context):
    """测试自定义天数查询"""
    mock_context.args = ["30"]

    with patch('commands.query._get_api') as mock_get_api:
        with patch('commands.query.authorized', return_value=True):
            mock_api = MagicMock()
            mock_api.get_pnl_history = AsyncMock(return_value=[])
            mock_get_api.return_value = mock_api

            await cmd_pnl_history(mock_update, mock_context)

            # 应该正常处理（即使数据为空）


@pytest.mark.asyncio
async def test_cmd_pnl_history_empty(mock_update, mock_context):
    """测试无记录情况"""
    with patch('commands.query._get_api') as mock_get_api:
        with patch('commands.query.authorized', return_value=True):
            mock_api = MagicMock()
            mock_api.get_pnl_history = AsyncMock(return_value=[])
            mock_get_api.return_value = mock_api

            await cmd_pnl_history(mock_update, mock_context)

            call_args = mock_update.message.reply_text.call_args[0][0]
            assert "No PnL history" in call_args


@pytest.mark.asyncio
async def test_cmd_pnl_history_api_error(mock_update, mock_context):
    """测试 API 错误处理"""
    with patch('commands.query._get_api') as mock_get_api:
        with patch('commands.query.authorized', return_value=True):
            mock_api = MagicMock()
            mock_api.get_pnl_history = AsyncMock(return_value={"error": "HTTP 500"})
            mock_get_api.return_value = mock_api

            await cmd_pnl_history(mock_update, mock_context)

            call_args = mock_update.message.reply_text.call_args[0][0]
            assert "Error" in call_args


@pytest.mark.asyncio
async def test_cmd_pnl_history_unauthorized(mock_update, mock_context):
    """测试未授权用户拒绝"""
    with patch('commands.query.authorized', return_value=False):
        await cmd_pnl_history(mock_update, mock_context)

        mock_update.message.reply_text.assert_not_called()
```

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story5.2]
- [Source: api.py:27-29 - get_pnl_history 方法]
- [Source: commands/query.py - 现有查询命令模式]
- [Source: utils/formatters.py - 格式化函数]
- [Source: utils/permissions.py - authorized 函数]
- [Source: _bmad-output/implementation-artifacts/5-1-deposits-history.md - Story 5.1 参考实现]

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

Story created with comprehensive developer context including:
- Complete command handler implementation for /pnl_history
- API integration with existing get_pnl_history() method
- Unit test templates with full coverage
- Consistent patterns with existing query commands (especially Story 5.1)
- Message format based on epics.md specification

### File List
