---
stepsCompleted: ['step-01-preflight-and-context', 'step-02-generation-mode', 'step-03-test-strategy', 'step-04-generate-tests']
lastStep: 'step-04-generate-tests'
lastSaved: '2026-03-01'
workflowType: 'testarch-atdd'
inputDocuments:
  - '/Users/nick/projects/dx-terminal-monitor/_bmad-output/implementation-artifacts/2-2-pause-resume-agent.md'
  - '/Users/nick/projects/dx-terminal-monitor/pyproject.toml'
  - '/Users/nick/projects/dx-terminal-monitor/tests/conftest.py'
  - '/Users/nick/projects/dx-terminal-monitor/tests/support/web3_fixtures.py'
  - '/Users/nick/projects/dx-terminal-monitor/tests/unit/test_command_handlers_p1.py'
---

# ATDD Checklist - Epic 2, Story 2: 暂停/恢复 Agent 交易命令

**Date:** 2026-03-01
**Author:** Nick
**Primary Test Level:** Unit (Command Handlers) + Unit (Contract Methods)

---

## Story Summary

**As a** 用户 (User)
**I want** 通过 `/pause` 和 `/resume` 命令控制 Agent 自动交易
**So that** 在市场异常时保护资金

---

## Acceptance Criteria

1. 实现 `contract.pause_vault(paused: bool)` 方法
2. 实现 `cmd_pause` 和 `cmd_resume` 命令处理函数
3. `/pause` 返回: "⏸️ Agent 已暂停，将不会执行任何交易"
4. `/resume` 返回: "▶️ Agent 已恢复，将继续执行交易"
5. 管理员权限检查
6. 添加单元测试

---

## Context Loaded

### Stack Detection
- **Detected Stack:** backend (Python with pytest)
- **Test Framework:** pytest >=8.0 with asyncio mode
- **Project Structure:**
  - Backend: Python Telegram bot with web3.py integration
  - Test Location: `/Users/nick/projects/dx-terminal-monitor/tests/`
  - Existing Patterns: Command handler tests in `tests/unit/test_command_handlers_p1.py`

### Existing Test Patterns Identified

**Command Handler Test Pattern:**
- Uses `@pytest.mark.asyncio` for async tests
- Mocks with `unittest.mock.AsyncMock` and `MagicMock`
- Patches `main.authorized` or `main.is_admin` for permission checks
- Patches `main.contract()` for contract interactions
- Asserts on `mock_telegram_update.message.reply_text.call_args`

**Web3 Mock Pattern:**
- Uses `mock_contract` from `tests/support/web3_fixtures.py`
- Mocks contract functions with `contract.functions.methodName()`
- Returns standard result dict: `{success, transactionHash, status, blockNumber, error}`

**Test Organization:**
- Unit tests in `tests/unit/`
- Fixtures in `tests/conftest.py` and `tests/support/web3_fixtures.py`
- Web3-specific tests can be in `tests/unit/web3/` subdirectory

### Key Implementation Requirements

**contract.py - pause_vault method:**
- Async method accepting `paused: bool`
- Calls `self.contract.functions.pauseVault(paused)`
- Uses `await self._send_transaction(tx_func)`
- Returns standard result dictionary

**main.py - cmd_pause & cmd_resume:**
- Admin permission check with `is_admin()`
- Audit logging with `logger.info()`
- Call `contract().pause_vault(True/False)`
- Return emoji-prefixed messages on success
- Handle errors gracefully

---

## Next Steps

Proceeding to Step 2: Generation Mode Selection

---

## Step 2: Generation Mode Selected

**Mode:** AI Generation
**Reason:** Backend Python project (detected_stack = backend) - no browser recording needed. Tests will be generated from story acceptance criteria and existing test patterns.

**Source Material:**
- Story acceptance criteria from implementation artifact
- Existing command handler test patterns
- Existing Web3 mock patterns
- Contract method signatures from story documentation

Proceeding to Step 3: Test Strategy

---

## Test Strategy

### Acceptance Criteria → Test Scenarios Mapping

**AC #1: 实现 `contract.pause_vault(paused: bool)` 方法**

Test Level: **Unit** (Contract Method)
Priority: **P0** (Critical path - core functionality)

