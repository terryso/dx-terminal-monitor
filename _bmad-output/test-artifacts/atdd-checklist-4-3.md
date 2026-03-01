---
stepsCompleted:
  - step-01-preflight-and-context
  - step-02-generation-mode
  - step-03-test-strategy
  - step-04-generate-tests
  - step-04c-aggregate
lastStep: 'step-04c-aggregate'
lastSaved: '2026-03-01'
workflowType: 'testarch-atdd'
inputDocuments:
  - '_bmad-output/implementation-artifacts/4-3-monitor-control-commands.md'
  - '_bmad/tea/testarch/knowledge/data-factories.md'
  - '_bmad/tea/testarch/knowledge/test-quality.md'
  - '_bmad/tea/testarch/knowledge/test-healing-patterns.md'
  - '_bmad/tea/testarch/knowledge/test-levels-framework.md'
  - 'tests/conftest.py'
  - 'tests/unit/test_story_4_1_monitor.py'
---

# ATDD Checklist - Epic 4, Story 3: Monitor Control Commands

**Date:** 2026-03-01
**Author:** Nick
**Primary Test Level:** Unit

---

## Story Summary

作为**用户**,我需要**通过命令控制监控服务的开启/关闭**,以便**灵活管理推送**。

**As a** user
**I want** to control the monitoring service via commands (start/stop/status)
**So that** I can flexibly manage push notifications

---

## Acceptance Criteria

1. 实现 `/monitor_start` 命令启动监控
2. 实现 `/monitor_stop` 命令停止监控
3. 实现 `/monitor_status` 命令查看状态
4. 管理员权限检查
5. Bot 启动时自动开始监控 (可配置)
6. 添加单元测试

---

## Test Strategy

### Level Selection Rationale

| AC | Scenario | Level | Justification |
|----|----------|-------|---------------|
| #1 | /monitor_start command | Unit | Command handler logic, no browser needed |
| #2 | /monitor_stop command | Unit | Command handler logic, no browser needed |
| #3 | /monitor_status command | Unit | Command handler logic, no browser needed |
| #4 | Admin permission check | Unit | Pure authorization logic |
| #5 | AUTO_START_MONITOR config | Unit | Environment variable configuration |
| #6 | Full test coverage | Unit | All scenarios covered at unit level |

### Priority Assignment

- **P0 (Critical):** Admin permission checks - Security requirement
- **P0 (Critical):** /monitor_status - Primary user-facing command
- **P1 (High):** /monitor_start - Essential control command
- **P1 (High):** /monitor_stop - Essential control command
- **P2 (Medium):** AUTO_START_MONITOR - Configuration flexibility
- **P2 (Medium):** Edge cases (already running, already stopped)

---

## Failing Tests Created (RED Phase)

### Unit Tests (20 tests)

**File:** `tests/unit/test_story_4_3_monitor_commands.py` (~400 lines)

#### Test Class: TestMonitorStatusCommand

| Test ID | Test Name | Status | Verifies |
|---------|-----------|--------|----------|
| 4.3-UNIT-001 | test_monitor_status_running | RED | AC#3 - Shows running state |
| 4.3-UNIT-002 | test_monitor_status_stopped | RED | AC#3 - Shows stopped state |
| 4.3-UNIT-003 | test_monitor_status_not_initialized | RED | AC#3 - Handles uninitialized |
| 4.3-UNIT-004 | test_monitor_status_includes_interval | RED | AC#3 - Displays poll interval |
| 4.3-UNIT-005 | test_monitor_status_includes_seen_count | RED | AC#3 - Displays processed count |

#### Test Class: TestMonitorStartCommand

| Test ID | Test Name | Status | Verifies |
|---------|-----------|--------|----------|
| 4.3-UNIT-006 | test_monitor_start_success | RED | AC#1 - Starts monitor |
| 4.3-UNIT-007 | test_monitor_start_already_running | RED | AC#1 - Handles already running |
| 4.3-UNIT-008 | test_monitor_start_not_initialized | RED | AC#1 - Handles uninitialized |
| 4.3-UNIT-009 | test_monitor_start_calls_start_background | RED | AC#1 - Calls correct method |

#### Test Class: TestMonitorStopCommand

| Test ID | Test Name | Status | Verifies |
|---------|-----------|--------|----------|
| 4.3-UNIT-010 | test_monitor_stop_success | RED | AC#2 - Stops monitor |
| 4.3-UNIT-011 | test_monitor_stop_already_stopped | RED | AC#2 - Handles already stopped |
| 4.3-UNIT-012 | test_monitor_stop_not_initialized | RED | AC#2 - Handles uninitialized |
| 4.3-UNIT-013 | test_monitor_stop_calls_stop_method | RED | AC#2 - Calls correct method |

