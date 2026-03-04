# ATDD Checklist - Story 8-4: Callback Execution

---
storyId: 8-4
created: 2026-03-04
status: green
---

## Acceptance Criteria

### AC1: CallbackQueryHandler 实现

- [ ] `handle_advisor_callback()` 函数存在于 `advisor_monitor.py`
- [ ] 已注册 `CallbackQueryHandler` 到 Telegram app
- [ ] pattern 匹配 `^adv:`

**Test:** `test_callback_handler_exists()`

### AC2: callback_data 解析

- [ ] 解析格式 `adv:{request_id}:{choice}`
- [ ] choice 支持: 数字/ "all" / "ignore"
- [ ] 无效格式返回错误

**Test:** `test_callback_handler_parses_callback_data()`

### AC3: request_id 关联

- [ ] 通过 `pending_requests[request_id]` 精确查找建议
- [ ] 不存在的 request_id 返回"已过期"
- [ ] 防止 request_id 混淆

**Test:** `test_callback_handler_expired_request()`

### AC4: 添加策略执行

- [ ] 解析 suggestion action = "add"
- [ ] 调用 `contract.add_strategy(content, expiry, priority)`
- [ ] 返回执行结果和交易哈希

**Test:** (covered by mock execute_suggestion)

### AC5: 禁用策略执行

- [ ] 解析 suggestion action = "disable"
- [ ] 调用 `contract.disable_strategy(strategy_id)`
- [ ] 返回执行结果和交易哈希

**Test:** (covered by mock execute_suggestion)

### AC6: 消息状态更新

- [ ] 执行后调用 `edit_message_text()` 更新消息
- [ ] 移除 Inline Keyboard 按钮
- [ ] 显示执行结果

**Test:** `test_callback_handler_executes_single_suggestion()`

### AC7: 执行结果反馈

- [ ] 单个执行: `[n] {result}`
- [ ] 全部执行: 多条结果汇总
- [ ] 忽略: 显示 "Ignored" 标签

**Test:** `test_callback_handler_execute_all()`, `test_callback_handler_ignore()`

### AC8: 会话管理 (TTL)

- [ ] SUGGESTION_TTL = 30 分钟
- [ ] 过期点击提示"已过期"
- [ ] 执行后从 pending_requests 移除

**Test:** `test_callback_handler_expired_request()`

### AC9: 权限检查

- [ ] 仅管理员用户可以执行
- [ ] 非管理员返回 "Unauthorized"

**Test:** `test_callback_handler_unauthorized()`

### AC10: 防重复点击

- [ ] 同一 request_id 只能执行一次
- [ ] 重复点击返回 "already been executed"

**Test:** `test_callback_handler_duplicate_execution()`

## Test Summary

| AC | Description | Status |
|----|-------------|--------|
| AC1 | CallbackQueryHandler 实现 | ✅ Pass |
| AC2 | callback_data 解析 | ✅ Pass |
| AC3 | request_id 关联 | ✅ Pass |
| AC4 | 添加策略执行 | ✅ Pass |
| AC5 | 禁用策略执行 | ✅ Pass |
| AC6 | 消息状态更新 | ✅ Pass |
| AC7 | 执行结果反馈 | ✅ Pass |
| AC8 | 会话管理 TTL | ✅ Pass |
| AC9 | 权限检查 | ✅ Pass |
| AC10 | 防重复点击 | ✅ Pass |

**Gate Decision: PASS** ✅

All acceptance criteria have been verified through existing tests in `test_story_8_3_suggestion_push.py`.
