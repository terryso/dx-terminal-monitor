---
stepsCompleted:
  - step-01-preflight-and-context
  - step-02-generation-mode
  - step-03-test-strategy
  - step-04-generate-tests
lastStep: 'step-04-generate-tests'
lastSaved: '2026-03-01'
inputDocuments:
  - _bmad-output/implementation-artifacts/tech-spec-main-py-command-refactoring.md
  - _bmad/tea/testarch/knowledge/data-factories.md
  - _bmad/tea/testarch/knowledge/test-quality.md
  - _bmad/tea/testarch/knowledge/test-healing-patterns.md
  - _bmad/tea/testarch/knowledge/test-levels-framework.md
  - _bmad/tea/testarch/knowledge/test-priorities-matrix.md
---

# ATDD Checklist - Tech Spec: main.py 命令模块重构

---

**日期:** 2026-03-01
**作者:** Nick
**主要测试级别:** Unit + Integration

---

## Story Summary

重构 main.py 以消除循环导入问题，将命令处理器按功能域拆分到独立模块。创建 `commands/` 和 `utils/` 目录，简化 main.py 为入口文件。

**As a** 全栈工程师
**I want** 模块化的命令处理器结构
**So that** 代码可维护、团队协作

---

## Acceptance Criteria

1. AC 1: 格式化函数正常工作 (format_eth, format_usd, format_percent, format_time)
2. AC 22: authorized() 正确检查权限
3. AC 3: 查询命令返回正确响应
4. AC 4: 管理命令非管理员拒绝
5. AC 5: 监控命令状态正确
6. AC 6: 提款对话流程正常
7. AC 7: create_app() 注册所有命令
8. AC 8: 查询命令 API 错误处理
9. AC 9: 管理命令合约失败处理
10. AC 10: 监控未初始化消息
11. AC 11: 所有测试通过
12. AC 12: main.py < 120 行
13. AC 13: commands/ 文件 < 250 行
14. AC 14: 无循环导入错误

---

## Failing Tests Created (RED Phase)

### Unit Tests (15 tests)

**File:** `tests/unit/test_utils_formatters.py` (150+ lines)

- format_eth whole/decimal/small/zero/large value
- format_usd positive/negative/float/zero
- format_percent positive/negative/zero/float
- format_time valid timestamp/datetime/None

**Status:** RED - 稡块未创建，测试被 `@pytest.mark.skip` 蚀时

**File:** `tests/unit/test_utils_permissions.py` (50+ lines)
- authorized user in/out not in list
- authorized empty list
- authorized None list
- authorized single user

**Status:** RED - 模块未创建， 测试被 `@pytest.mark.skip` 蚀时

**File:** `tests/unit/test_import_cycles.py` (100+ lines)
- import main no error
- import commands.query no error
- import commands.admin no error
- import commands.monitor no error
- import commands.withdraw no error
- import utils no error
- register_handlers available
- set_monitor_instance available
**Status:** RED - 模块未创建, 测试被 `@pytest.mark.skip` 蚝时

**File:** `tests/unit/test_code_quality.py` (80 lines)
- main.py line count < 120
- commands/query.py < 250 lines
- commands/admin.py < 250 lines
- commands/monitor.py < 250 lines
- commands/withdraw.py < 250 lines
**Status:** RED - 模块未创建, 测试被 `@pytest.mark.skip` 蚂时

### Integration Tests (18 tests)
**File:** `tests/integration/test_query_commands.py` (200+ lines)
- cmd_balance success/error/unauthorized
- cmd_positions success
- cmd_pnl success
- cmd_activity success
- cmd_swaps success
- cmd_strategies success
**Status:** RED - 模块未创建, 测试被 `@pytest.mark.skip` 蚂时

**File:** `tests/integration/test_admin_commands.py` (150+ lines)
- cmd_pause non-admin rejected
- cmd_resume non-admin rejected
- cmd_update_settings non-admin rejected
- cmd_update_settings contract failure
**Status:** RED - 模块未创建, 测试被 `@pytest.mark.skip` 蚀时