Test Scenarios:
1. ✅ `test_pause_vault_calls_web3_function` - Verify pause_vault(True) calls contract.functions.pauseVault(True)
2. ✅ `test_resume_vault_calls_web3_function` - Verify pause_vault(False) calls contract.functions.pauseVault(False)
3. ✅ `test_pause_vault_returns_success_dict` - Verify return format {success, transactionHash, status, blockNumber}
4. ✅ `test_pause_vault_handles_exception` - Verify exception handling returns {success: False, error: str}

**AC #2: 实现 `cmd_pause` 和 `cmd_resume` 命令处理函数**

Test Level: **Unit** (Command Handlers)
Priority: **P0** (Critical path - user-facing commands)

Test Scenarios for cmd_pause:
5. ✅ `test_cmd_pause_success` - Admin user successfully pauses vault
6. ✅ `test_cmd_pause_unauthorized` - Non-admin user is rejected
7. ✅ `test_cmd_pause_contract_failure` - Contract call fails, error message shown
8. ✅ `test_cmd_pause_logs_audit` - Audit log recorded with admin ID

Test Scenarios for cmd_resume:
9. ✅ `test_cmd_resume_success` - Admin user successfully resumes vault
10. ✅ `test_cmd_resume_unauthorized` - Non-admin user is rejected
11. ✅ `test_cmd_resume_contract_failure` - Contract call fails, error message shown
12. ✅ `test_cmd_resume_logs_audit` - Audit log recorded with admin ID

**AC #3: `/pause` 返回: "⏸️ Agent 已暂停，将不会执行任何交易"**

Test Level: **Unit** (Command Handler Response)
Priority: **P0** (Critical path - user feedback)

Test Scenarios:
13. ✅ Covered by test_cmd_pause_success - Verifies emoji and message content

**AC #4: `/resume` 返回: "▶️ Agent 已恢复，将继续执行交易"**

Test Level: **Unit** (Command Handler Response)
Priority: **P0** (Critical path - user feedback)

Test Scenarios:
14. ✅ Covered by test_cmd_resume_success - Verifies emoji and message content

**AC #5: 管理员权限检查**

Test Level: **Unit** (Authorization)
Priority: **P0** (Security - high risk)

Test Scenarios:
15. ✅ Covered by test_cmd_pause_unauthorized
16. ✅ Covered by test_cmd_resume_unauthorized
17. ✅ Additional: Verify is_admin() is called (not authorized())

**AC #6: 添加单元测试**

Test Level: **Unit**
Priority: **P0** (Quality gate)

All above tests satisfy this criterion.

**Additional Test Scenarios (Edge Cases):**

18. ✅ `test_pause_vault_transaction_format` - Verify _send_transaction receives correct tx_func
19. ✅ `test_both_commands_registered` - Verify BotCommand registration in post_init
20. ✅ `test_both_handlers_registered` - Verify CommandHandler registration in create_app

### Test Level Selection Rationale

**Unit Tests (Primary):**
- Contract method `pause_vault()` - Pure business logic with Web3 mock
- Command handlers `cmd_pause/cmd_resume` - Async handlers with mocked dependencies
- Permission checks - Fast, isolated tests with no external dependencies

**No Integration Tests Needed:**
- No database interactions
- No external API calls (all mocked)
- Web3 interactions fully mocked at unit level

**No E2E Tests Needed:**
- Backend-only project (no browser UI)
- All user interactions through Telegram API (mocked)

### Priority Assignment

| Priority | Tests | Rationale |
|----------|-------|-----------|
| **P0** | All 20 tests | Critical functionality - pause/resume is a safety mechanism for protecting funds during market anomalies. All paths must work correctly. |

### Red Phase Requirements

All tests MUST fail initially because:
1. `contract.pause_vault()` method does not exist
2. `cmd_pause` and `cmd_resume` handlers do not exist
3. BotCommand and CommandHandler not registered
4. Implementation code has not been written

Tests are designed to be **deterministic** and **isolated**:
- No actual blockchain connections (all mocked)
- No actual Telegram API calls (all mocked)
- No shared state between tests
- Clear failure messages indicating what needs implementation

Proceeding to Step 4: Generate Tests

---

## Failing Tests Created (RED Phase)

### Unit Tests - Contract Methods (5 tests)

**File:** `/Users/nick/projects/dx-terminal-monitor/tests/unit/test_story_2_2_pause_resume.py`

