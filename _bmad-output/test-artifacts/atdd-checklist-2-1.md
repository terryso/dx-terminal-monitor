---
stepsCompleted:
  - step-01-preflight-and-context
  - step-02-generation-mode
  - step-03-test-strategy
  - step-04-generate-tests
lastStep: step-04-generate-tests
lastSaved: '2026-03-01'
workflowType: testarch-atdd
inputDocuments:
  - _bmad-output/implementation-artifacts/2-1-add-strategy.md
  - main.py
  - contract.py
  - config.py
  - tests/conftest.py
  - tests/unit/test_command_handlers_p1.py
---

# ATDD Checklist - Epic 2, Story 2-1: 添加新策略命令

**Date:** 2026-03-01
**Author:** Nick
**Primary Test Level:** Unit

---

## Story Summary

作为**用户**，我需要**通过 `/add_strategy <text>` 命令添加新策略**，以便**指导 Agent 进行特定交易**。

**As a** 用户
**I want** 通过 `/add_strategy <text>` 命令添加新策略
**So that** 指导 Agent 进行特定交易

---

## Acceptance Criteria

1. 实现 `contract.add_strategy(content, expiry, priority)` 方法
2. 实现 `cmd_add_strategy` 命令处理函数
3. 命令格式: `/add_strategy 当 ETH 跌破 3000 时买入`
4. 默认参数: expiry=0 (永不过期), priority=1 (中等)
5. 成功时返回: "策略已添加，ID: #4"
6. 策略数量达到上限(8)时返回错误提示
7. 管理员权限检查
8. 添加单元测试

---

## Failing Tests Created (RED Phase)

### Unit Tests (8 tests)

**File:** `tests/unit/test_command_handlers_p1.py` (appended)

- **Test:** `test_add_strategy_success`
  - **Status:** RED - Function `cmd_add_strategy` not implemented
  - **Verifies:** AC#2, AC#3, AC#5

- **Test:** `test_add_strategy_unauthorized_non_admin`
  - **Status:** RED - Function `cmd_add_strategy` not implemented
  - **Verifies:** AC#7

- **Test:** `test_add_strategy_no_args`
  - **Status:** RED - Function `cmd_add_strategy` not implemented
  - **Verifies:** AC#2, AC#3

- **Test:** `test_add_strategy_empty_args`
  - **Status:** RED - Function `cmd_add_strategy` not implemented
  - **Verifies:** AC#2, AC#3

- **Test:** `test_add_strategy_max_limit_reached`
  - **Status:** RED - Function `cmd_add_strategy` not implemented
  - **Verifies:** AC#6

- **Test:** `test_add_strategy_contract_failure`
  - **Status:** RED - Function `cmd_add_strategy` not implemented
  - **Verifies:** AC#2

- **Test:** `test_contract_add_strategy_success`
  - **Status:** RED - Method `add_strategy` not implemented in VaultContract
  - **Verifies:** AC#1, AC#4

- **Test:** `test_contract_add_strategy_with_custom_params`
  - **Status:** RED - Method `add_strategy` not implemented in VaultContract
  - **Verifies:** AC#1, AC#4

---

## Data Factories Created

### StrategyResult Factory

**File:** `tests/conftest.py` (extended)

**Exports:**

- `create_strategy_result(overrides?)` - Create strategy result with optional overrides

**Example Usage:**

```python
result = create_strategy_result({"strategyId": 5})
result = create_strategy_result({"success": False, "error": "Max strategies reached"})
```

---

## Mock Requirements

### VaultContract Mock

**Mock Method:** `add_strategy(content, expiry, priority)`

**Success Response:**

```python
{
    "success": True,
    "strategyId": 4,
    "transactionHash": "0xabc123...",
    "status": 1,
    "blockNumber": 12345678
}
```

**Failure Response:**

```python
{
    "success": False,
    "error": "Max strategies limit reached"
}
```

**Notes:** Mock should be applied via `patch("main.contract")` for command handler tests

---

## Implementation Checklist

### Test: test_add_strategy_success

**File:** `tests/unit/test_command_handlers_p1.py`

**Tasks to make this test pass:**

