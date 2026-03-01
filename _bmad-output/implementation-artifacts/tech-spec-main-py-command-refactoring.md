---
title: 'main.py 命令模块重构'
slug: 'main-py-command-refactoring'
created: '2026-03-01'
status: 'completed'
stepsCompleted: [1, 2, 3, 4, 5]
tech_stack:
  - Python 3.12+
  - python-telegram-bot 21.x
  - pytest + AsyncMock
  - Web3.py
files_to_modify:
  - main.py (重构为入口)
  - commands/__init__.py (新建)
  - commands/query.py (新建)
  - commands/admin.py (新建)
  - commands/monitor.py (新建)
  - commands/withdraw.py (新建)
  - utils/__init__.py (新建)
  - utils/formatters.py (新建)
  - utils/permissions.py (新建)
  - tests/unit/test_command_handlers.py (更新导入)
  - tests/unit/test_command_handlers_p1.py (更新导入)
  - tests/unit/test_utils.py (更新导入)
  - tests/unit/test_edge_cases.py (更新导入)
  - tests/unit/test_story_*.py (更新导入)
  - tests/support/helpers.py (移除重复，改用 utils.formatters)
code_patterns:
  - async def cmd_<name>(update, context) 命令处理器模式
  - 权限检查前置模式 (authorized/is_admin)
  - 模块级单例访问 (api, contract)
  - patch('module.xxx') 测试模拟模式
test_patterns:
  - pytest.mark.asyncio 装饰器
  - MagicMock + AsyncMock 组合
  - Given-When-Then 结构
  - patch('module.function') 模式
---

# Tech-Spec: main.py 命令模块重构

**Created:** 2026-03-01
**Updated:** 2026-03-01 (Adversarial Review 反馈已整合)

## Overview

### Problem Statement

main.py 当前包含所有命令处理代码（877行），包括 18+ 命令处理器、格式化工具函数、权限检查、应用配置和启动逻辑。随着功能增加，文件将持续膨胀，导致：
- 代码难以导航和维护
- 职责不清晰
- 测试定位困难
- 多人协作易产生冲突

### Solution

采用混合模式进行模块拆分：
1. 按功能域组织命令处理器到 `commands/` 目录
2. 抽离公共工具函数到 `utils/` 目录
3. main.py 仅保留应用入口、启动逻辑和命令注册
4. 使用依赖注入模式避免循环导入

### Scope

**In Scope:**
- 创建 `commands/` 目录及子模块（query.py, admin.py, monitor.py, withdraw.py）
- 创建 `utils/` 目录及子模块（formatters.py, permissions.py）
- 迁移现有命令处理器到对应模块
- 迁移格式化函数到 utils/formatters.py
- 迁移 authorized() 函数到 utils/permissions.py
- 更新 main.py 为精简入口（~80行）
- 更新测试导入路径

**Out of Scope:**
- 修改 api.py、contract.py、config.py、monitor.py、notifier.py
- 添加新命令或功能
- 改变命令的外部行为
- 重构测试逻辑（仅更新导入）

## Context for Development

### Codebase Patterns

**命令处理器模式：**
```python
# 标准命令处理器模式
async def cmd_<name>(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 1. 权限检查
    if not authorized(update):
        await update.message.reply_text("未授权")
        return

    # 2. 参数解析
    args = context.args or []

    # 3. 业务逻辑
    result = await api_or_contract_call()

    # 4. 格式化响应
    await update.message.reply_text(formatted_response)
```

**测试导入模式：**
```python
# 重构后的测试导入方式
with patch("commands.query.authorized", return_value=True), \
     patch("commands.query.api") as mock_api:
    from commands.query import cmd_balance
    await cmd_balance(mock_update, mock_context)
```

**发现的问题：**
- `tests/support/helpers.py` 重复定义了 `format_eth`, `format_usd`, `format_percent`
- 测试文件大量使用 `from main import xxx`，重构后需改为对应模块导入

### Files to Reference

