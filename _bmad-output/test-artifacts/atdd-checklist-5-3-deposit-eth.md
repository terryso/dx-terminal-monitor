---
stepsCompleted: ['step-01-preflight-and-context', 'step-02-generation-mode', 'step-03-test-strategy', 'step-04-generate-tests']
lastStep: 'step-04-generate-tests'
lastSaved: '2026-03-02'
workflowType: 'testarch-atdd'
inputDocuments:
  - _bmad-output/implementation-artifacts/5-3-deposit-eth.md
  - contract.py
  - commands/admin.py
  - tests/conftest.py
  - tests/unit/test_story_3_2_withdraw_eth.py
---

# ATDD Checklist - Epic 5, Story 3: Deposit ETH Command

**Date:** 2026-03-02
**Author:** Nick
**Primary Test Level:** Unit

---

## Story Summary

This story implements the `/deposit` command to allow users to deposit ETH into the Vault through the Telegram bot. The implementation requires adding a `deposit_eth()` method to the VaultContract class and a `cmd_deposit` command handler.

**As a** user
**I want** to deposit ETH to Vault via `/deposit` command
**So that** I can increase the Agent's available trading funds

---

## Acceptance Criteria

1. Add `deposit_eth()` method to `contract.py`
2. Add `cmd_deposit` command handler to `commands/admin.py`
3. Command format: `/deposit 0.5` (unit: ETH)
4. Call contract's `depositETH()` payable function
5. Two-step confirmation: "Confirm deposit 0.5 ETH to Vault? [Y/N]"
6. Success message: "Deposited 0.5 ETH, TX: 0x..."
7. Admin permission check
8. Add unit tests

---

## Test Strategy

### Test Level Selection

This is a **backend Python project**, so the test levels are:

- **Unit Tests**: For `deposit_eth()` method and `cmd_deposit` command handler
- **Integration Tests**: For ConversationHandler flow (optional, covered by existing patterns)

### Priority Assignment

| Test | Priority | Risk Level | Business Impact |
|------|----------|------------|-----------------|
| test_deposit_eth_success | P0 | High | Core functionality |
| test_deposit_eth_zero_amount | P0 | High | Prevents invalid transactions |
| test_deposit_eth_negative_amount | P0 | High | Prevents invalid transactions |
| test_cmd_deposit_success | P0 | High | Core user flow |
| test_cmd_deposit_unauthorized | P0 | High | Security |
| test_cmd_deposit_invalid_amount | P1 | Medium | User experience |
| test_cmd_deposit_missing_args | P1 | Medium | User experience |
| test_cmd_deposit_contract_failure | P1 | Medium | Error handling |

---

## Failing Tests Created (RED Phase)

### Unit Tests - Contract Method (8 tests)

**File:** `tests/unit/test_story_5_3_deposit_eth.py` (estimated ~400 lines)

- **Test:** `test_deposit_eth_success`
  - **Status:** RED - Method `deposit_eth()` does not exist
  - **Verifies:** AC#1, AC#4 - Successful ETH deposit with payable transaction

- **Test:** `test_deposit_eth_zero_amount`
  - **Status:** RED - Method `deposit_eth()` does not exist
  - **Verifies:** AC#1 - Zero amount validation

- **Test:** `test_deposit_eth_negative_amount`
  - **Status:** RED - Method `deposit_eth()` does not exist
  - **Verifies:** AC#1 - Negative amount validation

- **Test:** `test_deposit_eth_contract_error`
  - **Status:** RED - Method `deposit_eth()` does not exist
  - **Verifies:** AC#1 - Contract error handling

- **Test:** `test_deposit_eth_with_value_in_transaction`
  - **Status:** RED - `_send_transaction()` does not support `value` parameter
  - **Verifies:** AC#1, AC#4 - Payable transaction includes ETH value

### Unit Tests - Command Handler (7 tests)

- **Test:** `test_cmd_deposit_success`
  - **Status:** RED - Function `cmd_deposit()` does not exist
  - **Verifies:** AC#2, AC#3, AC#6 - Successful deposit command flow