- [ ] 在 `main.py` 中添加 `async def cmd_add_strategy(update, ctx)` 函数
- [ ] 使用 `is_admin()` 检查管理员权限
- [ ] 解析命令参数 `ctx.args`，将所有参数拼接为 content
- [ ] 调用 `contract().add_strategy(content)` 使用默认参数
- [ ] 处理成功响应，返回 "策略已添加，ID: #X"
- [ ] Run test: `pytest tests/unit/test_command_handlers_p1.py::TestCmdAddStrategy::test_add_strategy_success -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 1 hour

---

### Test: test_add_strategy_unauthorized_non_admin

**File:** `tests/unit/test_command_handlers_p1.py`

**Tasks to make this test pass:**

- [ ] 在 `cmd_add_strategy` 中添加 `is_admin()` 检查
- [ ] 非管理员用户返回 "未授权: 仅管理员可添加策略"
- [ ] Run test: `pytest tests/unit/test_command_handlers_p1.py::TestCmdAddStrategy::test_add_strategy_unauthorized_non_admin -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 0.25 hour

---

### Test: test_add_strategy_no_args / test_add_strategy_empty_args

**File:** `tests/unit/test_command_handlers_p1.py`

**Tasks to make this test pass:**

- [ ] 在 `cmd_add_strategy` 中检查 `ctx.args` 是否为空
- [ ] 无参数时返回 "用法: /add_strategy <策略内容>"
- [ ] Run test: `pytest tests/unit/test_command_handlers_p1.py::TestCmdAddStrategy::test_add_strategy_no_args -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 0.25 hour

---

### Test: test_add_strategy_max_limit_reached

**File:** `tests/unit/test_command_handlers_p1.py`

**Tasks to make this test pass:**

- [ ] 在 `cmd_add_strategy` 中处理合约返回的错误
- [ ] 检测错误信息中包含 "max" 或 "limit" 或 "8"
- [ ] 返回用户友好的错误提示 "错误: 已达到策略数量上限 (最多 8 个)"
- [ ] Run test: `pytest tests/unit/test_command_handlers_p1.py::TestCmdAddStrategy::test_add_strategy_max_limit_reached -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 0.5 hour

---

### Test: test_add_strategy_contract_failure

**File:** `tests/unit/test_command_handlers_p1.py`

**Tasks to make this test pass:**

- [ ] 在 `cmd_add_strategy` 中处理合约调用失败
- [ ] 返回 "添加失败: {error}"
- [ ] Run test: `pytest tests/unit/test_command_handlers_p1.py::TestCmdAddStrategy::test_add_strategy_contract_failure -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 0.25 hour

---

### Test: test_contract_add_strategy_success

**File:** `tests/unit/web3/test_contract.py`

**Tasks to make this test pass:**

- [ ] 在 `contract.py` 中添加 `add_strategy(content, expiry=0, priority=1)` 方法
- [ ] 调用合约的 `addStrategy(string, uint64, uint8)` 函数
- [ ] 使用 `_send_transaction()` 处理交易
- [ ] 从日志解析 `strategyId`
- [ ] 返回标准结果字典
- [ ] Run test: `pytest tests/unit/web3/test_contract.py::TestVaultContract::test_contract_add_strategy_success -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 1.5 hours

---

### Test: test_contract_add_strategy_with_custom_params

**File:** `tests/unit/web3/test_contract.py`

**Tasks to make this test pass:**

- [ ] 验证 `add_strategy` 支持自定义 expiry 和 priority 参数
- [ ] 正确传递参数到合约函数
- [ ] Run test: `pytest tests/unit/web3/test_contract.py::TestVaultContract::test_contract_add_strategy_with_custom_params -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 0.5 hour

---

### Task: 注册命令到 Bot

**File:** `main.py`

**Tasks:**

- [ ] 在 `post_init()` 中添加 `BotCommand("add_strategy", "Add new strategy")`
- [ ] 在 `create_app()` 中添加 `CommandHandler("add_strategy", cmd_add_strategy)`
- [ ] 更新 `cmd_start()` 帮助文本，添加 `/add_strategy <text>` 说明

**Estimated Effort:** 0.25 hour

---

## Running Tests

```bash
# Run all failing tests for this story
pytest tests/unit/test_command_handlers_p1.py::TestCmdAddStrategy -v
pytest tests/unit/web3/test_contract.py::TestVaultContract::test_contract_add_strategy_success -v
pytest tests/unit/web3/test_contract.py::TestVaultContract::test_contract_add_strategy_with_custom_params -v

