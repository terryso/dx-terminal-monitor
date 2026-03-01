---
stepsCompleted:
  - step-01-preflight-and-context
  - step-02-generation-mode
  - step-03-test-strategy
  - step-04-generate-tests
lastStep: step-04-generate-tests
lastSaved: '2026-03-01'
workflowType: 'testarch-atdd'
inputDocuments:
  - _bmad-output/implementation-artifacts/4-2-tg-message-push.md
  - monitor.py
  - config.py
  - api.py
---

# ATDD Checklist - Epic 4, Story 2: TG 消息推送

**Date:** 2026-03-01
**Author:** Nick
**Primary Test Level:** Unit (Backend Python)

---

## Story Summary

实现 Telegram 通知功能，当 Agent 执行操作时自动推送消息到用户。

**As a** 用户
**I want** 当 Agent 执行操作时收到 TG 通知
**So that** 及时了解交易动态

---

## Acceptance Criteria

1. 实现 `format_activity_message()` 格式化活动消息
2. 支持格式化 Swap/Deposit/Withdrawal 三种类型
3. 推送到 `.env` 配置的 `ADMIN_USERS` 或 `ALLOWED_USERS`
4. 消息包含: 操作类型、时间、金额/数量、交易链接
5. 添加单元测试

---

## Failing Tests Created (RED Phase)

### Unit Tests (28 tests)

**File:** `tests/unit/test_story_4_2_notifier.py` (28 tests)

**Test Classes:**

- ✅ **TestFormatActivityMessageExists** (2 tests)
  - Status: SKIPPED - notifier.py not yet implemented
  - Verifies: AC1 - 函数存在且返回字符串

- ✅ **TestFormatSwapMessage** (5 tests)
  - Status: SKIPPED - notifier.py not yet implemented
  - Verifies: AC2, AC4 - Swap 消息格式化

- ✅ **TestFormatDepositMessage** (2 tests)
  - Status: SKIPPED - notifier.py not yet implemented
  - Verifies: AC2, AC4 - Deposit 消息格式化

- ✅ **TestFormatWithdrawalMessage** (2 tests)
  - Status: SKIPPED - notifier.py not yet implemented
  - Verifies: AC2, AC4 - Withdrawal 消息格式化

- ✅ **TestFormatUnknownType** (1 test)
  - Status: SKIPPED - notifier.py not yet implemented
  - Verifies: 边界情况 - 未知类型处理

- ✅ **TestTelegramNotifierUserSelection** (2 tests)
  - Status: SKIPPED - notifier.py not yet implemented
  - Verifies: AC3 - 用户选择逻辑

- ✅ **TestTelegramNotifierSendNotification** (3 tests)
  - Status: SKIPPED - notifier.py not yet implemented
  - Verifies: AC3 - 发送通知逻辑

- ✅ **TestMessageContent** (4 tests)
  - Status: SKIPPED - notifier.py not yet implemented
  - Verifies: AC4 - 消息内容完整性

- ✅ **TestEtherscanUrlGeneration** (2 tests)
  - Status: SKIPPED - notifier.py not yet implemented
  - Verifies: AC4 - 交易链接生成

- ✅ **TestHelperFunctions** (5 tests)
  - Status: SKIPPED - notifier.py not yet implemented
  - Verifies: 辅助函数正确性

---

## Implementation Checklist

### Task 1: 创建 notifier.py 基础结构

**File:** `notifier.py`

**Tasks to make tests pass:**

- [ ] 创建 `notifier.py` 文件
- [ ] 实现 `format_eth(wei: str) -> str` 函数
- [ ] 实现 `format_usd(value) -> str` 函数
- [ ] 实现 `format_timestamp(ts: str) -> str` 函数
- [ ] 实现 `get_tx_url(tx_hash: str) -> str` 函数
- [ ] 实现 `format_activity_message(activity: Dict) -> str` 函数
- [ ] 实现 `TelegramNotifier` 类
- [ ] 实现 `TelegramNotifier.__init__(bot, notify_users)` 方法
- [ ] 实现 `TelegramNotifier.send_notification(activity)` 异步方法
- [ ] Run test: `python -m pytest tests/unit/test_story_4_2_notifier.py -v`
- [ ] ✅ All tests pass (green phase)

