# Story 5.1: 存取款历史查询

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

作为**用户**,我需要**通过 `/deposits` 命令查看存取款历史**,以便**追踪资金进出情况**。

## Acceptance Criteria

1. 在 `commands/query.py` 添加 `cmd_deposits` 命令处理函数
2. 调用现有 `api.get_deposits_withdrawals()` 方法
3. 格式化输出: 时间、类型(存入/取出)、金额、状态
4. 默认显示最近 10 条记录
5. 支持参数指定数量: `/deposits 20`
6. 添加单元测试

## Tasks / Subtasks

- [x] **Task 1: 实现 cmd_deposits 命令处理函数** (AC: #1, #2, #3, #4, #5)
  - [x] 在 `commands/query.py` 中添加 `cmd_deposits` 异步函数
  - [x] 使用 `authorized()` 检查用户权限
  - [x] 解析可选参数 `ctx.args` 获取显示数量 (默认 10)
  - [x] 调用 `api.get_deposits_withdrawals(limit)` 获取数据
  - [x] 处理 API 错误响应
  - [x] 格式化输出消息:
    - 时间戳 (使用 `format_time`)
    - 类型 (Deposit/Withdrawal)
    - 金额 (使用 `format_eth`)
    - 状态 (Confirmed/Pending)
  - [x] 处理无记录的情况

- [x] **Task 2: 更新命令注册和菜单** (AC: #1)
  - [x] 在 `commands/__init__.py` 中导出 `cmd_deposits`
  - [x] 在 `register_handlers()` 中添加 `CommandHandler("deposits", cmd_deposits)`
  - [x] 在 `main.py` 的 `post_init()` 中添加 `BotCommand("deposits", "Deposits history")`
  - [x] 在 `cmd_start` 帮助文本中添加 `/deposits` 命令说明

- [x] **Task 3: 添加单元测试** (AC: #6)
  - [x] 创建 `tests/unit/test_story_5_1_deposits.py`
  - [x] 测试正常查询 (默认 10 条)
  - [x] 测试自定义数量查询
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

**api.py - get_deposits_withdrawals (已实现):**
```python
# api.py:49-54
async def get_deposits_withdrawals(self, limit: int = 10) -> dict:
    """获取存取款记录"""
    return await self._get(
        f"/deposits-withdrawals/{self.vault}",
        {"limit": limit, "order": "desc"}
    )
```

**utils/formatters.py (已实现):**
```python
# 格式化函数
def format_eth(wei: str | int) -> str  # Wei 转 ETH
def format_time(timestamp: str) -> str  # ISO 时间转可读格式
def format_usd(value: str) -> str       # USD 格式化
```

**utils/permissions.py (已实现):**
```python
def authorized(update: Update) -> bool  # 检查用户是否在允许列表中
```

### 新增代码实现指南

**commands/query.py - cmd_deposits 命令:**
```python
async def cmd_deposits(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """查询存取款历史。 """
    if not authorized(update):
        return

    # 解析可选参数
    limit = 10
    if ctx.args and ctx.args[0].isdigit():
        limit = int(ctx.args[0])

    # 调用 API
    api = _get_api()
    data = await api.get_deposits_withdrawals(limit)

    # 错误处理
    if "error" in data:
        await update.message.reply_text(f"错误: {data['error']}")
        return

    # 获取记录列表
    items = data.get("items", [])
    if not items:
        await update.message.reply_text("暂无存取款记录")
        return

    # 格式化输出
    lines = [f"存取款历史 (最近 {len(items)} 条):\n"]
    for item in items:
        ts = format_time(item.get("timestamp"))
        t = item.get("type", "?")
        status = item.get("status", "?")

        if t == "deposit":
            d = item.get("deposit", {})
            amt = format_eth(d.get("amountWei", "0"))
            lines.append(f"[{ts}] 存入 {amt} ETH")
        elif t == "withdrawal":
            w = item.get("withdrawal", {})
            amt = format_eth(w.get("amountWei", "0"))
            lines.append(f"[{ts}] 取出 {amt} ETH")

        lines.append(f"  状态: {status}\n")

    await update.message.reply_text("\n".join(lines))
```

**commands/__init__.py - 更新导出:**
```python
from .query import (
    cmd_activity,
    cmd_balance,
    cmd_deposits,  # 新增
    cmd_pnl,
    cmd_positions,
    cmd_start,
    cmd_strategies,
    cmd_swaps,
    cmd_vault,
)

def register_handlers(app):
    # Query commands
    # ...existing handlers...
    app.add_handler(CommandHandler("deposits", cmd_deposits))  # 新增

__all__ = [
    # ...
    'cmd_deposits',  # 新增
]
```

**main.py - post_init 更新:**
```python
async def post_init(app: Application):
    commands = [
        # ...existing commands...
        BotCommand("deposits", "Deposits history"),  # 新增
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
/positions - View positions
/activity - Recent activity
/swaps - Recent swaps
/strategies - Active strategies
/vault - Vault info
/deposits - Deposits history  # 新增
...
"""
```

### Project Structure Notes

**修改文件:**
```
dx-terminal-monitor/
├── main.py              # 修改 - 添加 BotCommand
└── commands/
    ├── __init__.py      # 修改 - 导出和注册 cmd_deposits
    └── query.py         # 修改 - 添加 cmd_deposits 函数
```

**新增测试文件:**
```
tests/
└── unit/
    └── test_story_5_1_deposits.py  # 新增
```

### 与其他 Story 的关系

**前置依赖:**
- **api.py** - 提供了 `get_deposits_withdrawals()` 方法
- **utils/formatters.py** - 提供了 `format_eth()`, `format_time()` 格式化函数
- **utils/permissions.py** - 提供了 `authorized()` 权限检查

**功能关系:**
```
Epic 5: 资金查询与历史数据
    ├── Story 5.1: 存取款历史查询 (本 Story) - 仅依赖 api.py
    ├── Story 5.2: PnL 趋势历史 - 仅依赖 api.py
    └── Story 5.3: 存入 ETH - 依赖 Epic 1 (contract.py)
```

### API 响应格式参考

根据 Terminal Markets API，`/deposits-withdrawals/{vault}` 返回格式:
```json
{
    "items": [
        {
            "type": "deposit",
            "timestamp": "2026-03-01T12:00:00Z",
            "status": "Confirmed",
            "deposit": {"amountWei": "1000000000000000000"}
        },
        {
            "type": "withdrawal",
            "timestamp": "2026-03-02T14:30:00Z",
            "status": "Confirmed",
            "withdrawal": {"amountWei": "500000000000000000"}
        }
    ]
}
```

### 测试策略

**单元测试覆盖:**
```python
# tests/unit/test_story_5_1_deposits.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from commands.query import cmd_deposits


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
async def test_cmd_deposits_success(mock_update, mock_context):
    """测试正常查询"""
    with patch('commands.query._get_api') as mock_get_api:
        with patch('commands.query.authorized', return_value=True):
            mock_api = MagicMock()
            mock_api.get_deposits_withdrawals = AsyncMock(return_value={
                "items": [
                    {
                        "type": "deposit",
                        "timestamp": "2026-03-01T12:00:00Z",
                        "status": "Confirmed",
                        "deposit": {"amountWei": "1000000000000000000"}
                    }
                ]
            })
            mock_get_api.return_value = mock_api

            await cmd_deposits(mock_update, mock_context)

            call_args = mock_update.message.reply_text.call_args[0][0]
            assert "存取款历史" in call_args
            assert "存入" in call_args


@pytest.mark.asyncio
async def test_cmd_deposits_with_limit(mock_update, mock_context):
    """测试自定义数量查询"""
    mock_context.args = ["20"]

    with patch('commands.query._get_api') as mock_get_api:
        with patch('commands.query.authorized', return_value=True):
            mock_api = MagicMock()
            mock_api.get_deposits_withdrawals = AsyncMock(return_value={"items": []})
            mock_get_api.return_value = mock_api

            await cmd_deposits(mock_update, mock_context)

            mock_api.get_deposits_withdrawals.assert_called_once_with(20)


@pytest.mark.asyncio
async def test_cmd_deposits_empty(mock_update, mock_context):
    """测试无记录情况"""
    with patch('commands.query._get_api') as mock_get_api:
        with patch('commands.query.authorized', return_value=True):
            mock_api = MagicMock()
            mock_api.get_deposits_withdrawals = AsyncMock(return_value={"items": []})
            mock_get_api.return_value = mock_api

            await cmd_deposits(mock_update, mock_context)

            call_args = mock_update.message.reply_text.call_args[0][0]
            assert "暂无存取款记录" in call_args


@pytest.mark.asyncio
async def test_cmd_deposits_api_error(mock_update, mock_context):
    """测试 API 错误处理"""
    with patch('commands.query._get_api') as mock_get_api:
        with patch('commands.query.authorized', return_value=True):
            mock_api = MagicMock()
            mock_api.get_deposits_withdrawals = AsyncMock(return_value={"error": "HTTP 500"})
            mock_get_api.return_value = mock_api

            await cmd_deposits(mock_update, mock_context)

            call_args = mock_update.message.reply_text.call_args[0][0]
            assert "错误" in call_args


@pytest.mark.asyncio
async def test_cmd_deposits_unauthorized(mock_update, mock_context):
    """测试未授权用户拒绝"""
    with patch('commands.query.authorized', return_value=False):
        await cmd_deposits(mock_update, mock_context)

        mock_update.message.reply_text.assert_not_called()
```

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story5.1]
- [Source: api.py:49-54 - get_deposits_withdrawals 方法]
- [Source: commands/query.py - 现有查询命令模式]
- [Source: utils/formatters.py - 格式化函数]
- [Source: utils/permissions.py - authorized 函数]
- [Source: _bmad-output/project-context.md - API 参考]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6 (claude-opus-4-6)

### Debug Log References

N/A - No issues encountered during implementation.

### Completion Notes List

Story created with comprehensive developer context including:
- Complete command handler implementation for /deposits
- API integration with existing get_deposits_withdrawals() method
- Unit test templates with full coverage
- Consistent patterns with existing query commands

**Implementation completed (2026-03-02):**
- Added `cmd_deposits` async function to `commands/query.py`
- Registered command handler and bot menu entry
- Updated help text in `/start` command
- Created 5 unit tests covering all acceptance criteria
- All tests pass, code quality checks pass

### File List

**Modified files:**
- `commands/query.py` - Added cmd_deposits function and updated help text
- `commands/__init__.py` - Added export and handler registration for cmd_deposits
- `main.py` - Added BotCommand("deposits", "Deposits history")
- `tests/unit/test_story_5_1_deposits.py` - Added unit tests (created during story creation, updated import)

### Change Log

- 2026-03-02: Completed implementation of /deposits command with full test coverage