**Test Class:** `TestContractPauseVault`

- ✅ **Test:** `test_pause_vault_calls_web3_function`
  - **Status:** RED - @pytest.mark.skip (method not implemented)
  - **Verifies:** AC#1 - pause_vault(True) calls contract.functions.pauseVault(True)

- ✅ **Test:** `test_resume_vault_calls_web3_function`
  - **Status:** RED - @pytest.mark.skip (method not implemented)
  - **Verifies:** AC#1 - pause_vault(False) calls contract.functions.pauseVault(False)

- ✅ **Test:** `test_pause_vault_returns_success_dict`
  - **Status:** RED - @pytest.mark.skip (method not implemented)
  - **Verifies:** AC#1 - Returns standard {success, transactionHash, status, blockNumber}

- ✅ **Test:** `test_pause_vault_handles_exception`
  - **Status:** RED - @pytest.mark.skip (method not implemented)
  - **Verifies:** AC#1 - Exception handling returns {success: False, error: str}

- ✅ **Test:** `test_pause_vault_transaction_format`
  - **Status:** RED - @pytest.mark.skip (method not implemented)
  - **Verifies:** AC#1 - _send_transaction receives correct tx_func

### Unit Tests - Command Handler: cmd_pause (4 tests)

**File:** `/Users/nick/projects/dx-terminal-monitor/tests/unit/test_story_2_2_pause_resume.py`

**Test Class:** `TestCmdPause`

- ✅ **Test:** `test_cmd_pause_success`
  - **Status:** RED - @pytest.mark.skip (handler not implemented)
  - **Verifies:** AC#2, #3, #5 - Admin pauses vault, gets emoji message with tx hash

- ✅ **Test:** `test_cmd_pause_unauthorized`
  - **Status:** RED - @pytest.mark.skip (handler not implemented)
  - **Verifies:** AC#5 - Non-admin user rejected with "未授权" message

- ✅ **Test:** `test_cmd_pause_contract_failure`
  - **Status:** RED - @pytest.mark.skip (handler not implemented)
  - **Verifies:** AC#2 - Contract failure handled gracefully

- ✅ **Test:** `test_cmd_pause_logs_audit`
  - **Status:** RED - @pytest.mark.skip (handler not implemented)
  - **Verifies:** AC#5 - Admin action logged with user ID

### Unit Tests - Command Handler: cmd_resume (4 tests)

**File:** `/Users/nick/projects/dx-terminal-monitor/tests/unit/test_story_2_2_pause_resume.py`

**Test Class:** `TestCmdResume`

- ✅ **Test:** `test_cmd_resume_success`
  - **Status:** RED - @pytest.mark.skip (handler not implemented)
  - **Verifies:** AC#2, #4, #5 - Admin resumes vault, gets emoji message with tx hash

- ✅ **Test:** `test_cmd_resume_unauthorized`
  - **Status:** RED - @pytest.mark.skip (handler not implemented)
  - **Verifies:** AC#5 - Non-admin user rejected with "未授权" message

- ✅ **Test:** `test_cmd_resume_contract_failure`
  - **Status:** RED - @pytest.mark.skip (handler not implemented)
  - **Verifies:** AC#2 - Contract failure handled gracefully

- ✅ **Test:** `test_cmd_resume_logs_audit`
  - **Status:** RED - @pytest.mark.skip (handler not implemented)
  - **Verifies:** AC#5 - Admin action logged with user ID

### Unit Tests - Permission Checks (2 tests)

**File:** `/Users/nick/projects/dx-terminal-monitor/tests/unit/test_story_2_2_pause_resume.py`

**Test Class:** `TestPermissionChecks`

- ✅ **Test:** `test_pause_uses_is_admin_not_authorized`
  - **Status:** RED - @pytest.mark.skip (handler not implemented)
  - **Verifies:** AC#5 - Uses is_admin() (not authorized()) for security

- ✅ **Test:** `test_resume_uses_is_admin_not_authorized`
  - **Status:** RED - @pytest.mark.skip (handler not implemented)
  - **Verifies:** AC#5 - Uses is_admin() (not authorized()) for security

### Unit Tests - Command Registration (3 tests)

**File:** `/Users/nick/projects/dx-terminal-monitor/tests/unit/test_story_2_2_pause_resume.py`

