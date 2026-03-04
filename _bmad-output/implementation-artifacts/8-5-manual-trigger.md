# Story 8.5: 手动触发分析命令

Status: done

---

storyId: 8-5
title: 手动触发分析命令
epic: Epic 8 - AI Strategy Advisor
status: done
created: 2026-03-04
completed: 2026-03-04

---

## 概述

实现 `/advisor_analyze` 命令，允许用户手动触发 AI 分析，无需等待定时任务即可获得策略建议。

## Story

As a **用户**,
I want **通过 `/advisor_analyze` 命令手动触发 AI 分析**,
so that **不等待定时任务即可获得策略建议**.

## 验收标准

1. [x] 实现 `cmd_advisor_analyze` 命令处理函数
2. [x] 命令格式: `/advisor_analyze` (无参数)
3. [x] 调用 `StrategyAdvisor.analyze()` 执行分析
4. [x] 立即推送分析结果（带 Inline Keyboard）
5. [x] 管理员权限检查（仅管理员可执行）
6. [x] 防止频繁调用: 5 分钟内只能调用一次（冷却时间）
7. [x] 分析中显示 "正在分析..." 状态消息
8. [x] 无建议时返回友好提示: "No suggestions at this time"
9. [x] 错误时返回友好错误提示
10. [x] 添加单元测试

## Tasks / Subtasks

- [x] Task 1: 实现 cmd_advisor_analyze 命令 (AC: 1, 2, 3, 4, 5, 6, 7, 8, 9)
  - [x] 1.1 在 `commands/advisor.py` 添加 `_last_manual_analysis` 缓存和 `MANUAL_ANALYSIS_COOLDOWN` 常量
  - [x] 1.2 实现权限检查逻辑（复用现有 `is_admin()` 模式）
  - [x] 1.3 实现冷却时间检查逻辑
  - [x] 1.4 实现分析状态消息发送
  - [x] 1.5 调用 `StrategyAdvisor.analyze()` 执行分析
  - [x] 1.6 调用 `push_suggestions()` 推送结果（复用 Story 8-3 的推送逻辑）
  - [x] 1.7 处理无建议和错误情况

- [x] Task 2: 注册命令到 handlers (AC: 1)
  - [x] 2.1 在 `commands/__init__.py` 中导入 `cmd_advisor_analyze`
  - [x] 2.2 在 `register_handlers()` 中注册 CommandHandler
  - [x] 2.3 在 `__all__` 中导出命令

- [x] Task 3: 更新命令菜单 (AC: 1)
  - [x] 3.1 在 `main.py` 的 `post_init()` 中添加 `BotCommand("advisor_analyze", "Trigger AI analysis")`

- [x] Task 4: 添加单元测试
  - [x] 4.1 测试权限检查（非管理员被拒绝）
  - [x] 4.2 测试冷却时间（5分钟内重复调用被拒绝）
  - [x] 4.3 测试成功分析流程
  - [x] 4.4 测试无建议情况
  - [x] 4.5 测试错误处理

## Dev Notes

### 现有代码模式参考

1. **权限检查模式** (`commands/advisor.py` 行 28-31):
```python
if not is_admin(update.effective_user.id):
    await update.message.reply_text("Unauthorized: Admin only")
    return
```

2. **Advisor Monitor 访问模式** (`commands/advisor.py` 行 32-34):
```python
if _advisor_monitor is None:
    await update.message.reply_text("Advisor monitor not initialized")
    return
```

3. **状态检查模式** (`commands/advisor.py` 行 74-77):
```python
status = "Running" if _advisor_monitor.running else "Stopped"
interval = _advisor_monitor.interval_seconds // 3600
last = _advisor_monitor.last_analysis
```

4. **push_suggestions 调用模式** (`advisor_monitor.py` 行 121-161):
```python
async def push_suggestions(
    chat_id: int,
    suggestions: list[Suggestion] | list[dict],
    context: dict,
    bot: Bot
) -> str:
```

### 关键依赖

- `advisor_monitor._advisor_monitor` - 全局 AdvisorMonitor 实例
- `advisor_monitor.push_suggestions` - 推送建议消息函数
- `advisor.StrategyAdvisor.analyze()` - AI 分析方法
- `advisor.StrategyDataCollector.collect()` - 数据收集方法
- `config.is_admin()` - 权限检查函数

