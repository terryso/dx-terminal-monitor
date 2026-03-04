# Story 8-4: 建议确认执行 (Inline Keyboard 回调)

---
storyId: 8-4
title: 建议确认执行 (Inline Keyboard 回调)
epic: Epic 8 - AI Strategy Advisor
status: done
created: 2026-03-04
---

## 概述

实现 Inline Keyboard 回调处理，允许用户通过点击按钮执行 AI 建议，快速应用策略变更。

## 实现位置

- `advisor_monitor.py` - `handle_advisor_callback()` 函数 (行 332-423)
- `commands/advisor.py` - 委托函数 (行 88-91)
- `main.py` - 注册 CallbackQueryHandler (行 137)

## 验收标准完成情况

| AC | 描述 | 状态 |
|----|------|------|
| 1 | 实现 `CallbackQueryHandler` 处理按钮点击 | ✅ |
| 2 | 解析 callback_data 格式: `adv:{request_id}:{choice}` | ✅ |
| 3 | 通过 `request_id` 精确关联建议 | ✅ |
| 4 | 执行添加策略: 调用 `contract.add_strategy()` | ✅ |
| 5 | 执行禁用策略: 调用 `contract.disable_strategy()` | ✅ |
| 6 | 点击后更新按钮状态为"已执行" | ✅ |
| 7 | 执行结果反馈 | ✅ |
| 8 | 会话管理: 建议有效期 30 分钟 | ✅ |
| 9 | 权限检查: 仅管理员按钮有效 | ✅ |
| 10 | 防重复点击 | ✅ |

## 关键实现

### callback_data 格式

```
adv:{request_id}:{choice}
- choice = 1/2/3... 执行单个建议
- choice = "all" 执行所有建议
- choice = "ignore" 忽略
```

### 核心逻辑

```python
async def handle_advisor_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    # 1. 权限检查
    if not is_admin(user_id):
        return

    # 2. 解析 callback_data
    _, request_id, choice = query.data.split(":")

    # 3. 查找建议
    request = pending_requests.get(request_id)

    # 4. 检查有效期 (30分钟 TTL)
    if datetime.now() - request["created_at"] > SUGGESTION_TTL:
        return

    # 5. 防重复执行
    if request.get("executed"):
        return

    # 6. 执行操作
    if choice == "ignore":
        # 忽略
    elif choice == "all":
        # 执行所有建议
    else:
        # 执行单个建议
        result = await execute_suggestion(suggestion)

    # 7. 更新消息
    await query.edit_message_text(...)
```

## 测试覆盖

测试位于 `tests/unit/test_story_8_3_suggestion_push.py`:

- `TestCallbackQueryHandler` 类
- 测试 callback 解析、权限检查、过期处理、重复执行防护
- 测试单个执行、全部执行、忽略操作

## 依赖关系

- 依赖 Story 8-3 (建议推送)
- 依赖 Story 8-2 (AI 分析)
- 依赖 Epic 1 (contract.py)

## 完成时间

2026-03-04