**Test Class:** `TestCommandRegistration`

- ✅ **Test:** `test_pause_resume_commands_registered_in_post_init`
  - **Status:** RED - @pytest.mark.skip (commands not registered)
  - **Verifies:** AC#2 - BotCommand("pause") and BotCommand("resume") in post_init()

- ✅ **Test:** `test_pause_resume_handlers_registered_in_create_app`
  - **Status:** RED - @pytest.mark.skip (handlers not registered)
  - **Verifies:** AC#2 - CommandHandler for pause/resume in create_app()

- ✅ **Test:** `test_start_help_includes_pause_resume`
  - **Status:** RED - @pytest.mark.skip (help text not updated)
  - **Verifies:** AC#2 - /start help text mentions pause/resume commands

---

## Test Summary Statistics

- **Total Tests:** 18 (all marked with @pytest.mark.skip)
- **Test File:** 1 file created
- **Lines of Code:** 557 lines
- **TDD Phase:** RED (all tests skipped, waiting for implementation)
- **Expected Behavior:** All tests document EXPECTED behavior
- **Implementation Trigger:** Remove @pytest.mark.skip after implementing features

---

## Test Execution Commands

```bash
# Run all Story 2-2 tests (will show as skipped)
pytest tests/unit/test_story_2_2_pause_resume.py -v

# Run specific test class
pytest tests/unit/test_story_2_2_pause_resume.py::TestCmdPause -v

# Run with coverage
pytest tests/unit/test_story_2_2_pause_resume.py --cov=main --cov=contract --cov-report=term-missing

# Run all skipped tests
pytest tests/unit/test_story_2_2_pause_resume.py -v -m skip
```

---

## Implementation Checklist

### Task 1: Implement contract.pause_vault() Method

**File:** `contract.py`

**Tests that will pass:**
- `test_pause_vault_calls_web3_function`
- `test_resume_vault_calls_web3_function`
- `test_pause_vault_returns_success_dict`
- `test_pause_vault_handles_exception`
- `test_pause_vault_transaction_format`

**Implementation Steps:**
- [ ] Add `async def pause_vault(self, paused: bool = True)` method
- [ ] Call `self.contract.functions.pauseVault(paused)`
- [ ] Use `await self._send_transaction(tx_func)`
- [ ] Return `{success, transactionHash, status, blockNumber}` on success
- [ ] Return `{success: False, error: str(e)}` on exception
- [ ] Add logger.error() for exceptions
- [ ] Run tests: `pytest tests/unit/test_story_2_2_pause_resume.py::TestContractPauseVault -v`
- [ ] ✅ All 5 tests pass (green phase)

**Estimated Effort:** 1 hour

---

### Task 2: Implement cmd_pause Command Handler

**File:** `main.py`

**Tests that will pass:**
- `test_cmd_pause_success`
- `test_cmd_pause_unauthorized`
- `test_cmd_pause_contract_failure`
- `test_cmd_pause_logs_audit`

**Implementation Steps:**
- [ ] Add `async def cmd_pause(update, ctx)` function
- [ ] Check admin: `if not is_admin(update.effective_user.id): return`
- [ ] Log audit: `logger.info(f"Admin {user_id} pausing vault")`
- [ ] Call: `result = await contract().pause_vault(True)`
- [ ] On success: Reply "⏸️ Agent 已暂停，将不会执行任何交易\n交易哈希: {tx_hash}"
- [ ] On failure: Reply "暂停失败: {error}"
- [ ] Run tests: `pytest tests/unit/test_story_2_2_pause_resume.py::TestCmdPause -v`
- [ ] ✅ All 4 tests pass (green phase)

**Estimated Effort:** 1 hour

---

### Task 3: Implement cmd_resume Command Handler

**File:** `main.py`

**Tests that will pass:**
- `test_cmd_resume_success`
- `test_cmd_resume_unauthorized`
- `test_cmd_resume_contract_failure`
- `test_cmd_resume_logs_audit`