### 冷却时间实现

```python
from datetime import datetime, timedelta

_last_manual_analysis: dict[int, datetime] = {}
MANUAL_ANALYSIS_COOLDOWN = timedelta(minutes=5)

# 在命令处理函数中:
user_id = update.effective_user.id
last_time = _last_manual_analysis.get(user_id)
if last_time and datetime.now() - last_time < MANUAL_ANALYSIS_COOLDOWN:
    remaining = MANUAL_ANALYSIS_COOLDOWN - (datetime.now() - last_time)
    await update.message.reply_text(
        f"Please wait {int(remaining.total_seconds() // 60)} min before next analysis"
    )
    return
```

### 分析流程

```python
# 1. 发送状态消息
status_msg = await update.message.reply_text("Analyzing your portfolio...")

# 2. 执行分析
suggestions = await _advisor_monitor.advisor.analyze()

# 3. 处理无建议
if not suggestions:
    await status_msg.edit_text("No suggestions at this time. Your portfolio looks good!")
    return

# 4. 收集上下文并推送
context = await _advisor_monitor.advisor.collector.collect()
request_id = await push_suggestions(
    chat_id=update.effective_chat.id,
    suggestions=suggestions,
    bot=ctx.bot,
    context=context
)

# 5. 更新状态消息
await status_msg.edit_text(f"Analysis complete! {len(suggestions)} suggestion(s) generated.")

# 6. 记录调用时间
_last_manual_analysis[user_id] = datetime.now()
```

### Project Structure Notes

- 命令文件位置: `commands/advisor.py`
- 命令注册位置: `commands/__init__.py`
- 菜单配置位置: `main.py` 的 `post_init()` 函数
- 测试文件位置: `tests/unit/` 目录

### 测试文件命名

建议创建: `tests/unit/test_story_8_5_manual_trigger.py`

### References

- [Source: commands/advisor.py] - 现有 advisor 命令模式
- [Source: advisor_monitor.py] - push_suggestions 函数和 AdvisorMonitor 类
- [Source: advisor.py] - StrategyAdvisor.analyze() 方法
- [Source: main.py#post_init] - 命令菜单注册
- [Source: commands/__init__.py] - 命令注册模式
- [Source: _bmad-output/planning-artifacts/epics.md#Story-8.5] - Story 定义

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6 (claude-opus-4-6)

### Debug Log References

- Test execution: `pytest tests/unit/test_story_8_5_manual_trigger.py -v`
- All 10 tests passed in 0.46s

### Completion Notes List

1. **Implementation completed in `commands/advisor.py`:**
   - Added `_last_manual_analysis` dict for cooldown tracking
   - Added `MANUAL_ANALYSIS_COOLDOWN = timedelta(minutes=5)` constant
   - Implemented `cmd_advisor_analyze()` function with:
     - Admin permission check via `is_admin()`
     - 5-minute cooldown enforcement per user
     - Monitor initialization check
     - Status message display ("Analyzing your portfolio...")
     - Integration with `StrategyAdvisor.analyze()`
     - Push suggestions via `push_suggestions()` from advisor_monitor
     - No suggestions handling with friendly message
     - Error handling with logger.error

2. **Key Design Decisions:**
   - Cooldown check placed BEFORE monitor initialization check to prevent spam even when monitor is unavailable
   - Cooldown is recorded on successful analysis AND when no suggestions are returned
   - Status message is editable (uses `edit_text()`) for in-place updates

3. **Test Coverage:**
   - 10 unit tests covering all acceptance criteria
   - Tests use proper mocking of `_advisor_monitor` and `push_suggestions`
   - Both success and error paths are covered

### File List

Modified files:
- `commands/advisor.py` - Added cmd_advisor_analyze function, cooldown constants, and tracking dict
- `commands/__init__.py` - Imported and registered cmd_advisor_analyze command
- `main.py` - Added "advisor_analyze" to BotCommand menu in post_init()
- `tests/unit/test_story_8_5_manual_trigger.py` - Unit tests (10 tests, all passing)