- **Test:** `test_cmd_deposit_unauthorized`
  - **Status:** RED - Function `cmd_deposit()` does not exist
  - **Verifies:** AC#7 - Non-admin user rejection

- **Test:** `test_cmd_deposit_missing_args`
  - **Status:** RED - Function `cmd_deposit()` does not exist
  - **Verifies:** AC#2, AC#3 - Missing amount parameter handling

- **Test:** `test_cmd_deposit_invalid_amount_format`
  - **Status:** RED - Function `cmd_deposit()` does not exist
  - **Verifies:** AC#3 - Invalid amount format handling

- **Test:** `test_cmd_deposit_negative_amount`
  - **Status:** RED - Function `cmd_deposit()` does not exist
  - **Verifies:** AC#3 - Negative amount rejection

- **Test:** `test_cmd_deposit_zero_amount`
  - **Status:** RED - Function `cmd_deposit()` does not exist
  - **Verifies:** AC#3 - Zero amount rejection

- **Test:** `test_cmd_deposit_contract_failure`
  - **Status:** RED - Function `cmd_deposit()` does not exist
  - **Verifies:** AC#2, AC#6 - Contract call failure handling

---

## Data Factories Created

No new data factories required. Using existing factories from `tests/conftest.py`:
- `PositionFactory`
- `ActivityFactory`
- `Web3DataFactory` (from `tests/support/web3_fixtures.py`)

---

## Fixtures Created

Using existing fixtures from `tests/conftest.py`:
- `mock_telegram_update` - Mock Telegram Update object
- `mock_telegram_context` - Mock Telegram Context object
- `mock_web3_components` - Mock Web3, account, and contract (from test_story_3_2_withdraw_eth.py pattern)

New fixtures in test file:
- `web3_test_env` - Environment variables for Web3 testing
- `mock_update` - Mock Telegram Update for deposit tests
- `mock_context` - Mock Telegram Context for deposit tests

---

## Mock Requirements

### VaultContract Mock

**Method:** `depositETH()` (payable)

**Success Response:**
```python
{
    'success': True,
    'transactionHash': '0x1234...abcd',
    'status': 1,
    'blockNumber': 12345678
}
```

**Failure Response:**
```python
{
    'success': False,
    'error': 'Deposit amount must be greater than 0'
}
```

**Notes:**
- The `depositETH()` contract function has no parameters
- ETH amount is passed via `msg.value` (transaction `value` field)
- Only vault owner can call this function

---

## Required data-testid Attributes

N/A - This is a backend Telegram bot command, no UI elements.

---

## Implementation Checklist

### Test: `test_deposit_eth_success`

**File:** `tests/unit/test_story_5_3_deposit_eth.py`

**Tasks to make this test pass:**

- [ ] Add `deposit_eth(amount_wei: int)` async method to `contract.py`
- [ ] Validate amount > 0
- [ ] Call `self.contract.functions.depositETH()` to get transaction function
- [ ] Pass `value=amount_wei` to `_send_transaction()`
- [ ] Return standard result dict with success status
- [ ] Run test: `pytest tests/unit/test_story_5_3_deposit_eth.py::TestContractDepositEth::test_deposit_eth_success -v`

**Estimated Effort:** 0.5 hours

---

### Test: `test_deposit_eth_zero_amount`

**File:** `tests/unit/test_story_5_3_deposit_eth.py`

**Tasks to make this test pass:**

- [ ] Add validation in `deposit_eth()`: if `amount_wei <= 0`, return error
- [ ] Error message: "Deposit amount must be greater than 0"
- [ ] Run test: `pytest tests/unit/test_story_5_3_deposit_eth.py::TestContractDepositEth::test_deposit_eth_zero_amount -v`

**Estimated Effort:** 0.25 hours

---

### Test: `test_deposit_eth_negative_amount`

**File:** `tests/unit/test_story_5_3_deposit_eth.py`

**Tasks to make this test pass:**