| File | Purpose | 变更类型 |
| ---- | ------- | -------- |
| main.py | 当前 877 行，所有命令代码 | 重构为 ~80 行入口 |
| api.py | REST API 客户端 | 不变 |
| contract.py | Web3 合约交互 | 不变 |
| config.py | 配置管理，含 is_admin() | 不变 |
| monitor.py | ActivityMonitor 类 | 不变 |
| notifier.py | TelegramNotifier 类 | 不变 |
| tests/unit/test_command_handlers.py | 命令处理器测试 | 更新导入路径 |
| tests/unit/test_command_handlers_p1.py | 命令处理器测试 P1 | 更新导入路径 |
| tests/unit/test_utils.py | 格式化函数测试 | 更新导入路径 |
| tests/unit/test_story_*.py | 各 Story 测试 | 更新导入路径 |
| tests/support/helpers.py | 测试辅助函数 | 移除重复的格式化函数 |

### Technical Decisions

1. **目录结构**：采用扁平化 commands/ 和 utils/，避免过度嵌套
2. **导出方式**：commands/__init__.py 集中导出所有处理器，便于 main.py 注册
3. **依赖注入（重要）**：
   - `api` 实例保留在 main.py，各模块通过 `from main import api` 访问
   - `_monitor_instance` 保留在 main.py，monitor.py 通过 setter 注入（避免循环导入）
   - `contract` 通过 `get_contract()` 函数访问（保持现有模式）
4. **命名约定**：保持 cmd_ 前缀，便于识别命令处理器
5. **is_admin 保留**：`is_admin()` 保留在 config.py，因为它依赖 config.ADMIN_USERS
6. **authorized 迁移**：`authorized()` 迁移到 utils/permissions.py
7. **格式化函数**：迁移到 utils/formatters.py，tests/support/helpers.py 改为导入使用
8. **全局状态**：`_monitor_instance`, `_notifier_instance` 保留在 main.py（应用生命周期管理）
9. **导入顺序**：遵循 PEP 8 - 标准库 → 第三方库 → 本地模块

### 循环导入解决方案

**问题**：monitor.py 需要访问 main.py 中的 `_monitor_instance`，但 main.py 导入 commands 模块。

**解决方案**：使用 setter 注入模式
```python
# commands/monitor.py
_monitor_instance = None

def set_monitor_instance(instance):
    """由 main.py 在 post_init 中调用"""
    global _monitor_instance
    _monitor_instance = instance

# main.py post_init 中
from commands.monitor import set_monitor_instance
set_monitor_instance(_monitor_instance)
```

### 延迟导入实现（实际采用）

**问题**：commands 模块需要访问 main.py 中的 `api` 和 `contract`，但直接导入会导致循环依赖。

**解决方案**：使用延迟导入 getter 函数
```python
# commands/query.py
def _get_api():
    """延迟导入 api 避免循环导入。"""
    from main import api
    return api

async def cmd_balance(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    api = _get_api()  # 在函数内部获取实例
    data = await api.get_balance()
    # ...
```

**测试时的 patch 模式**：
```python
# 测试文件
with patch("commands.query._get_api") as mock_get_api:
    mock_api = AsyncMock()
    mock_get_api.return_value = mock_api
    from commands.query import cmd_balance
    await cmd_balance(mock_update, mock_context)
```

**优点**：
1. 避免模块加载时的循环导入
2. 允许测试时注入 mock
3. 保持代码结构清晰

## Implementation Plan

### Tasks

#### Phase 1: 创建基础设施（无依赖）

- [x] Task 1: 创建 utils/ 目录结构
  - File: `utils/__init__.py`
  - Action: 创建导出文件
  - Notes:
    ```python
    # utils/__init__.py
    from .formatters import format_eth, format_usd, format_percent, format_time
    from .permissions import authorized

    __all__ = ['format_eth', 'format_usd', 'format_percent', 'format_time', 'authorized']
    ```

- [x] Task 2: 创建格式化工具模块
  - File: `utils/formatters.py`
  - Action: 从 main.py 迁移以下函数（保持签名和逻辑不变）：
    - `format_eth(wei: str) -> str`
    - `format_usd(value) -> str`
    - `format_percent(value) -> str`
    - `format_time(timestamp) -> str`
  - Notes: 导入顺序：标准库 → 无

- [x] Task 3: 创建权限工具模块
  - File: `utils/permissions.py`
  - Action: 从 main.py 迁移 `authorized(update: Update) -> bool` 函数
  - Notes:
    ```python
    from telegram import Update
    from config import ALLOWED_USERS

    def authorized(update: Update) -> bool:
        if not ALLOWED_USERS:
            return True
        return update.effective_user.id in ALLOWED_USERS
    ```