#### Test Class: TestAdminPermissionChecks

| Test ID | Test Name | Status | Verifies |
|---------|-----------|--------|----------|
| 4.3-UNIT-014 | test_status_denies_non_admin | RED | AC#4 - Permission check |
| 4.3-UNIT-015 | test_start_denies_non_admin | RED | AC#4 - Permission check |
| 4.3-UNIT-016 | test_stop_denies_non_admin | RED | AC#4 - Permission check |
| 4.3-UNIT-017 | test_all_commands_check_admin | RED | AC#4 - All commands protected |

#### Test Class: TestAutoStartConfiguration

| Test ID | Test Name | Status | Verifies |
|---------|-----------|--------|----------|
| 4.3-UNIT-018 | test_auto_start_enabled | RED | AC#5 - Auto-start when true |
| 4.3-UNIT-019 | test_auto_start_disabled | RED | AC#5 - No auto-start when false |
| 4.3-UNIT-020 | test_auto_start_default_true | RED | AC#5 - Default is true |

---

## Data Factories Created

### MonitorStateFactory

**File:** `tests/support/factories/monitor_state.factory.py` (new)

**Exports:**

- `create_monitor_state(running=True, poll_interval=30, seen_count=0)` - Create monitor state with defaults
- `create_running_monitor_state()` - Preconfigured running state
- `create_stopped_monitor_state()` - Preconfigured stopped state

**Example Usage:**

```python
from tests.support.factories.monitor_state.factory import create_monitor_state

state = create_monitor_state(running=True, poll_interval=60, seen_count=10)
# {'running': True, 'poll_interval': 60, 'seen_ids': set of 10 ids}
```

---

## Fixtures Created

### Monitor Command Fixtures

**File:** `tests/support/fixtures/monitor_commands.fixture.py` (new)

**Fixtures:**

- `mock_monitor_instance` - Mock ActivityMonitor with controllable state
  - **Setup:** Creates MagicMock with running, poll_interval, seen_ids attributes
  - **Provides:** Mocked _monitor_instance for command testing
  - **Cleanup:** Automatic via pytest fixture scope

**Example Usage:**

```python
from tests.support.fixtures.monitor_commands.fixture import mock_monitor_instance

@pytest.mark.asyncio
async def test_something(mock_monitor_instance):
    mock_monitor_instance.running = True
    # mock_monitor_instance is ready to use
```

---

## Mock Requirements

### telegram.update.Mock

**Mock Object:** `unittest.mock.MagicMock`

**Attributes:**
- `effective_user.id` - User ID (int)
- `message.reply_text` - AsyncMock for response

### telegram.context.Mock

**Mock Object:** `unittest.mock.MagicMock`

**Attributes:**
- `bot` - AsyncMock for bot actions

### config.is_admin Mock

**Function:** `unittest.mock.patch`

**Behavior:**
- `return_value=True` - Admin user
- `return_value=False` - Non-admin user

---

## Implementation Checklist

### Test: test_monitor_status_running (4.3-UNIT-001)

**File:** `tests/unit/test_story_4_3_monitor_commands.py`

**Tasks to make this test pass:**

- [ ] Implement `cmd_monitor_status` function in `main.py`
- [ ] Check admin permission using `is_admin()`
- [ ] Return status message with "运行中" when `running=True`
- [ ] Include poll interval in message
- [ ] Include seen_ids count in message
- [ ] Run test: `pytest tests/unit/test_story_4_3_monitor_commands.py::TestMonitorStatusCommand::test_monitor_status_running -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 0.5 hours

---

### Test: test_monitor_status_stopped (4.3-UNIT-002)

**File:** `tests/unit/test_story_4_3_monitor_commands.py`

**Tasks to make this test pass:**

- [ ] Return status message with "已停止" when `running=False`
- [ ] Run test: `pytest tests/unit/test_story_4_3_monitor_commands.py::TestMonitorStatusCommand::test_monitor_status_stopped -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 0.25 hours

---

### Test: test_monitor_status_not_initialized (4.3-UNIT-003)

**File:** `tests/unit/test_story_4_3_monitor_commands.py`

**Tasks to make this test pass:**