# Run specific test file
pytest tests/unit/test_command_handlers_p1.py -v -k "add_strategy"

# Run with coverage
pytest tests/unit/test_command_handlers_p1.py --cov=main --cov=contract --cov-report=term-missing
```

---

## Red-Green-Refactor Workflow

### RED Phase (Complete)

**TEA Agent Responsibilities:**

- [x] All tests written and failing
- [x] Mock requirements documented
- [x] Implementation checklist created

**Verification:**

- All tests run and fail as expected
- Failure messages are clear and actionable
- Tests fail due to missing implementation, not test bugs

---

### GREEN Phase (DEV Team - Next Steps)

**DEV Agent Responsibilities:**

1. **Pick one failing test** from implementation checklist (start with highest priority)
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

---

### REFACTOR Phase (DEV Team - After All Tests Pass)

**DEV Agent Responsibilities:**

1. **Verify all tests pass** (green phase complete)
2. **Review code for quality** (readability, maintainability, performance)
3. **Extract duplications** (DRY principle)
4. **Optimize performance** (if needed)
5. **Ensure tests still pass** after each refactor
6. **Update documentation** (if API contracts change)

---

## Next Steps

1. **Run failing tests** to confirm RED phase: `pytest tests/unit/test_command_handlers_p1.py::TestCmdAddStrategy -v`
2. **Begin implementation** using implementation checklist as guide
3. **Work one test at a time** (red -> green for each)
4. **When all tests pass**, refactor code for quality
5. **Register command** in Bot menu and handlers

---

## Notes

- 使用 `is_admin()` 而非 `authorized()` 进行权限检查 (高风险操作)
- 策略内容直接传递给合约，不做额外验证
- 默认参数: expiry=0 (永不过期), priority=1 (中等)
- 策略上限为 8 个，由合约限制

---

## Test Execution Evidence

### Initial Test Run (RED Phase Verification)

**Command:** `pytest tests/unit/test_command_handlers_p1.py::TestCmdAddStrategy -v`

**Results:**

```
tests/unit/test_command_handlers_p1.py::TestCmdAddStrategy::test_add_strategy_success FAILED
tests/unit/test_command_handlers_p1.py::TestCmdAddStrategy::test_add_strategy_unauthorized_non_admin FAILED
tests/unit/test_command_handlers_p1.py::TestCmdAddStrategy::test_add_strategy_no_args FAILED
tests/unit/test_command_handlers_p1.py::TestCmdAddStrategy::test_add_strategy_empty_args FAILED
tests/unit/test_command_handlers_p1.py::TestCmdAddStrategy::test_add_strategy_max_limit_reached FAILED
tests/unit/test_command_handlers_p1.py::TestCmdAddStrategy::test_add_strategy_contract_failure FAILED

Error: ImportError: cannot import name 'cmd_add_strategy' from 'main'
============================== 6 failed in 0.33s ===============================
```

**Command:** `pytest tests/unit/web3/test_contract.py::TestAddStrategyMethod -v`

**Results:**

```
tests/unit/web3/test_contract.py::TestAddStrategyMethod::test_contract_add_strategy_success FAILED
tests/unit/web3/test_contract.py::TestAddStrategyMethod::test_contract_add_strategy_with_custom_params FAILED
tests/unit/web3/test_contract.py::TestAddStrategyMethod::test_contract_add_strategy_returns_error_on_failure FAILED
tests/unit/web3/test_contract.py::TestAddStrategyMethod::test_contract_add_strategy_default_parameters FAILED

Error: AttributeError: 'VaultContract' object has no attribute 'add_strategy'
============================== 4 failed in 0.24s ===============================
```

**Summary:**

- Total tests: 10
- Passing: 0 (expected)
- Failing: 10 (expected)
- Status: RED phase verified

**Expected Failure Messages:**

1. `ImportError: cannot import name 'cmd_add_strategy' from 'main'` - Expected until cmd_add_strategy is implemented
2. `AttributeError: 'VaultContract' object has no attribute 'add_strategy'` - Expected until add_strategy method is added

---

**Generated by BMad TEA Agent** - 2026-03-01
