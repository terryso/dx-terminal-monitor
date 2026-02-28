# Story 2.1: 添加新策略命令

Status: review

## Story

作为**用户**，我需要**通过 `/add_strategy <text>` 命令添加新策略**，以便**指导 Agent 进行特定交易**。

## Acceptance Criteria

1. 实现 `contract.add_strategy(content, expiry, priority)` 方法
2. 实现 `cmd_add_strategy` 命令处理函数
3. 命令格式: `/add_strategy 当 ETH 跌破 3000 时买入`
4. 默认参数: expiry=0 (永不过期), priority=1 (中等)
5. 成功时返回: "策略已添加，ID: #4"
6. 策略数量达到上限(8)时返回错误提示
7. 管理员权限检查
8. 添加单元测试

## Tasks / Subtasks

- [x] **Task 1: 实现 contract.add_strategy() 方法** (AC: #1, #4)
  - [x] 在 `contract.py` 中添加 `add_strategy(content: str, expiry: int = 0, priority: int = 1)` 方法
  - [x] 调用合约的 `addStrategy(string content, uint64 expiry, uint8 priority)` 函数
  - [x] 使用 `_send_transaction()` 私有方法处理交易
  - [x] 返回标准结果字典 (success, transactionHash, strategyId, error)

- [x] **Task 2: 实现 cmd_add_strategy 命令处理函数** (AC: #2, #3, #5, #6, #7)
  - [x] 在 `main.py` 中添加 `cmd_add_strategy` 异步函数
  - [x] 使用 `is_admin()` 检查管理员权限
  - [x] 解析命令参数 (将所有参数拼接为 content)
  - [x] 调用 `contract().add_strategy(content)` 使用默认参数
  - [x] 处理成功/失败响应
  - [x] 处理策略上限错误 (合约返回的错误信息)

- [x] **Task 3: 注册命令到 Bot** (AC: #2)
  - [x] 在 `post_init()` 中添加 `BotCommand("add_strategy", "Add new strategy")`
  - [x] 在 `create_app()` 中添加 `CommandHandler("add_strategy", cmd_add_strategy)`
  - [x] 更新 `cmd_start()` 帮助文本，添加 `/add_strategy <text>` 说明

- [x] **Task 4: 添加单元测试** (AC: #8)
  - [x] 在 `tests/unit/test_command_handlers_p1.py` 中添加测试
  - [x] 测试管理员用户成功添加策略
  - [x] 测试非管理员用户被拒绝
  - [x] 测试无参数时的错误提示
  - [x] 测试策略上限错误处理
  - [x] 测试合约调用失败处理

## Dev Notes

### 技术栈要求

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | >=3.12 | 主要开发语言 |
| python-telegram-bot | >=21.0 | Telegram Bot API |
| web3.py | >=6.0.0 | 智能合约交互 |
| pytest | >=8.0 | 测试框架 |

### 合约函数签名

```solidity
// AgentVault.sol
function addStrategy(
    string calldata content,    // 策略文本内容
    uint64 expiry,              // 过期时间戳 (0 = 永不过期)
    uint8 priority              // 优先级 (0=LOW, 1=MEDIUM, 2=HIGH)
) external onlyOwner returns (uint256 strategyId);
```

### 现有代码模式 (来自 Story 1-1, 1-2)

**contract.py 结构:**
```python
class VaultContract:
    async def _send_transaction(self, tx_func: Callable) -> Dict[str, Any]:
        """签名、发送、等待交易确认的私有方法"""
        # 已实现，直接复用

    async def disable_strategy(self, strategy_id: int) -> Dict[str, Any]:
        """禁用指定策略 - 已实现"""
        tx_func = self.contract.functions.disableStrategy(strategy_id)
        return await self._send_transaction(tx_func)
```

**main.py 命令处理器模式:**
```python
async def cmd_disable_strategy(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    # 1. 权限检查
    if not authorized(update):
        await update.message.reply_text("未授权")
        return

    # 2. 参数解析
    args = ctx.args or []
    if len(args) == 0:
        await update.message.reply_text("用法: /disable_strategy <id>")
        return

    # 3. 调用合约
    result = await contract().disable_strategy(strategy_id)

    # 4. 处理响应
    if result.get("success"):
        await update.message.reply_text(f"策略 #{strategy_id} 已禁用...")
    else:
        await update.message.reply_text(f"交易失败: {error}")
```

### 新增代码实现指南

**contract.py - add_strategy 方法:**
```python
async def add_strategy(
    self,
    content: str,
    expiry: int = 0,
    priority: int = 1
) -> Dict[str, Any]:
    """
    添加新策略。

    Args:
        content: 策略文本内容
        expiry: 过期时间戳 (0 = 永不过期)
        priority: 优先级 (0=LOW, 1=MEDIUM, 2=HIGH)

    Returns:
        Dict with keys:
            - success: bool
            - transactionHash: str (hex) - on success
            - strategyId: int - on success (从事件日志解析)
            - status: int - on success
            - blockNumber: int - on success
            - error: str - on failure
    """
    try:
        tx_func = self.contract.functions.addStrategy(content, expiry, priority)
        result = await self._send_transaction(tx_func)

        # 如果成功，尝试从日志解析 strategyId
        if result.get("success"):
            # 合约事件: StrategyAdded(uint256 indexed strategyId, string content)
            # 需要从 receipt 的 logs 中解析
            result["strategyId"] = self._parse_strategy_id_from_logs(
                result.get("receipt", {})
            )

        return result
    except Exception as e:
        logger.error(f"Failed to add strategy: {e}")
        return {"success": False, "error": str(e)}

def _parse_strategy_id_from_logs(self, receipt: Dict) -> Optional[int]:
    """从交易回执日志中解析新添加的策略 ID"""
    # 实现细节: 解析 StrategyAdded 事件
    # 如果无法解析，返回 None (不影响交易成功)
    pass
```

**main.py - cmd_add_strategy 函数:**
```python
from config import is_admin

async def cmd_add_strategy(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """添加新交易策略"""
    # 1. 管理员权限检查 (高风险操作)
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("未授权: 仅管理员可添加策略")
        return

    # 2. 参数解析
    args = ctx.args or []
    if len(args) == 0:
        await update.message.reply_text("用法: /add_strategy <策略内容>")
        return

    # 将所有参数拼接为策略内容
    content = " ".join(args)

    # 3. 调用合约 (使用默认参数: expiry=0, priority=1)
    result = await contract().add_strategy(content)

    # 4. 处理响应
    if result.get("success"):
        strategy_id = result.get("strategyId", "?")
        tx_hash = result.get("transactionHash", "")
        await update.message.reply_text(
            f"策略已添加，ID: #{strategy_id}\n交易哈希: {tx_hash}"
        )
    else:
        error = result.get("error", "未知错误")
        # 检查是否为策略上限错误
        if "max" in error.lower() or "limit" in error.lower() or "8" in error:
            await update.message.reply_text("错误: 已达到策略数量上限 (最多 8 个)")
        else:
            await update.message.reply_text(f"添加失败: {error}")
```

### Project Structure Notes

**修改文件:**
```
dx-terminal-monitor/
├── main.py              # 添加 cmd_add_strategy, 更新 post_init/create_app/cmd_start
├── contract.py          # 添加 add_strategy 方法
└── tests/
    └── unit/
        └── test_command_handlers_p1.py  # 添加 add_strategy 测试
```

### 安全要求

| 级别 | 操作 | 权限要求 |
|------|------|----------|
| 🟡 中风险 | 添加策略 | ADMIN_USERS (使用 is_admin()) |

**关键安全点:**
- 必须使用 `is_admin()` 检查，而非 `authorized()`
- 策略内容直接传递给合约，不做额外验证 (由合约处理)
- 私钥通过环境变量加载，不在代码中硬编码

### 测试模式

```python
# tests/unit/test_command_handlers_p1.py

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

class TestAddStrategy:
    """Tests for cmd_add_strategy command."""

    @pytest.mark.asyncio
    async def test_add_strategy_success(self, mock_update, mock_contract):
        """Test successful strategy addition."""
        # Given
        mock_update.effective_user.id = 12345  # Admin user
        mock_contract.add_strategy.return_value = {
            "success": True,
            "strategyId": 4,
            "transactionHash": "0xabc123"
        }

        with patch("main.is_admin", return_value=True), \
             patch("main.contract", return_value=mock_contract):
            from main import cmd_add_strategy

            # When
            ctx = MagicMock()
            ctx.args = ["当", "ETH", "跌破", "3000", "时买入"]
            await cmd_add_strategy(mock_update, ctx)

        # Then
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "策略已添加" in call_args
        assert "#4" in call_args

    @pytest.mark.asyncio
    async def test_add_strategy_unauthorized(self, mock_update):
        """Test non-admin user is rejected."""
        # Given
        mock_update.effective_user.id = 99999  # Non-admin

        with patch("main.is_admin", return_value=False):
            from main import cmd_add_strategy

            # When
            ctx = MagicMock()
            ctx.args = ["test strategy"]
            await cmd_add_strategy(mock_update, ctx)

        # Then
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "未授权" in call_args or "unauthorized" in call_args.lower()

    @pytest.mark.asyncio
    async def test_add_strategy_no_args(self, mock_update):
        """Test error when no strategy content provided."""
        # Given
        with patch("main.is_admin", return_value=True):
            from main import cmd_add_strategy

            # When
            ctx = MagicMock()
            ctx.args = []
            await cmd_add_strategy(mock_update, ctx)

        # Then
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "用法" in call_args
```

### Previous Story Intelligence (from Epic 1)

**已建立的代码模式:**
- `contract.py` - VaultContract 类使用 `_send_transaction()` 处理所有交易
- `main.py` - 命令处理器使用标准模式: 权限检查 -> 参数解析 -> 调用 -> 响应
- 测试使用 `pytest.mark.asyncio` 和 `AsyncMock`

**Code Review 遗留问题 (Story 1-2):**
- [HIGH] disabledCount always returns 0 - 不影响此 Story
- 此问题在 API 层，与本 Story 的合约调用无关

**已验证的合约调用模式:**
- `disable_strategy()` - 工作正常
- `disable_all_strategies()` - 工作正常
- `_send_transaction()` - 稳定的交易处理

### Git 智能分析

**最近提交:**
```
d6b38de test: Add tests for Story 1-3 menu and help documentation
2c65809 feat: Add /disable_all command with code review fixes
606b647 fix: Use English for disable_strategy BotCommand description
fd1d8bf feat: Add /disable_strategy command for disabling trading strategies
4010964 feat: Add Web3 infrastructure for AgentVault contract interaction
```

**代码模式:**
- 命令处理器使用 `async def cmd_<name>(update, ctx)` 模式
- 合约调用使用 `contract().method()` 模式
- 测试文件命名: `test_command_handlers_p1.py`

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story2.1]
- [Source: docs/architecture.md#智能合约方法]
- [Source: contract.py:89-165 - _send_transaction 方法]
- [Source: contract.py:167-196 - disable_strategy 方法]
- [Source: main.py:270-296 - cmd_disable_strategy 处理器]
- [Source: config.py:31-39 - is_admin 函数]
- [Source: _bmad-output/project-context.md#安全规则]

## Dev Agent Record

### Agent Model Used

GLM-5 (Claude Code CLI)

### Debug Log References

No critical issues encountered during implementation.

### Completion Notes List

- Successfully implemented `contract.add_strategy()` method with default parameters (expiry=0, priority=1)
- Implemented `cmd_add_strategy` command handler with admin permission check using `is_admin()`
- Added strategy ID parsing from event logs via `_parse_strategy_id_from_logs()` helper method
- Updated `_send_transaction()` to include receipt in return value for log parsing
- Registered BotCommand and CommandHandler in `post_init()` and `create_app()`
- Updated help text in `cmd_start()` to include `/add_strategy <text>` command
- Added 13 unit tests covering all acceptance criteria:
  - Test successful strategy addition (AC#2, #3, #5)
  - Test non-admin user rejection (AC#7)
  - Test no args error handling (AC#2, #3)
  - Test strategy limit error handling (AC#6)
  - Test generic contract failure handling (AC#2)
  - Test command handler registration
  - Test bot command registration
  - Test help text update
  - Test contract method calls web3 function
  - Test default parameters usage
  - Test strategy ID parsing from logs
  - Test contract failure handling

### File List

- main.py - Added cmd_add_strategy function, updated imports, post_init, create_app, cmd_start
- contract.py - Added add_strategy method, _parse_strategy_id_from_logs method, updated _send_transaction to include receipt
- tests/unit/test_command_handlers_p1.py - Added TestCmdAddStrategy class (9 tests) and TestContractAddStrategy class (4 tests)
- tests/unit/test_story_1_3_menu_help.py - Updated expected command count from 10 to 11 (added add_strategy)

### Change Log

- 2026-03-01: Implemented Story 2-1 - Add Strategy command with full test coverage
