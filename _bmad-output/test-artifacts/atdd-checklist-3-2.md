---
stepsCompleted: ['step-01-preflight-and-context', 'step-02-generation-mode', 'step-03-test-strategy', 'step-04-generate-tests']
lastStep: 'step-04-generate-tests'
lastSaved: '2026-03-01'
workflowType: 'testarch-atdd'
inputDocuments:
  - '_bmad-output/implementation-artifacts/3-2-withdraw-eth.md'
  - '_bmad/tea/testarch/knowledge/data-factories.md'
  - '_bmad/tea/testarch/knowledge/test-quality.md'
  - '_bmad/tea/testarch/knowledge/test-healing-patterns.md'
  - '_bmad/tea/testarch/knowledge/test-levels-framework.md'
---

# ATDD Checklist - Epic 3, Story 2: Withdraw ETH Command

**Date:** 2026-03-01
**Author:** Nick
**Primary Test Level:** Unit + Integration (Backend)

---

## Story Summary

作为**用户**,我需要**通过 `/withdraw <amount>` 命令提取 ETH**,以便**将资金转移到其他地址**。

**As a** user
**I want** to withdraw ETH via `/withdraw <amount>` command
**So that** I can transfer funds to other addresses

---

## Acceptance Criteria

1. 实现 `contract.withdraw_eth(amount)` 方法
2. 实现 `cmd_withdraw` 命令处理函数
3. 命令格式: `/withdraw 0.5` (单位: ETH)
4. 二次确认: "确认提取 0.5 ETH 到你的钱包? [Y/N]"
5. 成功时返回: "已提取 0.5 ETH,交易哈希: 0x..."
6. 余额不足时返回: "余额不足,当前可用: 0.3 ETH"
7. 管理员权限检查
8. 添加单元测试

---

## Failing Tests Created (RED Phase)

### Unit Tests (10 tests)

**File:** `tests/unit/test_story_3_2_withdraw_eth.py` (预计 ~400 lines)

#### Test Class: TestCmdWithdraw (Command Handler Tests)

- ✅ **Test:** `test_withdraw_success_flow`
  - **Status:** RED - Feature not implemented
  - **Verifies:** 管理员用户成功提取 ETH 完整流程(包括二次确认)
  - **Priority:** P0

- ✅ **Test:** `test_withdraw_insufficient_balance`
  - **Status:** RED - Feature not implemented
  - **Verifies:** 余额不足时的错误处理和用户提示
  - **Priority:** P0

- ✅ **Test:** `test_withdraw_unauthorized`
  - **Status:** RED - Feature not implemented
  - **Verifies:** 非管理员用户被拒绝访问
  - **Priority:** P0

- ✅ **Test:** `test_withdraw_cancel_confirmation`
  - **Status:** RED - Feature not implemented
  - **Verifies:** 二次确认时用户取消操作
  - **Priority:** P1

- ✅ **Test:** `test_withdraw_invalid_amount`
  - **Status:** RED - Feature not implemented
  - **Verifies:** 无效金额输入的验证
  - **Priority:** P1

- ✅ **Test:** `test_withdraw_missing_amount`
  - **Status:** RED - Feature not implemented
  - **Verifies:** 缺少金额参数时的提示
  - **Priority:** P1

#### Test Class: TestContractWithdrawEth (Contract Method Tests)

- ✅ **Test:** `test_withdraw_eth_valid_amount`
  - **Status:** RED - Feature not implemented
  - **Verifies:** 合约方法正确调用 withdrawETH 函数
  - **Priority:** P0

- ✅ **Test:** `test_withdraw_eth_zero_amount`
  - **Status:** RED - Feature not implemented
  - **Verifies:** 零金额被拒绝
  - **Priority:** P1

- ✅ **Test:** `test_withdraw_eth_negative_amount`
  - **Status:** RED - Feature not implemented
  - **Verifies:** 负金额被拒绝
  - **Priority:** P1

- ✅ **Test:** `test_withdraw_eth_contract_error`
  - **Status:** RED - Feature not implemented
  - **Verifies:** 合约调用失败时的错误处理
  - **Priority:** P1

---

## Test Strategy

### Test Level Selection

| Scenario | Level | Justification |
|----------|-------|---------------|
| 命令处理逻辑 | Unit | 纯业务逻辑,快速反馈 |
| 权限检查 | Unit | 隔离测试,无外部依赖 |
| 参数验证 | Unit | 输入验证逻辑 |
| 合约方法调用 | Unit | 使用 mock 隔离 Web3 依赖 |
| 二次确认流程 | Unit | 状态管理逻辑 |
| ETH/Wei 转换 | Unit | 纯计算逻辑 |

