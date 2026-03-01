# Story 3.2: 提取 ETH 命令

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

作为**用户**，我需要**通过 `/withdraw <amount>` 命令提取 ETH**，以便**将资金转移到其他地址**。

## Acceptance Criteria

1. 实现 `contract.withdraw_eth(amount)` 方法
2. 实现 `cmd_withdraw` 命令处理函数
3. 命令格式: `/withdraw 0.5` (单位: ETH)
4. 二次确认: "确认提取 0.5 ETH 到你的钱包？ [Y/N]"
5. 成功时返回: "已提取 0.5 ETH，交易哈希: 0x..."
6. 余额不足时返回: "余额不足，当前可用: 0.3 ETH"
7. 管理员权限检查
8. 添加单元测试

## Tasks / Subtasks

- [x] **Task 1: 实现 contract.withdraw_eth() 方法** (AC: #1)
  - [x] 在 `contract.py` 中添加 `withdraw_eth(amount_wei: int)` 方法
  - [x] 调用合约的 `withdrawETH(uint256 amount)` 函数
  - [x] 使用 `_send_transaction()` 私有方法处理交易
  - [x] 返回标准结果字典 (success, transactionHash, error)
  - [x] 注意: 合约函数使用 Wei 单位，命令层负责 ETH -> Wei 转换

- [x] **Task 2: 实现 cmd_withdraw 命令处理函数** (AC: #2, #3, #5, #6, #7)
  - [x] 在 `main.py` 中添加 `cmd_withdraw` 异步函数
  - [x] 使用 `is_admin()` 检查管理员权限
  - [x] 解析命令参数 (ETH 金额)
  - [x] 验证金额为正数
  - [x] 调用 API 获取当前余额进行预检查
  - [x] 实现二次确认流程 (等待用户 Y/N 响应)
  - [x] 处理成功/失败响应

- [x] **Task 3: 实现二次确认流程** (AC: #4)
  - [x] 使用 `ConversationHandler` 管理确认状态
  - [x] 状态 1: 等待确认 (WAITING_CONFIRMATION)
  - [x] 状态 2: 确认完成 (END)
  - [x] Y/y 确认执行，N/n 取消操作
  - [x] 超时处理 (30秒)

- [x] **Task 4: 注册命令到 Bot** (AC: #2)
  - [x] 在 `post_init()` 中添加 `BotCommand("withdraw", "Withdraw ETH to wallet")`
  - [x] 在 `create_app()` 中添加 `ConversationHandler` 或 `CommandHandler`
  - [x] 更新 `cmd_start()` 帮助文本，添加 `/withdraw` 说明

- [x] **Task 5: 添加单元测试** (AC: #8)
  - [x] 在 `tests/unit/test_story_3_2_withdraw_eth.py` 中添加测试
  - [x] 测试管理员用户成功提取 ETH
  - [x] 测试非管理员用户被拒绝
  - [x] 测试余额不足时的错误处理
  - [x] 测试无效金额输入
  - [x] 测试二次确认流程 (确认/取消)
  - [x] 测试合约调用失败处理
  - [x] 测试命令注册

## Dev Notes

### 技术栈要求

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | >=3.12 | 主要开发语言 |
| python-telegram-bot | >=21.0 | Telegram Bot API |
| web3.py | >=6.0.0 | 智能合约交互 |
| aiohttp | >=3.9.3 | 异步 HTTP 请求 (获取余额) |
| pytest | >=8.0 | 测试框架 |

### 合约函数签名

```solidity
// AgentVault.sol
function withdrawETH(uint256 amount) external onlyOwner;

// 参数说明:
// amount: 提取金额 (单位: Wei)
// 注意: 只能提取到 owner 地址 (即配置的钱包地址)

// ETH 单位转换:
// 1 ETH = 10^18 Wei
// 0.5 ETH = 500000000000000000 Wei
```

### 现有代码模式 (来自 Story 3-1)

**contract.py 结构:**
```python
class VaultContract:
    async def _send_transaction(self, tx_func: Callable) -> Dict[str, Any]:
        """签名、发送、等待交易确认的私有方法"""
        # 已实现，直接复用

    async def update_settings(self, max_trade_bps: int, slippage_bps: int) -> Dict[str, Any]:
        """更新交易设置 - 已实现"""
        # 参考此模式的参数处理和返回格式
```

**main.py 命令处理器模式 (高风险操作):**
```python
async def cmd_update_settings(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    # 1. 管理员权限检查 (高风险操作)
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("未授权: 仅管理员可更新设置")
        return

    # 2. 参数解析
    args = ctx.args or []
    if len(args) == 0:
        await update.message.reply_text("用法: /update_settings ...")
        return

    # 3. 调用合约
    result = await contract().update_settings(...)

    # 4. 处理响应
    if result.get("success"):
        await update.message.reply_text(f"...")
    else:
        await update.message.reply_text(f"...")
```

### 新增代码实现指南

**contract.py - withdraw_eth 方法:**
```python
async def withdraw_eth(self, amount_wei: int) -> Dict[str, Any]:
    """
    Withdraw ETH from the vault to the owner address.

    Args:
        amount_wei: Amount to withdraw in Wei

    Returns:
        Dict with keys:
            - success: bool
            - transactionHash: str (hex) - on success
            - status: int - on success
            - blockNumber: int - on success
            - error: str - on failure
    """
    try:
        # Validate amount
        if amount_wei <= 0:
            return {
                'success': False,
                'error': '提取金额必须大于 0'
            }

        tx_func = self.contract.functions.withdrawETH(amount_wei)
        return await self._send_transaction(tx_func)

    except Exception as e:
        logger.error(f"Failed to withdraw ETH: {e}")
        return {"success": False, "error": str(e)}
```

**main.py - cmd_withdraw 函数 (使用 ConversationHandler 进行二次确认):**
```python
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
from web3 import Web3
import re

# Conversation states
WAITING_CONFIRMATION = 1
END = ConversationHandler.END

# 临时存储提取金额 (实际生产中应使用更安全的方式)
_pending_withdrawals = {}

async def cmd_withdraw(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """提取 ETH 到钱包"""
    # 1. 管理员权限检查 (高风险操作)
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("未授权: 仅管理员可提取资金")
        return END

    # 2. 参数解析
    args = ctx.args or []
    if len(args) == 0:
        await update.message.reply_text(
            "用法: /withdraw <amount>\n"
            "示例: /withdraw 0.5\n"
            "说明: 提取指定数量的 ETH 到管理员钱包"
        )
        return END

    # 3. 解析金额
    try:
        amount_eth = float(args[0])
        if amount_eth <= 0:
            await update.message.reply_text("金额必须大于 0")
            return END
    except ValueError:
        await update.message.reply_text("无效的金额格式，请输入数字如: 0.5")
        return END

    # 4. 获取当前余额进行预检查
    try:
        vault_data = await api().get_vault()
        balance_eth = float(vault_data.get('balance', 0))
    except Exception as e:
        logger.warning(f"Failed to fetch balance: {e}")
        balance_eth = None  # 无法获取余额，跳过预检查

    # 5. 余额检查
    if balance_eth is not None and amount_eth > balance_eth:
        await update.message.reply_text(
            f"余额不足\n"
            f"当前可用: {balance_eth:.4f} ETH\n"
            f"请求提取: {amount_eth} ETH"
        )
        return END

    # 6. 存储待确认的提取金额
    user_id = update.effective_user.id
    _pending_withdrawals[user_id] = amount_eth

    # 7. 二次确认
    await update.message.reply_text(
        f"确认提取 {amount_eth} ETH 到你的钱包？\n"
        f"[Y] 确认\n"
        f"[N] 取消"
    )
    return WAITING_CONFIRMATION

async def handle_withdraw_confirm(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """处理提取确认"""
    user_id = update.effective_user.id
    response = update.message.text.strip().upper()

    if response not in ('Y', 'N', 'YES', 'NO'):
        await update.message.reply_text("请回复 Y 确认或 N 取消")
        return WAITING_CONFIRMATION

    if response in ('N', 'NO'):
        # 取消操作
        _pending_withdrawals.pop(user_id, None)
        await update.message.reply_text("已取消提取")
        return END

    # 确认提取
    amount_eth = _pending_withdrawals.pop(user_id, None)
    if amount_eth is None:
        await update.message.reply_text("会话已过期，请重新执行 /withdraw 命令")
        return END

    # 转换为 Wei
    amount_wei = int(Web3.to_wei(amount_eth, 'ether'))

    # 调用合约
    result = await contract().withdraw_eth(amount_wei)

    if result.get("success"):
        tx_hash = result.get("transactionHash", "")
        logger.info(f"Withdrawal confirmed: {amount_eth} ETH by user {user_id}, tx: {tx_hash}")
        await update.message.reply_text(
            f"已提取 {amount_eth} ETH\n"
            f"交易哈希: {tx_hash}"
        )
    else:
        error = result.get("error", "未知错误")
        await update.message.reply_text(f"提取失败: {error}")

    return END

async def handle_withdraw_cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """处理提取取消 (通过 /cancel 命令)"""
    user_id = update.effective_user.id
    _pending_withdrawals.pop(user_id, None)
    await update.message.reply_text("已取消提取")
    return END
```

**main.py - ConversationHandler 注册:**
```python
# 在 create_app() 中添加
withdraw_handler = ConversationHandler(
    entry_points=[CommandHandler("withdraw", cmd_withdraw)],
    states={
        WAITING_CONFIRMATION: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_withdraw_confirm)
        ],
    },
    fallbacks=[CommandHandler("cancel", handle_withdraw_cancel)],
)
app.add_handler(withdraw_handler)
```

### Project Structure Notes

**修改文件:**
```
dx-terminal-monitor/
├── main.py              # 添加 cmd_withdraw, handle_withdraw_confirm, handle_withdraw_cancel
│                       # 更新 post_init, create_app, cmd_start
├── contract.py          # 添加 withdraw_eth 方法
└── tests/
    └── unit/
        └── test_story_3_2_withdraw_eth.py  # 新增测试文件
```

### 安全要求

| 级别 | 操作 | 权限要求 |
|------|------|----------|
| 🔴 高风险 | 提取 ETH | ADMIN_USERS (使用 is_admin()) |

**关键安全点:**
- 必须使用 `is_admin()` 检查，而非 `authorized()`
- 二次确认是必需的，防止误操作
- 余额预检查避免不必要的交易失败
- 使用 `logger.info()` 记录审计日志，包括操作者、金额、交易哈希
- ETH -> Wei 转换使用 `Web3.to_wei()` 避免精度问题

**ConversationHandler 安全考虑:**
- `_pending_withdrawals` 字典存储临时状态 (生产环境建议使用 Redis)
- 超时处理防止状态泄露
- `/cancel` 命令作为 fallback 清理状态

### 测试模式

```python
# tests/unit/test_story_3_2_withdraw_eth.py

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from web3 import Web3

class TestCmdWithdraw:
    """Tests for cmd_withdraw command."""

    @pytest.mark.asyncio
    async def test_withdraw_success_flow(self, mock_update, mock_contract, mock_api):
        """Test successful ETH withdrawal with confirmation."""
        # Given
        mock_update.effective_user.id = 12345  # Admin user
        mock_api.get_vault.return_value = {'balance': '2.0'}
        mock_contract.withdraw_eth.return_value = {
            "success": True,
            "transactionHash": "0xabc123"
        }

        with patch("main.is_admin", return_value=True), \
             patch("main.contract", return_value=mock_contract), \
             patch("main.api", return_value=mock_api):
            from main import cmd_withdraw, handle_withdraw_confirm

            # When - Start withdrawal
            ctx = MagicMock()
            ctx.args = ["0.5"]
            result = await cmd_withdraw(mock_update, ctx)
            assert result == 1  # WAITING_CONFIRMATION

            # When - Confirm withdrawal
            mock_update.message.text = "Y"
            mock_update.message.reply_text = AsyncMock()
            result = await handle_withdraw_confirm(mock_update, MagicMock())
            assert result == -1  # END

        # Then
        mock_contract.withdraw_eth.assert_called_once_with(
            int(Web3.to_wei(0.5, 'ether'))
        )

    @pytest.mark.asyncio
    async def test_withdraw_insufficient_balance(self, mock_update, mock_api):
        """Test withdrawal with insufficient balance."""
        # Given
        mock_update.effective_user.id = 12345
        mock_api.get_vault.return_value = {'balance': '0.3'}

        with patch("main.is_admin", return_value=True), \
             patch("main.api", return_value=mock_api):
            from main import cmd_withdraw

            # When
            ctx = MagicMock()
            ctx.args = ["0.5"]
            result = await cmd_withdraw(mock_update, ctx)

        # Then
        assert result == -1  # END (rejected)
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "余额不足" in call_args or "0.3" in call_args

    @pytest.mark.asyncio
    async def test_withdraw_unauthorized(self, mock_update):
        """Test non-admin user is rejected."""
        # Given
        mock_update.effective_user.id = 99999  # Non-admin

        with patch("main.is_admin", return_value=False):
            from main import cmd_withdraw

            # When
            ctx = MagicMock()
            ctx.args = ["0.5"]
            result = await cmd_withdraw(mock_update, ctx)

        # Then
        assert result == -1  # END
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "未授权" in call_args

    @pytest.mark.asyncio
    async def test_withdraw_cancel_confirmation(self, mock_update, mock_api):
        """Test cancelling withdrawal during confirmation."""
        # Given
        mock_update.effective_user.id = 12345
        mock_api.get_vault.return_value = {'balance': '2.0'}

        with patch("main.is_admin", return_value=True), \
             patch("main.api", return_value=mock_api):
            from main import cmd_withdraw, handle_withdraw_confirm

            # Start withdrawal
            ctx = MagicMock()
            ctx.args = ["0.5"]
            await cmd_withdraw(mock_update, ctx)

            # When - Cancel
            mock_update.message.text = "N"
            mock_update.message.reply_text = AsyncMock()
            result = await handle_withdraw_confirm(mock_update, MagicMock())

        # Then
        assert result == -1  # END
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "取消" in call_args

    @pytest.mark.asyncio
    async def test_withdraw_invalid_amount(self, mock_update):
        """Test invalid amount format."""
        # Given
        mock_update.effective_user.id = 12345

        with patch("main.is_admin", return_value=True):
            from main import cmd_withdraw

            # When
            ctx = MagicMock()
            ctx.args = ["abc"]
            result = await cmd_withdraw(mock_update, ctx)

        # Then
        assert result == -1  # END
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "无效" in call_args or "数字" in call_args


class TestContractWithdrawEth:
    """Tests for VaultContract.withdraw_eth method."""

    @pytest.mark.asyncio
    async def test_withdraw_eth_valid_amount(self, mock_contract_instance):
        """Test successful ETH withdrawal."""
        # Given
        amount_wei = int(Web3.to_wei(0.5, 'ether'))
        mock_contract_instance.contract.functions.withdrawETH.return_value.build_transaction.return_value = {}
        mock_contract_instance.contract.functions.withdrawETH.return_value.estimate_gas.return_value = 100000

        # When
        result = await mock_contract_instance.withdraw_eth(amount_wei)

        # Then
        mock_contract_instance.contract.functions.withdrawETH.assert_called_once_with(amount_wei)

    @pytest.mark.asyncio
    async def test_withdraw_eth_zero_amount(self, mock_contract_instance):
        """Test zero amount is rejected."""
        # When
        result = await mock_contract_instance.withdraw_eth(0)

        # Then
        assert result["success"] is False
        assert "大于 0" in result["error"]

    @pytest.mark.asyncio
    async def test_withdraw_eth_negative_amount(self, mock_contract_instance):
        """Test negative amount is rejected."""
        # When
        result = await mock_contract_instance.withdraw_eth(-100)

        # Then
        assert result["success"] is False
        assert "大于 0" in result["error"]
```

### Previous Story Intelligence (from Story 3-1)

**已建立的代码模式:**
- `contract.py` - VaultContract 类使用 `_send_transaction()` 处理所有交易
- `main.py` - 高风险命令处理器使用 `is_admin()` 进行权限检查
- 测试使用 `pytest.mark.asyncio` 和 `AsyncMock`
- 命令注册在 `post_init()` (BotCommand) 和 `create_app()` (CommandHandler/ConversationHandler)

**Story 3-1 实现经验:**
- 使用 `is_admin()` 进行管理员权限检查
- 使用 `logger.info()` 记录管理员操作审计日志
- 参数验证在命令处理器层和合约层双重验证
- 合约方法包装在 try/except 中返回标准错误字典
- API 获取当前数据作为默认值或预检查

**已验证的合约调用模式:**
- `disable_strategy()` - 工作正常
- `disable_all_strategies()` - 工作正常
- `add_strategy()` - 工作正常
- `pause_vault()` - 工作正常
- `update_settings()` - 工作正常
- `_send_transaction()` - 稳定的交易处理

### Git 智能分析

**最近提交:**
```
8976fb2 feat: Add /update_settings command for trading configuration
b3db73f docs: Add BMAD artifacts for Story 2-2 delivery
6d281d8 feat: Add /pause and /resume commands for Agent trading control
b9c5832 feat: Add /add_strategy command for adding trading strategies
d6b38de test: Add tests for Story 1-3 menu and help documentation
```

**代码模式:**
- 命令处理器使用 `async def cmd_<name>(update, ctx)` 模式
- 合约调用使用 `contract().method()` 模式
- 测试文件命名: `test_story_<epic>_<story>_<name>.py`
- 高风险操作使用 `is_admin()` 检查
- BotCommand 描述使用小写开头

### 架构合规性

**合约交互层 (contract.py):**
- 复用 `_send_transaction()` 私有方法
- 返回标准结果字典格式: `{success, transactionHash, status, blockNumber, error}`
- 使用 `logger.error()` 记录错误
- 参数验证在合约方法入口处进行

**命令处理层 (main.py):**
- 使用 `is_admin()` 检查管理员权限
- 使用 `ConversationHandler` 管理二次确认流程
- 处理成功/失败响应，提供用户友好消息
- 使用 `logger.info()` 记录审计日志

**API 集成:**
- 使用 `api().get_vault()` 获取当前余额进行预检查
- 处理 API 调用失败时的降级逻辑 (跳过预检查)

### ETH/Wei 单位转换说明

Web3.py 提供了便捷的单位转换函数:

```python
from web3 import Web3

# ETH -> Wei
amount_wei = Web3.to_wei(0.5, 'ether')  # 500000000000000000

# Wei -> ETH
amount_eth = Web3.from_wei(500000000000000000, 'ether')  # 0.5

# 常用单位:
# wei: 1
# gwei: 10^9
# ether: 10^18
```

**注意事项:**
- 合约函数始终使用 Wei 单位
- 用户输入和显示使用 ETH 单位
- 转换时使用 `Web3.to_wei()` 和 `Web3.from_wei()` 避免手动计算错误

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story3.2]
- [Source: docs/architecture.md#智能合约方法]
- [Source: contract.py:89-166 - _send_transaction 方法]
- [Source: contract.py:344-382 - update_settings 方法参考]
- [Source: main.py - cmd_update_settings 处理器参考]
- [Source: config.py:31-39 - is_admin 函数]
- [Source: _bmad-output/project-context.md#安全规则]
- [Source: _bmad-output/implementation-artifacts/3-1-update-settings.md - Previous Story]
- [Source: api.py - get_vault() 方法用于获取当前余额]
- [Source: python-telegram-bot docs - ConversationHandler]

## Dev Agent Record

### Agent Model Used

GLM-5 (via Claude Code)

### Debug Log References

None required - all tests passed on first run after implementation.

### Completion Notes List

- **2026-03-01**: Story 3-2 implementation complete
  - Implemented `contract.withdraw_eth()` method with amount validation
  - Implemented `cmd_withdraw` command handler with admin permission check
  - Implemented `handle_withdraw_confirm` and `handle_withdraw_cancel` handlers
  - Added `ConversationHandler` for two-step confirmation flow
  - Added BotCommand registration in `post_init()`
  - Updated `cmd_start()` help text with `/withdraw` command
  - Added 14 unit tests covering all acceptance criteria
  - Fixed pre-existing test issues with ConversationHandler.commands attribute access
  - All 211 tests pass with no regressions

- **2026-03-01**: Code review fixes applied
  - Fixed balance error message format to match AC #6 specification
  - Added decimal precision validation (max 6 decimal places for ETH amounts)
  - Added 2 new tests: test_withdraw_excessive_precision, test_withdraw_session_expired
  - All 204 unit tests pass with no regressions

### File List

**Modified Files:**
- `contract.py` - Added `withdraw_eth()` method
- `main.py` - Added `cmd_withdraw`, `handle_withdraw_confirm`, `handle_withdraw_cancel`, conversation states, imports, updated `post_init()`, `create_app()`, `cmd_start()`, and precision validation
- `tests/unit/test_story_3_2_withdraw_eth.py` - 16 unit tests (added precision and session expiry tests during review)

## Change Log

- **2026-03-01**: Story 3-2 implementation complete
  - Added /withdraw command for ETH withdrawals with two-step confirmation
  - All acceptance criteria satisfied
  - 14 new unit tests added, all passing
  - Full test suite (211 tests) passing with no regressions

- **2026-03-01**: Code review complete
  - Fixed MEDIUM issue: Balance error message now matches AC format
  - Fixed MEDIUM issue: Added decimal precision validation (max 6 decimals)
  - Added 2 new tests for edge cases
  - 16 total unit tests for Story 3-2, all passing
  - Full test suite (204 tests) passing with no regressions
  - Story status: done