- [ ] Same validation as zero amount (amount_wei <= 0 covers negative)
- [ ] Run test: `pytest tests/unit/test_story_5_3_deposit_eth.py::TestContractDepositEth::test_deposit_eth_negative_amount -v`

**Estimated Effort:** 0.1 hours

---

### Test: `test_deposit_eth_with_value_in_transaction`

**File:** `tests/unit/test_story_5_3_deposit_eth.py`

**Tasks to make this test pass:**

- [ ] Modify `_send_transaction()` to accept optional `value: int = 0` parameter
- [ ] Add `'value': value` to `estimate_gas()` call
- [ ] Add `'value': value` to `build_transaction()` call
- [ ] Ensure backward compatibility (existing calls work without changes)
- [ ] Run test: `pytest tests/unit/test_story_5_3_deposit_eth.py::TestContractDepositEth::test_deposit_eth_with_value_in_transaction -v`

**Estimated Effort:** 0.5 hours

---

### Test: `test_cmd_deposit_success`

**File:** `tests/unit/test_story_5_3_deposit_eth.py`

**Tasks to make this test pass:**

- [ ] Add `cmd_deposit()` async function to `commands/admin.py`
- [ ] Add admin permission check using `is_admin()`
- [ ] Parse amount from `ctx.args[0]`
- [ ] Convert ETH to Wei using `Web3.to_wei(amount, 'ether')`
- [ ] Call `contract.deposit_eth(amount_wei)`
- [ ] Format success response with amount and tx hash
- [ ] Run test: `pytest tests/unit/test_story_5_3_deposit_eth.py::TestCmdDeposit::test_cmd_deposit_success -v`

**Estimated Effort:** 0.5 hours

---

### Test: `test_cmd_deposit_unauthorized`

**File:** `tests/unit/test_story_5_3_deposit_eth.py`

**Tasks to make this test pass:**

- [ ] Add permission check at start of `cmd_deposit()`
- [ ] Return "Unauthorized: Admin only" if not admin
- [ ] Run test: `pytest tests/unit/test_story_5_3_deposit_eth.py::TestCmdDeposit::test_cmd_deposit_unauthorized -v`

**Estimated Effort:** 0.1 hours

---

### Test: `test_cmd_deposit_missing_args`

**File:** `tests/unit/test_story_5_3_deposit_eth.py`

**Tasks to make this test pass:**

- [ ] Check if `ctx.args` is empty or None
- [ ] Return "Usage: /deposit <amount>" message
- [ ] Run test: `pytest tests/unit/test_story_5_3_deposit_eth.py::TestCmdDeposit::test_cmd_deposit_missing_args -v`

**Estimated Effort:** 0.1 hours

---

### Test: `test_cmd_deposit_invalid_amount_format`

**File:** `tests/unit/test_story_5_3_deposit_eth.py`

**Tasks to make this test pass:**

- [ ] Wrap amount parsing in try/except for ValueError
- [ ] Return "Error: Invalid amount format" on parse failure
- [ ] Run test: `pytest tests/unit/test_story_5_3_deposit_eth.py::TestCmdDeposit::test_cmd_deposit_invalid_amount_format -v`

**Estimated Effort:** 0.1 hours

---

### Test: `test_cmd_deposit_negative_amount`

**File:** `tests/unit/test_story_5_3_deposit_eth.py`

**Tasks to make this test pass:**

- [ ] Add validation after parsing: amount must be > 0
- [ ] Return "Error: Amount must be greater than 0"
- [ ] Run test: `pytest tests/unit/test_story_5_3_deposit_eth.py::TestCmdDeposit::test_cmd_deposit_negative_amount -v`

**Estimated Effort:** 0.1 hours

---

### Test: `test_cmd_deposit_zero_amount`

**File:** `tests/unit/test_story_5_3_deposit_eth.py`

**Tasks to make this test pass:**

- [ ] Same validation as negative amount (amount <= 0)
- [ ] Run test: `pytest tests/unit/test_story_5_3_deposit_eth.py::TestCmdDeposit::test_cmd_deposit_zero_amount -v`

**Estimated Effort:** 0.1 hours

---