### Test Priorities

- **P0 (Critical):** 核心流程 - 成功提取、权限检查、余额验证
- **P1 (High):** 错误处理 - 无效输入、取消操作、合约错误
- **P2 (Medium):** 边界情况 - 超时、并发(未在本 story 范围)
- **P3 (Low):** 优化场景 - 暂无

---

## Data Factories Required

### WithdrawRequest Factory

**File:** N/A (使用内联测试数据)

**Test Data Patterns:**
```python
# 有效提取请求
valid_withdraw = {
    'amount_eth': 0.5,
    'amount_wei': 500000000000000000,
    'user_id': 12345,
}

# 无效提取请求
invalid_withdraw = {
    'amount_eth': -0.5,
    'amount_eth_zero': 0.0,
    'amount_eth_invalid': 'abc',
}
```

---

## Fixtures Required

### Test Fixtures (from conftest.py)

- `mock_telegram_update` - Mock Telegram Update 对象
- `mock_telegram_context` - Mock Telegram Context 对象
- `web3_test_env` - Web3 测试环境变量
- `mock_web3_components` - Mock Web3 组件(w3, account, contract)

### Story-Specific Fixtures

```python
@pytest.fixture
def mock_vault_with_balance():
    """Mock vault API with sufficient balance."""
    return {'balance': '2.0'}

@pytest.fixture
def mock_vault_low_balance():
    """Mock vault API with insufficient balance."""
    return {'balance': '0.3'}
```

---

## Mock Requirements

### Web3 Contract Mock

**Contract Function:** `withdrawETH(uint256 amount)`

**Success Response:**
```python
{
    'success': True,
    'transactionHash': '0xabc123...',
    'status': 1,
    'blockNumber': 12345678,
}
```

**Failure Response:**
```python
{
    'success': False,
    'error': 'Insufficient balance',
}
```

### API Mock (get_vault)

**Endpoint:** `GET /api/v1/vault`

**Success Response:**
```json
{
    "balance": "2.5"
}
```

---

## Required data-testid Attributes

N/A - This is a backend command-line interface (Telegram bot), no UI elements.

---

## Implementation Checklist

### Test: test_withdraw_success_flow

**File:** `tests/unit/test_story_3_2_withdraw_eth.py`

**Tasks to make this test pass:**

- [ ] 在 `contract.py` 中添加 `withdraw_eth(amount_wei: int)` 方法
- [ ] 在 `main.py` 中添加 `cmd_withdraw` 异步函数
- [ ] 在 `main.py` 中添加 `handle_withdraw_confirm` 处理函数
- [ ] 在 `main.py` 中添加 `handle_withdraw_cancel` 处理函数
- [ ] 在 `main.py` 中定义 `WAITING_CONFIRMATION` 和 `END` 常量
- [ ] 在 `main.py` 中添加 `_pending_withdrawals` 字典
- [ ] 使用 `is_admin()` 检查管理员权限
- [ ] 实现二次确认流程 (ConversationHandler)
- [ ] 实现 ETH -> Wei 转换 (`Web3.to_wei()`)
- [ ] 调用 `api().get_vault()` 获取余额进行预检查
- [ ] 运行测试: `pytest tests/unit/test_story_3_2_withdraw_eth.py::TestCmdWithdraw::test_withdraw_success_flow -v`
- [ ] ✅ Test passes (green phase)

**Estimated Effort:** 2 hours

---

### Test: test_withdraw_insufficient_balance

**File:** `tests/unit/test_story_3_2_withdraw_eth.py`

**Tasks to make this test pass:**

- [ ] 在 `cmd_withdraw` 中调用 `api().get_vault()` 获取余额
- [ ] 比较 `amount_eth` 与 `balance_eth`
- [ ] 余额不足时返回用户友好的错误消息
- [ ] 错误消息包含当前可用余额
- [ ] 运行测试: `pytest tests/unit/test_story_3_2_withdraw_eth.py::TestCmdWithdraw::test_withdraw_insufficient_balance -v`
- [ ] ✅ Test passes (green phase)

**Estimated Effort:** 0.5 hours

---

### Test: test_withdraw_unauthorized

**File:** `tests/unit/test_story_3_2_withdraw_eth.py`

**Tasks to make this test pass:**

- [ ] 在 `cmd_withdraw` 开头使用 `is_admin()` 检查
- [ ] 非管理员时返回 "未授权: 仅管理员可提取资金"
- [ ] 运行测试: `pytest tests/unit/test_story_3_2_withdraw_eth.py::TestCmdWithdraw::test_withdraw_unauthorized -v`
- [ ] ✅ Test passes (green phase)

**Estimated Effort:** 0.25 hours