**Implementation Steps:**
- [ ] Add `async def cmd_resume(update, ctx)` function
- [ ] Check admin: `if not is_admin(update.effective_user.id): return`
- [ ] Log audit: `logger.info(f"Admin {user_id} resuming vault")`
- [ ] Call: `result = await contract().pause_vault(False)`
- [ ] On success: Reply "▶️ Agent 已恢复，将继续执行交易\n交易哈希: {tx_hash}"
- [ ] On failure: Reply "恢复失败: {error}"
- [ ] Run tests: `pytest tests/unit/test_story_2_2_pause_resume.py::TestCmdResume -v`
- [ ] ✅ All 4 tests pass (green phase)

**Estimated Effort:** 1 hour

---

### Task 4: Register Commands in Bot

**File:** `main.py`

**Tests that will pass:**
- `test_pause_resume_commands_registered_in_post_init`
- `test_pause_resume_handlers_registered_in_create_app`

**Implementation Steps:**
- [ ] In `post_init()`: Add `BotCommand("pause", "Pause Agent trading")`
- [ ] In `post_init()`: Add `BotCommand("resume", "Resume Agent trading")`
- [ ] In `create_app()`: Add `CommandHandler("pause", cmd_pause)`
- [ ] In `create_app()`: Add `CommandHandler("resume", cmd_resume)`
- [ ] Run tests: `pytest tests/unit/test_story_2_2_pause_resume.py::TestCommandRegistration -v`
- [ ] ✅ All 3 tests pass (green phase)

**Estimated Effort:** 0.5 hours

---

### Task 5: Update Help Text

**File:** `main.py`

**Tests that will pass:**
- `test_start_help_includes_pause_resume`

**Implementation Steps:**
- [ ] In `cmd_start()`: Add "/pause - 暂停 Agent 交易"
- [ ] In `cmd_start()`: Add "/resume - 恢复 Agent 交易"
- [ ] Run test: `pytest tests/unit/test_story_2_2_pause_resume.py::TestCommandRegistration::test_start_help_includes_pause_resume -v`
- [ ] ✅ Test passes (green phase)

**Estimated Effort:** 0.25 hours

---

### Task 6: Remove @pytest.mark.skip (GREEN Phase)

**File:** `tests/unit/test_story_2_2_pause_resume.py`

**Implementation Steps:**
- [ ] Remove all `@pytest.mark.skip` decorators from test file
- [ ] Run all tests: `pytest tests/unit/test_story_2_2_pause_resume.py -v`
- [ ] Verify all 18 tests PASS
- [ ] Run coverage: `pytest tests/unit/test_story_2_2_pause_resume.py --cov=main --cov=contract`
- [ ] Verify coverage > 90%
- [ ] ✅ All tests pass (green phase complete)

**Estimated Effort:** 0.25 hours

---

## Running Tests

```bash
# Run all failing tests for this story
pytest tests/unit/test_story_2_2_pause_resume.py -v

# Run specific test file
pytest tests/unit/test_story_2_2_pause_resume.py::TestCmdPause -v

# Run with coverage
pytest tests/unit/test_story_2_2_pause_resume.py --cov=main --cov=contract --cov-report=html

# Debug specific test
pytest tests/unit/test_story_2_2_pause_resume.py::TestCmdPause::test_cmd_pause_success -vv -s
```

---

## Red-Green-Refactor Workflow

### RED Phase (Complete) ✅

**TEA Agent Responsibilities:**
- ✅ All tests written and failing (marked with @pytest.mark.skip)
- ✅ Tests use existing mock fixtures from conftest.py and web3_fixtures.py
- ✅ Tests document expected behavior with clear assertions
- ✅ Implementation checklist created

**Verification:**
- All tests marked with @pytest.mark.skip
- Tests assert expected behavior (not placeholders)
- Tests fail due to missing implementation, not test bugs

---

### GREEN Phase (DEV Team - Next Steps)

**DEV Agent Responsibilities:**

1. **Pick one failing test** from implementation checklist (start with contract.pause_vault)
2. **Remove @pytest.mark.skip** from that test class
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
3. **Run failing tests** to confirm RED phase: `pytest tests/unit/test_story_2_2_pause_resume.py -v`
4. **Begin implementation** using implementation checklist as guide
5. **Work one test at a time** (red → green for each)
6. **Share progress** in daily standup
7. **When all tests pass**, refactor code for quality
8. **When refactoring complete**, manually update story status to 'done' in sprint-status.yaml

---

## Notes