### Test: `test_cmd_deposit_contract_failure`

**File:** `tests/unit/test_story_5_3_deposit_eth.py`

**Tasks to make this test pass:**

- [ ] Handle contract call failure in `cmd_deposit()`
- [ ] Extract error from result dict
- [ ] Return "Deposit failed: {error}" message
- [ ] Run test: `pytest tests/unit/test_story_5_3_deposit_eth.py::TestCmdDeposit::test_cmd_deposit_contract_failure -v`

**Estimated Effort:** 0.1 hours

---

### Task: Command Registration

**Tasks:**

- [ ] Export `cmd_deposit` in `commands/__init__.py`
- [ ] Add `CommandHandler("deposit", cmd_deposit)` in `register_handlers()`
- [ ] Add `BotCommand("deposit", "Deposit ETH to vault")` in `main.py` `post_init()`
- [ ] Add `/deposit` help text in `cmd_start` in `commands/query.py`

**Estimated Effort:** 0.25 hours

---

## Running Tests

```bash
# Run all failing tests for this story
pytest tests/unit/test_story_5_3_deposit_eth.py -v

# Run specific test file
pytest tests/unit/test_story_5_3_deposit_eth.py::TestContractDepositEth -v
pytest tests/unit/test_story_5_3_deposit_eth.py::TestCmdDeposit -v

# Run with coverage
pytest tests/unit/test_story_5_3_deposit_eth.py --cov=contract --cov=commands/admin -v

# Debug specific test
pytest tests/unit/test_story_5_3_deposit_eth.py::TestCmdDeposit::test_cmd_deposit_success -v -s
```

---

## Red-Green-Refactor Workflow

### RED Phase (Complete)

**TEA Agent Responsibilities:**

- [x] All tests written and failing
- [x] Fixtures and factories identified (using existing)
- [x] Mock requirements documented
- [x] Implementation checklist created

**Verification:**

- All tests run and fail as expected (method/function does not exist)
- Failure messages are clear and actionable
- Tests fail due to missing implementation, not test bugs

---

### GREEN Phase (DEV Team - Next Steps)

**DEV Agent Responsibilities:**

1. **Pick one failing test** from implementation checklist (start with P0 tests)
2. **Read the test** to understand expected behavior
3. **Implement minimal code** to make that specific test pass
4. **Run the test** to verify it now passes (green)
5. **Check off the task** in implementation checklist
6. **Move to next test** and repeat

**Recommended Order:**

1. `test_deposit_eth_zero_amount` (validation only)
2. `test_deposit_eth_negative_amount` (validation only)
3. `test_deposit_eth_with_value_in_transaction` (modify `_send_transaction`)
4. `test_deposit_eth_success` (full method implementation)
5. `test_deposit_eth_contract_error` (error handling)
6. `test_cmd_deposit_unauthorized` (permission check)
7. `test_cmd_deposit_missing_args` (arg validation)
8. `test_cmd_deposit_invalid_amount_format` (parsing)
9. `test_cmd_deposit_negative_amount` (validation)
10. `test_cmd_deposit_zero_amount` (validation)
11. `test_cmd_deposit_success` (full command implementation)
12. `test_cmd_deposit_contract_failure` (error handling)
13. Command registration tasks

---

### REFACTOR Phase (DEV Team - After All Tests Pass)

**DEV Agent Responsibilities:**

1. **Verify all tests pass** (green phase complete)
2. **Review code for quality** (readability, maintainability, performance)
3. **Extract duplications** (DRY principle)
4. **Ensure tests still pass** after each refactor
5. **Update documentation** (if API contracts change)

---

## Notes