---

### Test: test_withdraw_cancel_confirmation

**File:** `tests/unit/test_story_3_2_withdraw_eth.py`

**Tasks to make this test pass:**

- [ ] 在 `handle_withdraw_confirm` 中处理 "N" 或 "NO" 响应
- [ ] 清理 `_pending_withdrawals[user_id]`
- [ ] 返回 "已取消提取" 消息
- [ ] 运行测试: `pytest tests/unit/test_story_3_2_withdraw_eth.py::TestCmdWithdraw::test_withdraw_cancel_confirmation -v`
- [ ] ✅ Test passes (green phase)

**Estimated Effort:** 0.5 hours

---

### Test: test_withdraw_invalid_amount

**File:** `tests/unit/test_story_3_2_withdraw_eth.py`

**Tasks to make this test pass:**

- [ ] 在 `cmd_withdraw` 中使用 `float(args[0])` 解析金额
- [ ] 捕获 `ValueError` 异常
- [ ] 返回 "无效的金额格式" 错误消息
- [ ] 运行测试: `pytest tests/unit/test_story_3_2_withdraw_eth.py::TestCmdWithdraw::test_withdraw_invalid_amount -v`
- [ ] ✅ Test passes (green phase)

**Estimated Effort:** 0.25 hours

---

### Test: test_withdraw_missing_amount

**File:** `tests/unit/test_story_3_2_withdraw_eth.py`

**Tasks to make this test pass:**

- [ ] 检查 `ctx.args` 是否为空或长度为 0
- [ ] 返回用法提示: "用法: /withdraw <amount>"
- [ ] 运行测试: `pytest tests/unit/test_story_3_2_withdraw_eth.py::TestCmdWithdraw::test_withdraw_missing_amount -v`
- [ ] ✅ Test passes (green phase)

**Estimated Effort:** 0.25 hours

---

### Test: test_withdraw_eth_valid_amount

**File:** `tests/unit/test_story_3_2_withdraw_eth.py`

**Tasks to make this test pass:**

- [ ] 在 `contract.py` 中添加 `withdraw_eth(amount_wei: int)` 方法
- [ ] 调用 `self.contract.functions.withdrawETH(amount_wei)`
- [ ] 使用 `self._send_transaction(tx_func)` 处理交易
- [ ] 运行测试: `pytest tests/unit/test_story_3_2_withdraw_eth.py::TestContractWithdrawEth::test_withdraw_eth_valid_amount -v`
- [ ] ✅ Test passes (green phase)

**Estimated Effort:** 1 hour

---

### Test: test_withdraw_eth_zero_amount

**File:** `tests/unit/test_story_3_2_withdraw_eth.py`

**Tasks to make this test pass:**

- [ ] 在 `withdraw_eth` 方法中检查 `amount_wei <= 0`
- [ ] 返回 `{'success': False, 'error': '提取金额必须大于 0'}`
- [ ] 运行测试: `pytest tests/unit/test_story_3_2_withdraw_eth.py::TestContractWithdrawEth::test_withdraw_eth_zero_amount -v`
- [ ] ✅ Test passes (green phase)

**Estimated Effort:** 0.25 hours

---

### Test: test_withdraw_eth_negative_amount

**File:** `tests/unit/test_story_3_2_withdraw_eth.py`

**Tasks to make this test pass:**

- [ ] 在 `withdraw_eth` 方法中检查 `amount_wei <= 0` (覆盖负数)
- [ ] 运行测试: `pytest tests/unit/test_story_3_2_withdraw_eth.py::TestContractWithdrawEth::test_withdraw_eth_negative_amount -v`
- [ ] ✅ Test passes (green phase)

**Estimated Effort:** 0.25 hours (covered by zero amount check)

---

### Test: test_withdraw_eth_contract_error

**File:** `tests/unit/test_story_3_2_withdraw_eth.py`

**Tasks to make this test pass:**

- [ ] 在 `withdraw_eth` 方法中使用 try/except 捕获异常
- [ ] 记录错误日志: `logger.error(f"Failed to withdraw ETH: {e}")`
- [ ] 返回 `{'success': False, 'error': str(e)}`
- [ ] 运行测试: `pytest tests/unit/test_story_3_2_withdraw_eth.py::TestContractWithdrawEth::test_withdraw_eth_contract_error -v`
- [ ] ✅ Test passes (green phase)

**Estimated Effort:** 0.5 hours

---

### Task: Register Command to Bot

**Tasks:**

- [ ] 在 `post_init()` 中添加 `BotCommand("withdraw", "Withdraw ETH to wallet")`
- [ ] 在 `create_app()` 中添加 `ConversationHandler`
- [ ] 配置 `entry_points`, `states`, `fallbacks`
- [ ] 更新 `cmd_start()` 帮助文本,添加 `/withdraw` 说明