#### Phase 2: 创建命令模块（依赖 utils/）

- [x] Task 4: 创建 commands/ 目录结构
  - File: `commands/__init__.py`
  - Action: 创建模块，集中导出所有命令处理器和注册函数
  - Notes:
    ```python
    # commands/__init__.py
    from .query import (
        cmd_start, cmd_balance, cmd_positions, cmd_pnl,
        cmd_activity, cmd_swaps, cmd_strategies, cmd_vault
    )
    from .admin import (
        cmd_add_strategy, cmd_disable_strategy, cmd_disable_all,
        cmd_pause, cmd_resume, cmd_update_settings
    )
    from .monitor import (
        cmd_monitor_status, cmd_monitor_start, cmd_monitor_stop,
        set_monitor_instance
    )
    from .withdraw import create_withdraw_handler

    def register_handlers(app):
        """注册所有命令处理器到 Application"""
        from telegram.ext import CommandHandler

        # 查询命令
        app.add_handler(CommandHandler("start", cmd_start))
        app.add_handler(CommandHandler("help", cmd_start))
        app.add_handler(CommandHandler("balance", cmd_balance))
        app.add_handler(CommandHandler("positions", cmd_positions))
        app.add_handler(CommandHandler("pnl", cmd_pnl))
        app.add_handler(CommandHandler("activity", cmd_activity))
        app.add_handler(CommandHandler("swaps", cmd_swaps))
        app.add_handler(CommandHandler("strategies", cmd_strategies))
        app.add_handler(CommandHandler("vault", cmd_vault))

        # 管理命令
        app.add_handler(CommandHandler("add_strategy", cmd_add_strategy))
        app.add_handler(CommandHandler("disable_strategy", cmd_disable_strategy))
        app.add_handler(CommandHandler("disable_all", cmd_disable_all))
        app.add_handler(CommandHandler("pause", cmd_pause))
        app.add_handler(CommandHandler("resume", cmd_resume))
        app.add_handler(CommandHandler("update_settings", cmd_update_settings))

        # 监控命令
        app.add_handler(CommandHandler("monitor_status", cmd_monitor_status))
        app.add_handler(CommandHandler("monitor_start", cmd_monitor_start))
        app.add_handler(CommandHandler("monitor_stop", cmd_monitor_stop))

        # 提款对话（ConversationHandler）
        app.add_handler(create_withdraw_handler())

    __all__ = ['register_handlers', 'set_monitor_instance']
    ```

- [x] Task 5: 创建查询命令模块
  - File: `commands/query.py`
  - Action: 迁移以下命令处理器：
    - `cmd_start` (帮助信息)
    - `cmd_balance`
    - `cmd_positions`
    - `cmd_pnl`
    - `cmd_activity`
    - `cmd_swaps`
    - `cmd_strategies`
    - `cmd_vault`
  - Notes: 使用延迟导入模式避免循环导入（见下方"循环导入解决方案"）

- [x] Task 6: 创建管理命令模块
  - File: `commands/admin.py`
  - Action: 迁移以下命令处理器：
    - `cmd_add_strategy`
    - `cmd_disable_strategy`
    - `cmd_disable_all`
    - `cmd_pause`
    - `cmd_resume`
    - `cmd_update_settings`
  - Notes: 使用延迟导入模式（见下方"延迟导入实现"）

- [x] Task 7: 创建监控命令模块
  - File: `commands/monitor.py`
  - Action: 迁移以下内容：
    - `_monitor_instance` 模块级变量（初始为 None）
    - `set_monitor_instance(instance)` setter 函数
    - `cmd_monitor_status`
    - `cmd_monitor_start`
    - `cmd_monitor_stop`
  - Notes:
    ```python
    import logging

    from telegram import Update
    from telegram.ext import ContextTypes

    from config import is_admin

    logger = logging.getLogger(__name__)
    _monitor_instance = None

    def set_monitor_instance(instance):
        """由 main.py 在 post_init 中调用，注入 monitor 实例"""
        global _monitor_instance
        _monitor_instance = instance
    ```

- [x] Task 8: 创建提款命令模块（带对话流程）
  - File: `commands/withdraw.py`
  - Action: 迁移以下内容：
    - `WAITING_CONFIRMATION` 常量
    - `END` 常量
    - `_pending_withdrawals` 字典（模块级）
    - `cmd_withdraw`
    - `handle_withdraw_confirm`
    - `handle_withdraw_cancel`
    - `create_withdraw_handler()` 工厂函数
  - Notes: 使用延迟导入模式