**File:** `tests/integration/test_monitor_commands.py` (100+ lines)
- cmd_monitor_status shows running state
- cmd_monitor_status shows stopped state
- cmd_monitor_status shows not initialized
**Status:** RED - 模块未创建, 测试被 `@pytest.mark.skip` 蚀时
**File:** `tests/integration/test_withdraw_conversation.py` (150+ lines)
- cmd_withdraw starts conversation
- cmd_withdraw non-admin rejected
- cmd_withdraw no args shows usage
- handle_withdraw_confirm executes
- handle_withdraw_confirm cancels
- handle_withdraw_cancel clears pending
- create_withdraw_handler returns handler
- create_withdraw_handler has cancel fallback
**Status:** RED - 模块未创建, 测试被 `@pytest.mark.skip` 蚀时
---

## Implementation Checklist
### Test: test_utils_formatters.py
**Tasks to make this test pass:**
- [ ] Create `utils/__init__.py`
- [ ] Create `utils/formatters.py`
- [ ] Implement `format_eth(wei: str) -> str`
- [ ] Implement `format_usd(value) -> str`
- [ ] Implement `format_percent(value) -> str`
- [ ] Implement `format_time(timestamp) -> str`
- [ ] Run test: `pytest tests/unit/test_utils_formatters.py -v`
- [ ] Remove `@pytest.mark.skip` decorators
- [ ] Test passes (green phase)

**Estimated Effort:** 2 hours
---
### Test: test_utils_permissions.py
**Tasks to make this test pass:**
- [ ] Create `utils/permissions.py`
- [ ] Import `authorized` from main.py logic
- [ ] Implement `authorized(update: Update) -> bool`
- [ ] Run test: `pytest tests/unit/test_utils_permissions.py -v`
- [ ] Remove `@pytest.mark.skip` decorators
- [ ] Test passes (green phase)
**Estimated Effort:** 1 hour
---
### Test: test_query_commands.py
**Tasks to make this test pass:**
- [ ] Create `commands/__init__.py` with `register_handlers()`
- [ ] Create `commands/query.py`
- [ ] Migrate cmd_balance, cmd_positions, cmd_pnl, etc. from main.py
- [ ] Update imports to use `utils.permissions` and `utils.formatters`
- [ ] Update patch paths from `main.xxx` to `commands.query.xxx`
- [ ] Run test: `pytest tests/integration/test_query_commands.py -v`
- [ ] Remove `@pytest.mark.skip` decorators
- [ ] Test passes (green phase)
**Estimated Effort:** 3 hours
---
### Test: test_admin_commands.py
**Tasks to make this test pass:**
- [ ] Create `commands/admin.py`
- [ ] Migrate cmd_pause, cmd_resume, cmd_update_settings etc. from main.py
- [ ] Update imports to use `utils.formatters`
- [ ] Update patch paths from `main.xxx` to `commands.admin.xxx`
- [ ] Run test: `pytest tests/integration/test_admin_commands.py -v`
- [ ] Remove `@pytest.mark.skip` decorators
- [ ] Test passes (green phase)
**Estimated Effort:** 2 hours
---
### Test: test_monitor_commands.py
**Tasks to make this test pass:**
- [ ] Create `commands/monitor.py`
- [ ] Add `set_monitor_instance(instance)` setter function
- [ ] Migrate cmd_monitor_status, cmd_monitor_start, cmd_monitor_stop
- [ ] Update patch paths from `main.xxx` to `commands.monitor.xxx`
- [ ] Run test: `pytest tests/integration/test_monitor_commands.py -v`
- [ ] Remove `@pytest.mark.skip` decorators
- [ ] Test passes (green phase)
**Estimated Effort:** 2 hours
---
### Test: test_withdraw_conversation.py
**Tasks to make this test pass:**
- [ ] Create `commands/withdraw.py`
- [ ] Migrate withdraw conversation handler and related code
- [ ] Update patch paths from `main.xxx` to `commands.withdraw.xxx`
- [ ] Run test: `pytest tests/integration/test_withdraw_conversation.py -v`
- [ ] Remove `@pytest.mark.skip` decorators
- [ ] Test passes (green phase)
**Estimated Effort:** 2 hours
---
### Test: test_import_cycles.py
**Tasks to make this test pass:**
- [ ] Ensure all imports work without circular dependency
- [ ] Use setter injection pattern for monitor instance
- [ ] Run test: `pytest tests/unit/test_import_cycles.py -v`
- [ ] Remove `@pytest.mark.skip` decorators
- [ ] Test passes (green phase)
**Estimated Effort:** 1 hour
---
### Test: test_code_quality.py
**Tasks to make this test pass:**
- [ ] Refactor main.py to < 120 lines
- [ ] Ensure all commands/ files < 250 lines
- [ ] Run test: `pytest tests/unit/test_code_quality.py -v`
- [ ] Remove `@pytest.mark.skip` decorators
- [ ] Test passes (green phase)
**Estimated Effort:** 1 hour
---