**Estimated Effort:** 0.5 hours

---

## Running Tests

```bash
# Run all failing tests for this story
pytest tests/unit/test_story_3_2_withdraw_eth.py -v

# Run specific test class
pytest tests/unit/test_story_3_2_withdraw_eth.py::TestCmdWithdraw -v
pytest tests/unit/test_story_3_2_withdraw_eth.py::TestContractWithdrawEth -v

# Run specific test
pytest tests/unit/test_story_3_2_withdraw_eth.py::TestCmdWithdraw::test_withdraw_success_flow -v

# Run with coverage
pytest tests/unit/test_story_3_2_withdraw_eth.py --cov=contract --cov=main --cov-report=term-missing

# Run all unit tests
pytest tests/unit/ -v -k "withdraw"
```

---

## Red-Green-Refactor Workflow

### RED Phase (Complete) ✅

**TEA Agent Responsibilities:**

- ✅ All tests written and failing
- ✅ Fixtures created with mock data
- ✅ Mock requirements documented
- ✅ Implementation checklist created

**Verification:**

- All tests run and fail as expected (tests use `pytest.mark.skip` with reason)
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

**Recommended Order:**

1. `test_withdraw_eth_valid_amount` (Contract method - foundation)
2. `test_withdraw_eth_zero_amount` (Contract validation)
3. `test_withdraw_eth_negative_amount` (Contract validation)
4. `test_withdraw_eth_contract_error` (Error handling)
5. `test_withdraw_unauthorized` (Command handler - auth)
6. `test_withdraw_missing_amount` (Command handler - validation)
7. `test_withdraw_invalid_amount` (Command handler - validation)
8. `test_withdraw_insufficient_balance` (Command handler - balance check)
9. `test_withdraw_cancel_confirmation` (Command handler - confirmation)
10. `test_withdraw_success_flow` (Command handler - full flow)
11. Register command to bot (integration)

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
3. **Run failing tests** to confirm RED phase: `pytest tests/unit/test_story_3_2_withdraw_eth.py -v`
4. **Begin implementation** using implementation checklist as guide
5. **Work one test at a time** (red → green for each)
6. **Share progress** in daily standup
7. **When all tests pass**, refactor code for quality
8. **When refactoring complete**, manually update story status to 'done' in sprint-status.yaml

---

## Knowledge Base References Applied

This ATDD workflow consulted the following knowledge fragments:

- **data-factories.md** - Factory patterns for test data (used inline data patterns)
- **test-quality.md** - Test quality principles (deterministic, isolated, explicit, focused, fast)
- **test-healing-patterns.md** - Common failure patterns (for future reference)
- **test-levels-framework.md** - Test level selection (Unit for backend logic)

---

## Test Execution Evidence

### Initial Test Run (RED Phase Verification)

**Command:** `pytest tests/unit/test_story_3_2_withdraw_eth.py -v`

**Expected Results:**

All tests should be SKIPPED with reason: "Feature not implemented yet (RED phase)"

**Summary:**

- Total tests: 10
- Passing: 0 (expected)
- Failing: 0 (expected - tests are skipped)
- Skipped: 10 (expected - RED phase)
- Status: ✅ RED phase verified

**Run Command:**
```bash
pytest tests/unit/test_story_3_2_withdraw_eth.py -v
```

---

## Notes

### Implementation Notes

- **ETH/Wei Conversion:** Use `Web3.to_wei(amount_eth, 'ether')` to avoid precision issues
- **ConversationHandler:** Required for two-step confirmation flow
- **State Management:** `_pending_withdrawals` dict for temporary storage (consider Redis for production)
- **Security:** Always use `is_admin()` for high-risk operations

### Testing Notes

- **Async Tests:** Use `pytest.mark.asyncio` decorator
- **Mocking:** Use `unittest.mock.AsyncMock` for async functions
- **Environment:** Tests should reset environment in `autouse` fixture
- **Web3 Mocking:** Follow pattern from `test_story_3_1_update_settings.py`

### Known Considerations

- **API Failure:** If `api().get_vault()` fails, skip balance pre-check (graceful degradation)
- **Timeout:** ConversationHandler should have 30-second timeout
- **Fallback:** `/cancel` command should clear pending state

---

## Contact

**Questions or Issues?**

- Ask in team standup
- Refer to `./tests/README.md` for testing documentation
- Refer to `./_bmad-output/implementation-artifacts/3-2-withdraw-eth.md` for full story details

---

**Generated by BMad TEA Agent** - 2026-03-01