**Estimated Effort:** 1-2 hours

---

### Task 2: 集成到 main.py

**File:** `main.py`

**Tasks to make integration work:**

- [ ] 添加 `from notifier import TelegramNotifier` 导入
- [ ] 创建全局变量 `_notifier_instance`
- [ ] 实现 `on_new_activity(activity)` 回调函数
- [ ] 在 `post_init` 中初始化 `TelegramNotifier`
- [ ] 将回调传递给 `ActivityMonitor`
- [ ] Run test: `python -m pytest tests/unit/test_story_4_2_notifier.py -v`
- [ ] ✅ All tests pass (green phase)

**Estimated Effort:** 0.5 hours

---

### Task 3: 更新配置文件

**Files:** `config.py`, `.env.example`

**Tasks:**

- [ ] 在 `config.py` 添加 `NOTIFY_USERS` 环境变量读取
- [ ] 在 `.env.example` 添加 `NOTIFY_USERS` 配置说明
- [ ] Run test: `python -m pytest tests/unit/test_story_4_2_notifier.py -v`
- [ ] ✅ All tests pass (green phase)

**Estimated Effort:** 0.25 hours

---

## Running Tests

```bash
# Run all failing tests for this story
python -m pytest tests/unit/test_story_4_2_notifier.py -v

# Run specific test class
python -m pytest tests/unit/test_story_4_2_notifier.py::TestFormatSwapMessage -v

# Run with coverage
python -m pytest tests/unit/test_story_4_2_notifier.py --cov=notifier --cov-report=term-missing

# Run all tests and see skipped reasons
python -m pytest tests/unit/test_story_4_2_notifier.py -v -rs
```

---

## Red-Green-Refactor Workflow

### RED Phase (Complete) ✅

**TEA Agent Responsibilities:**

- ✅ All tests written and skipped (awaiting implementation)
- ✅ Tests cover all acceptance criteria
- ✅ Helper function tests included
- ✅ Edge cases covered (unknown type, no users, invalid input)
- ✅ Implementation checklist created

**Verification:**

- All tests are SKIPPED because `notifier.py` does not exist
- Failure reason is clear: "TDD RED PHASE: notifier.py not yet implemented"
- Tests will pass once feature is implemented

---

### GREEN Phase (DEV Team - Next Steps)

**DEV Agent Responsibilities:**

1. **Pick one failing test group** from implementation checklist
2. **Read the test** to understand expected behavior
3. **Implement minimal code** to make those tests pass
4. **Run the test** to verify it now passes (green)
5. **Check off the task** in implementation checklist
6. **Move to next test group** and repeat

**Key Principles:**

- Start with helper functions (format_eth, format_usd, etc.)
- Then implement format_activity_message
- Finally implement TelegramNotifier class
- Run tests frequently (immediate feedback)

---

## Next Steps

1. **Run failing tests** to confirm RED phase: `python -m pytest tests/unit/test_story_4_2_notifier.py -v`
2. **Begin implementation** using implementation checklist as guide
3. **Start with helper functions** (format_eth, format_usd, etc.)
4. **Work one test class at a time** (red → green for each)
5. **When all tests pass**, run code review workflow
6. **When code review passes**, update story status to 'done' in sprint-status.yaml

---

## Notes

- **前置依赖**: Story 4-1 (ActivityMonitor) 已完成
- **后续依赖**: Story 4-3 (监控控制命令) 需要本 Story 的 `_monitor_instance`
- 测试使用 `pytest.mark.skipif` 实现 TDD RED PHASE
- 所有测试将在 `notifier.py` 实现后自动启用

---

**Generated by BMad TEA Agent** - 2026-03-01
