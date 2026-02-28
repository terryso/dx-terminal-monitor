# Story 1.3: 更新命令菜单和帮助文档

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

作为**用户**，我需要**在帮助菜单中看到新命令**，以便**知道可以使用哪些功能**。

## Acceptance Criteria

1. `/start` 命令包含新命令说明
2. `post_init()` 注册新命令到 Telegram 菜单
3. 更新 `tests/unit/test_edge_cases.py` 中的 `test_post_init_sets_commands`

## Tasks / Subtasks

- [x] **Task 1: 验证 /start 帮助文本包含新命令** (AC: #1)
  - [x] 验证 `cmd_start` 函数包含 `/disable_strategy <id>` 说明
  - [x] 验证 `cmd_start` 函数包含 `/disable_all` 说明

- [x] **Task 2: 验证 post_init 注册新命令到菜单** (AC: #2)
  - [x] 验证 `post_init` 函数包含 `BotCommand("disable_strategy", "Disable strategy")`
  - [x] 验证 `post_init` 函数包含 `BotCommand("disable_all", "Disable all strategies")`

- [x] **Task 3: 更新 test_post_init_sets_commands 测试** (AC: #3)
  - [x] 在 `tests/unit/test_edge_cases.py` 的 `test_post_init_sets_commands` 测试中
  - [x] 添加对 `disable_strategy` 命令的断言
  - [x] 添加对 `disable_all` 命令的断言

## Dev Notes

### 当前实现状态分析

**重要发现**: 此 Story 的主要功能已在 Story 1-1 和 Story 1-2 中实现完毕！

已完成的实现（在之前的 Story 中）:
- `main.py:253-267` - `post_init()` 已注册新命令
- `main.py:72-86` - `cmd_start` 已包含新命令帮助文本
- `main.py:330-344` - `create_app()` 已注册命令处理器

**本 Story 的剩余工作**: 仅需更新测试以验证新命令已正确注册。

### 技术栈要求

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | >=3.12 | 主要开发语言 |
| python-telegram-bot | >=21.0 | Telegram Bot API |
| pytest | >=8.0 | 测试框架 |

### 验证现有实现

**main.py - post_init 函数 (第 253-267 行):**
```python
async def post_init(app: Application):
    commands = [
        BotCommand("start", "Help"),
        BotCommand("balance", "Balance"),
        BotCommand("pnl", "PnL"),
        BotCommand("positions", "Positions"),
        BotCommand("activity", "Activity"),
        BotCommand("swaps", "Swaps"),
        BotCommand("strategies", "Strategies"),
        BotCommand("vault", "Vault info"),
        BotCommand("disable_strategy", "Disable strategy"),      # 已存在
        BotCommand("disable_all", "Disable all strategies"),     # 已存在
    ]
    await app.bot.set_my_commands(commands)
    logger.info("Commands menu set")
```

**main.py - cmd_start 帮助文本 (第 72-86 行):**
```python
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not authorized(update):
        await update.message.reply_text("Unauthorized")
        return
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
/disable_strategy <id> - Disable a specific strategy    # 已存在
/disable_all - Disable all active strategies             # 已存在
"""
    await update.message.reply_text(help_text)
```

### 测试更新要求

**当前测试问题**: `tests/unit/test_edge_cases.py:79-102` 的 `test_post_init_sets_commands` 只验证了 8 个命令，未包含新增的 `disable_strategy` 和 `disable_all`。

**需要修改的测试**:

```python
# tests/unit/test_edge_cases.py
class TestPostInit:
    """Tests for post_init function."""

    @pytest.mark.asyncio
    async def test_post_init_sets_commands(self) -> None:
        """Test post_init sets bot commands."""
        # Given
        mock_app = MagicMock()
        mock_app.bot = AsyncMock()

        from main import post_init

        # When
        await post_init(mock_app)

        # Then
        mock_app.bot.set_my_commands.assert_called_once()
        call_args = mock_app.bot.set_my_commands.call_args[0][0]
        command_names = [cmd.command for cmd in call_args]
        assert "start" in command_names
        assert "balance" in command_names
        assert "pnl" in command_names
        assert "positions" in command_names
        assert "activity" in command_names
        assert "swaps" in command_names
        assert "strategies" in command_names
        assert "vault" in command_names
        # 添加以下两行，验证新命令已注册
        assert "disable_strategy" in command_names
        assert "disable_all" in command_names
```

### Project Structure Notes

**修改现有文件:**
```
dx-terminal-monitor/
├── main.py              # 无需修改 - 已包含所有必需代码
└── tests/
    └── unit/
        └── test_edge_cases.py  # 修改 - 添加对 disable_strategy 和 disable_all 的断言
```

### Previous Story Intelligence (from Story 1-1, 1-2)

**已建立的代码模式:**
- 命令注册在 `post_init()` 函数中使用 `BotCommand` 列表
- 帮助文本在 `cmd_start` 函数中使用多行字符串
- 命令处理器在 `create_app()` 函数中注册

**测试模式:**
- 使用 `pytest.mark.asyncio` 装饰器
- 使用 `MagicMock` 和 `AsyncMock` 模拟对象
- 通过 `command.command` 属性获取命令名称

**Code Review 遗留问题 (Story 1-2):**
- [HIGH] disabledCount always returns 0 - 不影响此 Story
- [MEDIUM] 帮助文本语言一致性已在 Story 1-2 中修复

### 实施顺序

由于主要功能已实现，本 Story 的步骤如下:

1. **验证** - 确认 `post_init` 和 `cmd_start` 已包含新命令
2. **更新测试** - 在 `test_post_init_sets_commands` 添加新命令断言
3. **运行测试** - 确保所有测试通过

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story1.3]
- [Source: main.py:253-267 - post_init 函数]
- [Source: main.py:72-86 - cmd_start 帮助文本]
- [Source: tests/unit/test_edge_cases.py:79-102 - test_post_init_sets_commands 测试]
- [Source: _bmad-output/implementation-artifacts/1-1-disable-strategy.md - Story 1-1 参考]
- [Source: _bmad-output/implementation-artifacts/1-2-disable-all-strategies.md - Story 1-2 参考]

## Change Log

**2026-03-01** - Story 1-3 Implementation Complete
- Verified main.py contains all required functionality (implemented in Stories 1-1, 1-2)
- Updated tests/unit/test_edge_cases.py with new command assertions
- Created tests/unit/test_story_1_3_menu_help.py with comprehensive AC tests
- All 138 tests passing

**2026-03-01** - Code Review Complete (yolo mode)
- All 3 Acceptance Criteria verified: IMPLEMENTED ✅
- All 3 Tasks verified: COMPLETE ✅
- Fixed: File List updated to include sprint-status.yaml and ATTD checklist
- Story status updated: review → done
- Sprint status synced: 1-3-update-menu-help → done

## Dev Agent Record

### Agent Model Used

GLM-5 (Claude Code)

### Debug Log References

无

### Completion Notes List

**Story 1-3 Implementation Summary:**

本 Story 的主要功能已在之前的 Story 1-1 和 1-2 中实现完毕。本 Story 主要工作是验证和测试。

1. **验证完成的功能:**
   - `main.py:72-86` - `cmd_start` 帮助文本已包含新命令说明
   - `main.py:253-267` - `post_init` 已注册新命令到 Telegram 菜单
   - `main.py:330-344` - `create_app` 已注册命令处理器

2. **测试更新:**
   - `tests/unit/test_edge_cases.py:102-104` - 添加了对 `disable_strategy` 和 `disable_all` 的断言
   - 创建了 `tests/unit/test_story_1_3_menu_help.py` - 全面的 Story 1-3 专用测试

3. **验证结果:**
   - 所有 138 个测试通过
   - 所有验收标准已满足

### File List

**Modified:**
- `tests/unit/test_edge_cases.py` - Updated test_post_init_sets_commands to include disable_strategy and disable_all assertions
- `_bmad-output/implementation-artifacts/sprint-status.yaml` - Story status updated to review

**Added:**
- `tests/unit/test_story_1_3_menu_help.py` - Comprehensive tests for Story 1-3 acceptance criteria
- `_bmad-output/test-artifacts/atdd-checklist-1-3.md` - ATTD checklist generated during development

**No changes needed (already implemented in Story 1-1, 1-2):**
- `main.py` - All required functionality already present