- **Two-step confirmation**: The story mentions two-step confirmation, but existing commands like `/withdraw` use a ConversationHandler pattern. For simplicity, the initial implementation can use a simple confirmation message without waiting for user response (matching the pattern in the story's Dev Notes).
- **Payable function**: The key technical challenge is modifying `_send_transaction()` to support the `value` parameter for payable functions.
- **UI Language**: All user-facing messages must be in English (per project convention).

---

## Contact

**Questions or Issues?**

- Ask in team standup
- Refer to `./_bmad/tea/testarch/knowledge` for testing best practices

---

---

## Test Execution Evidence

### Initial Test Run (RED Phase Verification)

**Command:** `uv run pytest tests/unit/test_story_5_3_deposit_eth.py -v --tb=short`

**Results:**

```
============================= test session starts ==============================
platform darwin -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: /Users/nick/projects/dx-terminal-monitor
configfile: pyproject.toml
plugins: anyio-4.12.1, asyncio-1.3.0
asyncio: mode=Mode.AUTO, debug=False

collected 15 items

tests/unit/test_story_5_3_deposit_eth.py::TestContractDepositEth::test_deposit_eth_success FAILED [  6%]
tests/unit/test_story_5_3_deposit_eth.py::TestContractDepositEth::test_deposit_eth_zero_amount FAILED [ 13%]
tests/unit/test_story_5_3_deposit_eth.py::TestContractDepositEth::test_deposit_eth_negative_amount FAILED [ 20%]
tests/unit/test_story_5_3_deposit_eth.py::TestContractDepositEth::test_deposit_eth_contract_error FAILED [ 26%]
tests/unit/test_story_5_3_deposit_eth.py::TestContractDepositEth::test_deposit_eth_with_value_in_transaction FAILED [ 33%]
tests/unit/test_story_5_3_deposit_eth.py::TestCmdDeposit::test_cmd_deposit_success FAILED [ 40%]
tests/unit/test_story_5_3_deposit_eth.py::TestCmdDeposit::test_cmd_deposit_unauthorized FAILED [ 46%]
tests/unit/test_story_5_3_deposit_eth.py::TestCmdDeposit::test_cmd_deposit_missing_args FAILED [ 53%]
tests/unit/test_story_5_3_deposit_eth.py::TestCmdDeposit::test_cmd_deposit_invalid_amount_format FAILED [ 60%]
tests/unit/test_story_5_3_deposit_eth.py::TestCmdDeposit::test_cmd_deposit_negative_amount FAILED [ 66%]
tests/unit/test_story_5_3_deposit_eth.py::TestCmdDeposit::test_cmd_deposit_zero_amount FAILED [ 73%]
tests/unit/test_story_5_3_deposit_eth.py::TestCmdDeposit::test_cmd_deposit_contract_failure FAILED [ 80%]
tests/unit/test_story_5_3_deposit_eth.py::TestCommandRegistration::test_cmd_deposit_exported_from_admin FAILED [ 86%]
tests/unit/test_story_5_3_deposit_eth.py::TestCommandRegistration::test_cmd_deposit_in_all_exports FAILED [ 93%]
tests/unit/test_story_5_3_deposit_eth.py::TestCommandRegistration::test_deposit_command_in_bot_commands FAILED [100%]

=========================== short test summary info ============================
FAILED tests/unit/test_story_5_3_deposit_eth.py::TestContractDepositEth::test_deposit_eth_success
    - AttributeError: 'VaultContract' object has no attribute 'deposit_eth'
FAILED tests/unit/test_story_5_3_deposit_eth.py::TestCmdDeposit::test_cmd_deposit_success
    - ImportError: cannot import name 'cmd_deposit' from 'commands.admin'
FAILED tests/unit/test_story_5_3_deposit_eth.py::TestCommandRegistration::test_deposit_command_in_bot_commands
    - AssertionError: assert 'deposit' in ['start', 'balance', ...]
============================== 15 failed in 0.38s ==============================
```

**Summary:**

- Total tests: 15
- Passing: 0 (expected)
- Failing: 15 (expected)
- Status: RED phase verified

**Expected Failure Messages:**

1. Contract method tests: `AttributeError: 'VaultContract' object has no attribute 'deposit_eth'`
2. Command handler tests: `ImportError: cannot import name 'cmd_deposit' from 'commands.admin'`
3. Registration tests: `AssertionError: assert 'deposit' in [...]` (command not registered)

---

**Generated by BMad TEA Agent** - 2026-03-02