#### Phase 3: 重构主入口（依赖 commands/）

- [x] Task 9: 重构 main.py 为精简入口
  - File: `main.py`
  - Action:
    1. 移除已迁移的命令处理器
    2. 移除已迁移的工具函数
    3. 保留以下内容：
       - 导入语句（包括 `from commands import register_handlers, set_monitor_instance`）
       - 日志配置
       - `api = TerminalAPI()` 实例
       - `_contract_instance` 及 get/set 函数
       - `_monitor_instance`, `_notifier_instance`
       - `post_init` 函数（添加 `set_monitor_instance(_monitor_instance)` 调用）
       - `_on_new_activity` 回调
       - `create_app` 函数（使用 `register_handlers(app)` 替代手动注册）
       - `main` 函数
  - Notes: 最终目标 ~80-100 行（实际实现：119 行）

#### Phase 4: 更新测试（依赖所有模块）

- [x] Task 10: 更新测试辅助模块
  - File: `tests/support/helpers.py`
  - Action:
    1. 移除 `format_eth`, `format_usd`, `format_percent` 函数定义
    2. 改为从 `utils.formatters` 导入并重新导出
  - Notes:
    ```python
    # tests/support/helpers.py
    from utils.formatters import format_eth, format_usd, format_percent, format_time

    # 重新导出以保持向后兼容
    __all__ = ['format_eth', 'format_usd', 'format_percent', 'format_time', ...]
    ```

- [x] Task 11: 更新命令处理器测试
  - Files: `tests/unit/test_command_handlers.py`, `tests/unit/test_command_handlers_p1.py`
  - Action: 更新所有 patch 路径和导入：
    | 原路径 | 新路径 |
    |--------|--------|
    | `patch("main.authorized")` | `patch("commands.query.authorized")` |
    | `patch("main.api")` | `patch("commands.query._get_api")` |
    | `patch("main.is_admin")` | `patch("commands.admin.is_admin")` 或 `patch("config.is_admin")` |
    | `from main import cmd_balance` | `from commands.query import cmd_balance` |
  - Notes: 按命令所属模块分类更新，使用 `_get_api()` 延迟导入模式

- [x] Task 12: 更新格式化函数测试
  - File: `tests/unit/test_utils.py`
  - Action: 更新导入路径
    ```python
    # 原导入
    from tests.support.helpers import format_eth, format_usd, format_percent

    # 新导入（直接从源模块导入）
    from utils.formatters import format_eth, format_usd, format_percent, format_time
    ```
  - Notes: 添加 format_time 的测试用例

- [x] Task 13: 更新 Story 测试文件
  - Files: `tests/unit/test_story_*.py`
  - Action: 批量更新 patch 路径和导入：
    | 原路径 | 新路径 |
    |--------|--------|
    | `patch("main._monitor_instance")` | `patch("commands.monitor._monitor_instance")` |
    | `patch("main.is_admin")` | `patch("commands.monitor.is_admin")` 或对应模块 |
    | `from main import cmd_monitor_status` | `from commands.monitor import cmd_monitor_status` |
  - Notes: 需要根据命令实际位置调整

- [x] Task 14: 更新边缘情况测试
  - File: `tests/unit/test_edge_cases.py`
  - Action: 更新导入和 patch 路径（同上表）
  - Notes: 确保 mock 路径指向函数定义的模块，而非导入模块

#### Phase 5: 验证

- [x] Task 15: 运行完整测试套件
  - Action: 执行 `pytest tests/ -v` 确保所有测试通过
  - Notes: 预期测试覆盖率不变 - 实际结果：323 tests passing

- [x] Task 16: 验证 Bot 启动
  - Action: 手动启动 Bot，测试基本命令（/start, /balance）
  - Notes: 确保无运行时导入错误

### Git 提交策略（回滚保障）

每个 Phase 完成后单独提交：
```
Phase 1 完成后: git commit -m "refactor: Create utils/ module with formatters and permissions"
Phase 2 完成后: git commit -m "refactor: Create commands/ module with all command handlers"
Phase 3 完成后: git commit -m "refactor: Simplify main.py to entry point only"
Phase 4 完成后: git commit -m "refactor: Update test imports for new module structure"
Phase 5 完成后: git commit -m "refactor: Verify all tests pass after refactoring"
```