- [ ] Handle case when `_monitor_instance is None`
- [ ] Return "监控服务未初始化" message
- [ ] Run test: `pytest tests/unit/test_story_4_3_monitor_commands.py::TestMonitorStatusCommand::test_monitor_status_not_initialized -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 0.25 hours

---

### Test: test_monitor_start_success (4.3-UNIT-006)

**File:** `tests/unit/test_story_4_3_monitor_commands.py`

**Tasks to make this test pass:**

- [ ] Implement `cmd_monitor_start` function in `main.py`
- [ ] Check admin permission using `is_admin()`
- [ ] Check monitor is initialized
- [ ] Call `_monitor_instance.start_background()` when not running
- [ ] Return "已启动" confirmation message
- [ ] Run test: `pytest tests/unit/test_story_4_3_monitor_commands.py::TestMonitorStartCommand::test_monitor_start_success -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 0.5 hours

---

### Test: test_monitor_start_already_running (4.3-UNIT-007)

**File:** `tests/unit/test_story_4_3_monitor_commands.py`

**Tasks to make this test pass:**

- [ ] Check if monitor is already running before starting
- [ ] Return "已在运行中" message when already running
- [ ] Run test: `pytest tests/unit/test_story_4_3_monitor_commands.py::TestMonitorStartCommand::test_monitor_start_already_running -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 0.25 hours

---

### Test: test_monitor_stop_success (4.3-UNIT-010)

**File:** `tests/unit/test_story_4_3_monitor_commands.py`

**Tasks to make this test pass:**

- [ ] Implement `cmd_monitor_stop` function in `main.py`
- [ ] Check admin permission using `is_admin()`
- [ ] Check monitor is initialized
- [ ] Call `_monitor_instance.stop()` when running
- [ ] Return "已停止" confirmation message
- [ ] Run test: `pytest tests/unit/test_story_4_3_monitor_commands.py::TestMonitorStopCommand::test_monitor_stop_success -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 0.5 hours

---

### Test: test_monitor_stop_already_stopped (4.3-UNIT-011)

**File:** `tests/unit/test_story_4_3_monitor_commands.py`

**Tasks to make this test pass:**

- [ ] Check if monitor is already stopped before stopping
- [ ] Return "已处于停止状态" message when already stopped
- [ ] Run test: `pytest tests/unit/test_story_4_3_monitor_commands.py::TestMonitorStopCommand::test_monitor_stop_already_stopped -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 0.25 hours

---

### Test: test_status_denies_non_admin (4.3-UNIT-014)

**File:** `tests/unit/test_story_4_3_monitor_commands.py`

**Tasks to make this test pass:**

- [ ] Add `is_admin()` check at start of `cmd_monitor_status`
- [ ] Return "未授权: 仅管理员可查看监控状态" when check fails
- [ ] Run test: `pytest tests/unit/test_story_4_3_monitor_commands.py::TestAdminPermissionChecks::test_status_denies_non_admin -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 0.25 hours

---

### Test: test_start_denies_non_admin (4.3-UNIT-015)

**File:** `tests/unit/test_story_4_3_monitor_commands.py`

**Tasks to make this test pass:**

- [ ] Add `is_admin()` check at start of `cmd_monitor_start`
- [ ] Return "未授权: 仅管理员可启动监控" when check fails
- [ ] Run test: `pytest tests/unit/test_story_4_3_monitor_commands.py::TestAdminPermissionChecks::test_start_denies_non_admin -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 0.25 hours

---

### Test: test_stop_denies_non_admin (4.3-UNIT-016)

**File:** `tests/unit/test_story_4_3_monitor_commands.py`

**Tasks to make this test pass:**

- [ ] Add `is_admin()` check at start of `cmd_monitor_stop`
- [ ] Return "未授权: 仅管理员可停止监控" when check fails
- [ ] Run test: `pytest tests/unit/test_story_4_3_monitor_commands.py::TestAdminPermissionChecks::test_stop_denies_non_admin -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 0.25 hours

---

### Test: test_auto_start_enabled (4.3-UNIT-018)

**File:** `tests/unit/test_story_4_3_monitor_commands.py`

**Tasks to make this test pass:**

- [ ] Add `AUTO_START_MONITOR` to `config.py`
- [ ] Read from environment with default `true`
- [ ] Update `post_init()` to check config before starting
- [ ] Run test: `pytest tests/unit/test_story_4_3_monitor_commands.py::TestAutoStartConfiguration::test_auto_start_enabled -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 0.5 hours

---

### Test: test_auto_start_disabled (4.3-UNIT-019)

**File:** `tests/unit/test_story_4_3_monitor_commands.py`

**Tasks to make this test pass:**

- [ ] Ensure `AUTO_START_MONITOR=false` prevents auto-start
- [ ] Monitor should be initialized but not started
- [ ] Run test: `pytest tests/unit/test_story_4_3_monitor_commands.py::TestAutoStartConfiguration::test_auto_start_disabled -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 0.25 hours