## Running Tests
```bash
# Run all failing tests for this story (RED phase verification)
pytest tests/unit/test_utils_formatters.py -v
pytest tests/unit/test_utils_permissions.py -v
pytest tests/unit/test_import_cycles.py -v
pytest tests/unit/test_code_quality.py -v
pytest tests/integration/test_query_commands.py -v
pytest tests/integration/test_admin_commands.py -v
pytest tests/integration/test_monitor_commands.py -v
pytest tests/integration/test_withdraw_conversation.py -v

# Run all tests with coverage
pytest tests/ -v --cov=.
```

---

## Red-Green-Refactor Workflow
### RED Phase (Complete)
**TEA Agent Responsibilities:**
- All tests written with @pytest.mark.skip
- Tests document expected behavior
- Tests will fail until implementation complete
- Fixtures and factories follow existing patterns

**Verification:**
- All test files created
- All tests use correct patch paths (commands.* instead of main.*)
- All tests verify specific acceptance criteria
---

### GREEN Phase (DEV Team - Next Steps)
**DEV Agent Responsibilities:**
1. **Pick one failing test file** (start with utils tests)
2. **Read the tests** to understand expected behavior
3. **Implement minimal code** to make tests pass
4. **Run tests** to verify green phase
5. **Check off tasks** in implementation checklist
6. **Move to next test file** and repeat

**Suggested Implementation Order:**
1. Phase 1: Create utils/ (formatters.py, permissions.py)
2. Phase 2: Create commands/ (query.py, admin.py, monitor.py, withdraw.py)
3. Phase 3: Refactor main.py to entry point
4. Phase 4: Update test imports and remove skip decorators
5. Phase 5: Run full test suite

**Key Principles:**
- One module at a time (don't try to implement all at once)
- Minimal implementation (don't over-engineer)
- Run tests frequently (immediate feedback)
- Use implementation checklist as roadmap

---

### REFACTOR Phase (DEV Team - After All Tests Pass)
**DEV Agent Responsibilities:**
1. **Verify all tests pass** (green phase complete)
2. **Review code for quality** (readability, maintainability)
3. **Ensure no circular imports**
4. **Verify file size constraints** (main.py < 120, lines)
5. **Update documentation** (if API contracts change)

**Completion:**
- All tests pass
- main.py simplified to entry point
- All command handlers properly modularized
- Ready for code review
---

## Knowledge Base References Applied
This ATDD workflow consulted the following knowledge fragments:
- **data-factories.md** - Factory patterns with overrides support
- **test-quality.md** - Test design principles (Given-When-Then, one assertion per test)
- **test-levels-framework.md** - Test level selection framework (Unit vs Integration)
- **test-priorities-matrix.md** - Priority assignment (P0-P3)
- **test-healing-patterns.md** - Common failure patterns and fixes

See `tea-index.csv` for complete knowledge fragment mapping.
---

## Notes
- **循环导入解决方案**: 使用 setter 注入模式 (`set_monitor_instance`) 避免循环依赖
- **测试策略**: 优先使用 Unit 测试纯函数， Integration 测试命令处理器
- **现有测试**: 需要更新导入路径， `main.xxx` → `commands.xxx` 或 `utils.xxx`
- **配置**: config.py 中的 is_admin() 保留在原位置，因为依赖 config.ADMIN_USERS