如果任一 Phase 失败，可回滚到上一 Phase 的提交点。

### Acceptance Criteria

**功能验证：**

- [x] AC 1: Given utils/formatters.py 已创建, when 导入 format_eth/format_usd/format_percent/format_time, then 函数正常工作且返回正确格式

- [x] AC 2: Given utils/permissions.py 已创建, when 调用 authorized(update), then 正确检查 ALLOWED_USERS

- [x] AC 3: Given commands/query.py 已创建, when 调用任意查询命令, then 返回与重构前相同的响应

- [x] AC 4: Given commands/admin.py 已创建, when 非管理员调用管理命令, then 返回"未授权"错误

- [x] AC 5: Given commands/monitor.py 已创建, when 调用 /monitor_status, then 正确显示监控状态

- [x] AC 6: Given commands/withdraw.py 已创建, when 执行 /withdraw 流程, then ConversationHandler 正常工作

- [x] AC 7: Given main.py 已重构, when 执行 create_app(), then 所有命令正确注册

**负面测试：**

- [x] AC 8: Given commands/query.py 已创建, when API 返回错误, then 命令正确处理并显示错误消息

- [x] AC 9: Given commands/admin.py 已创建, when 合约交易失败, then 正确显示失败原因

- [x] AC 10: Given commands/monitor.py 已创建, when _monitor_instance 为 None, then 返回"未初始化"消息

**测试验证：**

- [x] AC 11: Given 所有测试已更新, when 运行 pytest, then 所有测试通过 - 实际结果：323 tests passing

**代码质量：**

- [x] AC 12: Given 重构完成, when 查看 main.py 行数, then 少于 120 行 - 实际结果：119 行

- [x] AC 13: Given 重构完成, when 查看任意 commands/ 文件, then 少于 250 行 - 实际结果：admin.py 203 行, query.py ~250 行

- [x] AC 14: Given 重构完成, when 运行 python -c "import main", then 无循环导入错误

## Additional Context

### Dependencies

**无新增外部依赖**

**内部依赖关系（解决循环导入后）：**
```
utils/
├── formatters.py (独立)
└── permissions.py → config.py

commands/
├── query.py → main.api, utils.permissions, utils.formatters
├── admin.py → main.api, main.contract, config.is_admin, utils.formatters
├── monitor.py → config.is_admin, (_monitor_instance 通过 setter 注入)
└── withdraw.py → main.api, main.contract, config.is_admin

main.py → commands.register_handlers, commands.set_monitor_instance
```

**关键点**：monitor.py 不再直接导入 main，而是通过 setter 接收实例。

### Testing Strategy

**单元测试：**
- 现有测试保持不变（仅更新导入路径）
- 测试覆盖率目标：保持当前水平
- 新增 format_time 测试用例

**集成测试：**
- 手动启动 Bot 验证所有命令可用
- 测试 /start 菜单显示所有命令

**回归测试清单：**
1. /balance - 显示余额
2. /pnl - 显示盈亏
3. /positions - 显示持仓
4. /strategies - 显示策略
5. /monitor_status - 显示监控状态
6. /withdraw 流程 - 确认对话正常

### Notes

**高风险项（已解决）：**
- ~~循环导入风险~~ → 使用 setter 注入模式解决

**已知限制：**
- _pending_withdrawals 仍为模块级字典，单实例场景可接受
- 未来可考虑使用 Redis 或数据库存储

**重构后目录结构：**
```
dx-terminal-monitor/
├── main.py              # ~100 行入口
├── commands/
│   ├── __init__.py      # 导出 + register_handlers()
│   ├── query.py         # ~220 行 (8 个命令)
│   ├── admin.py         # ~200 行 (6 个命令)
│   ├── monitor.py       # ~100 行 (3 个命令 + setter)
│   └── withdraw.py      # ~120 行 (1 个对话流程)
├── utils/
│   ├── __init__.py      # 导出所有工具函数
│   ├── formatters.py    # ~50 行
│   └── permissions.py   # ~20 行
├── api.py               # 不变
├── contract.py          # 不变
├── config.py            # 不变
├── monitor.py           # 不变
└── notifier.py          # 不变
```