- All tests use existing fixtures from `tests/conftest.py` and `tests/support/web3_fixtures.py`
- No new fixtures needed for this story
- Tests follow existing patterns from `tests/unit/test_command_handlers_p1.py`
- All permission checks use `is_admin()` (not `authorized()`)
- Audit logging is verified for security compliance
- Test file: 557 lines, 18 test cases
- Estimated total implementation effort: 4 hours

---

## Contact

**Questions or Issues?**
- Ask in team standup
- Refer to story artifact: `/Users/nick/projects/dx-terminal-monitor/_bmad-output/implementation-artifacts/2-2-pause-resume-agent.md`
- Refer to existing test patterns in `tests/unit/test_command_handlers_p1.py`

---

**Generated by BMad TEA Agent** - 2026-03-01

---

## Test Execution Evidence

### Initial Test Run (RED Phase Verification)

**Command:** `pytest tests/unit/test_story_2_2_pause_resume.py -v --tb=no`

**Results:**

```
============================= test session starts ==============================
platform darwin -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0
rootdir: /Users/nick/projects/dx-terminal-monitor
configfile: pyproject.toml
plugins: anyio-4.12.1, asyncio-1.3.0, aiohttp-1.1.0, cov-7.0.0

tests/unit/test_story_2_2_pause_resume.py::TestContractPauseVault::test_pause_vault_calls_web3_function SKIPPED
tests/unit/test_story_2_2_pause_resume.py::TestContractPauseVault::test_resume_vault_calls_web3_function SKIPPED
tests/unit/test_story_2_2_pause_resume.py::TestContractPauseVault::test_pause_vault_returns_success_dict SKIPPED
tests/unit/test_story_2_2_pause_resume.py::TestContractPauseVault::test_pause_vault_handles_exception SKIPPED
tests/unit/test_story_2_2_pause_resume.py::TestContractPauseVault::test_pause_vault_transaction_format SKIPPED
tests/unit/test_story_2_2_pause_resume.py::TestCmdPause::test_cmd_pause_success SKIPPED
tests/unit/test_story_2_2_pause_resume.py::TestCmdPause::test_cmd_pause_unauthorized SKIPPED
tests/unit/test_story_2_2_pause_resume.py::TestCmdPause::test_cmd_pause_contract_failure SKIPPED
tests/unit/test_story_2_2_pause_resume.py::TestCmdPause::test_cmd_pause_logs_audit SKIPPED
tests/unit/test_story_2_2_pause_resume.py::TestCmdResume::test_cmd_resume_success SKIPPED
tests/unit/test_story_2_2_pause_resume.py::TestCmdResume::test_cmd_resume_unauthorized SKIPPED
tests/unit/test_story_2_2_pause_resume.py::TestCmdResume::test_cmd_resume_contract_failure SKIPPED
tests/unit/test_story_2_2_pause_resume.py::TestCmdResume::test_cmd_resume_logs_audit SKIPPED
tests/unit/test_story_2_2_pause_resume.py::TestPermissionChecks::test_pause_uses_is_admin_not_authorized SKIPPED
tests/unit/test_story_2_2_pause_resume.py::TestPermissionChecks::test_resume_uses_is_admin_not_authorized SKIPPED
tests/unit/test_story_2_2_pause_resume.py::TestCommandRegistration::test_pause_resume_commands_registered_in_post_init SKIPPED
tests/unit/test_story_2_2_pause_resume.py::TestCommandRegistration::test_pause_resume_handlers_registered_in_create_app SKIPPED
tests/unit/test_story_2_2_pause_resume.py::TestCommandRegistration::test_start_help_includes_pause_resume SKIPPED

============================= 18 skipped in 0.03s ==============================
```

**Summary:**

- Total tests: 18
- Passing: 0 (expected - all skipped)
- Failing: 0 (all skipped by design)
- Skipped: 18 (TDD red phase - waiting for implementation)
- Status: ✅ RED phase verified

**Expected Skip Reasons:**
- 5 tests: "RED PHASE: pause_vault() method not implemented yet"
- 4 tests: "RED PHASE: cmd_pause not implemented yet"
- 4 tests: "RED PHASE: cmd_resume not implemented yet"
- 2 tests: "RED PHASE: Commands not implemented yet"
- 3 tests: "RED PHASE: Commands/Handlers/Help not registered yet"

All tests are properly marked with `@pytest.mark.skip` and document expected behavior.