---

### Task: Update Command Menu

**Tasks:**

- [ ] Add `BotCommand("monitor_status", "Check monitor status")` to command list
- [ ] Add `BotCommand("monitor_start", "Start activity monitor")` to command list
- [ ] Add `BotCommand("monitor_stop", "Stop activity monitor")` to command list
- [ ] Update `/start` help text with new commands
- [ ] Register command handlers in `create_app()`

**Estimated Effort:** 0.25 hours

---

### Task: Update .env.example

**Tasks:**

- [ ] Add `AUTO_START_MONITOR=true` with description

**Estimated Effort:** 0.1 hours

---

## Running Tests

```bash
# Run all failing tests for this story
pytest tests/unit/test_story_4_3_monitor_commands.py -v

# Run specific test class
pytest tests/unit/test_story_4_3_monitor_commands.py::TestMonitorStatusCommand -v

# Run specific test
pytest tests/unit/test_story_4_3_monitor_commands.py::TestMonitorStatusCommand::test_monitor_status_running -v

# Run with coverage
pytest tests/unit/test_story_4_3_monitor_commands.py --cov=main --cov-report=term-missing

# Run all unit tests
pytest tests/unit/ -v -m unit
```

---

## Red-Green-Refactor Workflow

### RED Phase (Complete)

**TEA Agent Responsibilities:**

- All tests written and failing
- Fixtures and factories created with auto-cleanup
- Mock requirements documented
- Implementation checklist created

**Verification:**

- All tests run and fail as expected
- Failure messages are clear and actionable
- Tests fail due to missing implementation, not test bugs

---

### GREEN Phase (DEV Team - Next Steps)

**DEV Agent Responsibilities:**

1. **Pick one failing test** from implementation checklist (start with P0 priority)
2. **Read the test** to understand expected behavior
3. **Implement minimal code** to make that specific test pass
4. **Run the test** to verify it now passes (green)
5. **Check off the task** in implementation checklist
6. **Move to next test** and repeat

**Key Principles:**

- One test at a time (don't try to fix all at once)
- Minimal implementation (don't over-engineer)
- Run tests frequently (immediate feedback)
- Use implementation checklist as roadmap

**Progress Tracking:**

- Check off tasks as you complete them
- Share progress in daily standup

---

### REFACTOR Phase (DEV Team - After All Tests Pass)

**DEV Agent Responsibilities:**

1. **Verify all tests pass** (green phase complete)
2. **Review code for quality** (readability, maintainability, performance)
3. **Extract duplications** (DRY principle)
4. **Optimize performance** (if needed)
5. **Ensure tests still pass** after each refactor
6. **Update documentation** (if API contracts change)

**Key Principles:**

- Tests provide safety net (refactor with confidence)
- Make small refactors (easier to debug if tests fail)
- Run tests after each change
- Don't change test behavior (only implementation)

**Completion:**

- All tests pass
- Code quality meets team standards
- No duplications or code smells
- Ready for code review and story approval

---

## Next Steps

1. **Share this checklist and failing tests** with the dev workflow (manual handoff)
2. **Review this checklist** with team in standup or planning
3. **Run failing tests** to confirm RED phase: `pytest tests/unit/test_story_4_3_monitor_commands.py -v`
4. **Begin implementation** using implementation checklist as guide
5. **Work one test at a time** (red -> green for each)
6. **Share progress** in daily standup
7. **When all tests pass**, refactor code for quality
8. **When refactoring complete**, manually update story status to 'done' in sprint-status.yaml

---

## Knowledge Base References Applied

This ATDD workflow consulted the following knowledge fragments:

- **data-factories.md** - Factory patterns with overrides support
- **test-quality.md** - Test design principles (Given-When-Then, one assertion per test, determinism, isolation)
- **test-healing-patterns.md** - Common failure patterns and fixes
- **test-levels-framework.md** - Test level selection framework (Unit for backend)

---

## Notes

- Tests follow existing patterns from `test_story_4_1_monitor.py`
- Using pytest fixtures from `tests/conftest.py`
- Tests are unit-level (no browser/E2E needed for backend)
- All commands require admin permission (AC#4)
- AUTO_START_MONITOR enables flexible deployment (AC#5)

---

**Generated by BMad TEA Agent** - 2026-03-01
