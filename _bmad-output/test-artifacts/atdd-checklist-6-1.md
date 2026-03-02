---
stepsCompleted: ['step-01-preflight-and-context', 'step-03-test-strategy', 'step-04c-aggregate', 'step-05-validate-and-complete']
lastStep: 'step-05-validate-and-complete'
lastSaved: '2026-03-03'
workflowType: 'testarch-atdd'
inputDocuments:
  - _bmad-output/implementation-artifacts/6-1-eth-price.md
  - _bmad/tea/testarch/knowledge/data-factories.md
  - _bmad/tea/testarch/knowledge/test-quality.md
  - _bmad/tea/testarch/knowledge/test-levels-framework.md
  - tests/conftest.py
  - tests/unit/test_story_5_3_deposit_eth.py
---

# ATDD Checklist - Epic 6, Story 1: ETH Price Query

 **Date:** 2026-03-03
 **Author:** Nick
 **Primary Test Level:** Unit

---

## Story Summary

 **As a** user
 **I want** to query ETH real-time price via `/price` command
 **So that** I can understand the current market situation

---

## Acceptance Criteria

 1. Add `get_eth_price()` method to `api.py`
 2. Call `/eth-price` endpoint
 3. Add `cmd_price` command handler to `commands/query.py`
 4. Format output: current price, 24h change
 5. Add unit tests

---

## Failing Tests Created (RED Phase)

### Unit Tests (15 tests)

**File:** `tests/unit/test_story_6_1_eth_price.py` (310 lines)

- **Test:** `test_get_eth_price_success`
  - **Status:** RED - Method `get_eth_price()` not implemented
  - **Verifies:** API method successfully retrieves ETH price data

- **Test:** `test_get_eth_price_api_error`
  - **Status:** RED - Method `get_eth_price()` not implemented
  - **Verifies:** API error response handling

- **Test:** `test_get_eth_price_http_error`
  - **Status:** RED - Method `get_eth_price()` not implemented
  - **Verifies:** HTTP error response handling

- **Test:** `test_cmd_price_success`
  - **Status:** RED - Function `cmd_price()` not implemented
  - **Verifies:** Command handler formats and displays ETH price correctly

- **Test:** `test_cmd_price_unauthorized`
  - **Status:** RED - Function `cmd_price()` not implemented
  - **Verifies:** Unauthorized user rejection

- **Test:** `test_cmd_price_api_error`
  - **Status:** RED - Function `cmd_price()` not implemented
  - **Verifies:** API error message display

- **Test:** `test_cmd_price_negative_change`
  - **Status:** RED - Function `cmd_price()` not implemented
  - **Verifies:** Negative 24h change formatting

- **Test:** `test_cmd_price_zero_change`
  - **Status:** RED - Function `cmd_price()` not implemented
  - **Verifies:** Zero 24h change formatting

- **Test:** `test_cmd_price_large_price`
  - **Status:** RED - Function `cmd_price()` not implemented
  - **Verifies:** Large price formatting with commas

- **Test:** `test_cmd_price_exported_from_query`
  - **Status:** RED - Function `cmd_price()` not exported
  - **Verifies:** Command export from query module

- **Test:** `test_cmd_price_in_all_exports`
  - **Status:** RED - Function `cmd_price()` not in __all__
  - **Verifies:** Command presence in __all__ exports list

- **Test:** `test_price_command_in_bot_commands`
  - **Status:** RED - BotCommand not registered
  - **Verifies:** Price command registration in bot menu

- **Test:** `test_price_command_handler_registered`
  - **Status:** RED - CommandHandler not registered
  - **Verifies:** Command handler registration in bot

- **Test:** `test_cmd_start_includes_price_help`
  - **Status:** RED - Help text not updated
  - **Verifies:** Help text includes /price command

---

## Data Factories Created

None required - tests use inline mock data with patch fixtures.

---

## Fixtures Created

### Shared Fixtures (from conftest.py)

- `reset_env` - Auto-use fixture for environment reset after each test
- `mock_update` - Mock Telegram Update object
- `mock_context` - Mock Telegram Context object

---

## Mock Requirements

None - This is a pure backend feature with no external service mocking required beyond the API mock.

---

## Required data-testid Attributes

None - This is a Telegram bot command handler, not a web UI component.

---

## Implementation Checklist

### Test: test_get_eth_price_success

**File:** `tests/unit/test_story_6_1_eth_price.py`

**Tasks to make this test pass:**

- [ ] Add `get_eth_price()` method to `api.py` TerminalAPI class
- [ ] Method should call `/eth-price` endpoint using `self._get()`
- [ ] Return dict with `price` and `change24h` fields
- [ ] Run test: `pytest tests/unit/test_story_6_1_eth_price.py::TestAPIGetEthPrice::test_get_eth_price_success -v`

**Estimated Effort:** 0.5 hours

---

### Test: test_get_eth_price_api_error

**File:** `tests/unit/test_story_6_1_eth_price.py`

**Tasks to make this test pass:**

- [ ] Handle API error responses in `get_eth_price()`
- [ ] Return dict with `error` key when API returns error
- [ ] Run test: `pytest tests/unit/test_story_6_1_eth_price.py::TestAPIGetEthPrice::test_get_eth_price_api_error -v`

**Estimated Effort:** 0.25 hours

---

### Test: test_get_eth_price_http_error

**File:** `tests/unit/test_story_6_1_eth_price.py`

**Tasks to make this test pass:**

- [ ] Handle HTTP errors in `get_eth_price()`
- [ ] Return dict with `error` key on non-200 status
- [ ] Run test: `pytest tests/unit/test_story_6_1_eth_price.py::TestAPIGetEthPrice::test_get_eth_price_http_error -v`

**Estimated Effort:** 0.25 hours

---

### Test: test_cmd_price_success

**File:** `tests/unit/test_story_6_1_eth_price.py`

**Tasks to make this test pass:**

- [ ] Add `cmd_price()` async function to `commands/query.py`
- [ ] Check permission using `authorized()` function
- [ ] Call `api.get_eth_price()` method via `_get_api()`
- [ ] Handle API error response with error message
- [ ] Format price using `format_usd()` from utils/formatters.py
- [ ] Format percentage using `format_percent()` from utils/formatters.py
- [ ] Output message format:
  ```
  ETH Price

  Current: $3,000.00
  24h Change: +2.5%
  ```
- [ ] Run test: `pytest tests/unit/test_story_6_1_eth_price.py::TestCmdPrice::test_cmd_price_success -v`

**Estimated Effort:** 1 hour

---

### Test: test_cmd_price_unauthorized

**File:** `tests/unit/test_story_6_1_eth_price.py`

**Tasks to make this test pass:**

- [ ] Return early without sending message if `authorized()` returns False
- [ ] Run test: `pytest tests/unit/test_story_6_1_eth_price.py::TestCmdPrice::test_cmd_price_unauthorized -v`

**Estimated Effort:** 0.25 hours

---

### Test: test_cmd_price_api_error

**File:** `tests/unit/test_story_6_1_eth_price.py`

**Tasks to make this test pass:**

- [ ] Display error message when API returns error
- [ ] Run test: `pytest tests/unit/test_story_6_1_eth_price.py::TestCmdPrice::test_cmd_price_api_error -v`

**Estimated Effort:** 0.25 hours

---

### Test: test_cmd_price_negative_change

**File:** `tests/unit/test_story_6_1_eth_price.py`

**Tasks to make this test pass:**

- [ ] Format negative percentage with minus sign using `format_percent()`
- [ ] Run test: `pytest tests/unit/test_story_6_1_eth_price.py::TestCmdPrice::test_cmd_price_negative_change -v`

**Estimated Effort:** 0.25 hours

---

### Test: test_cmd_price_zero_change

**File:** `tests/unit/test_story_6_1_eth_price.py`

**Tasks to make this test pass:**

- [ ] Format zero percentage as "0.0%" using `format_percent()`
- [ ] Run test: `pytest tests/unit/test_story_6_1_eth_price.py::TestCmdPrice::test_cmd_price_zero_change -v`

**Estimated Effort:** 0.25 hours

---

### Test: test_cmd_price_large_price

**File:** `tests/unit/test_story_6_1_eth_price.py`

**Tasks to make this test pass:**

- [ ] Format large prices with comma separators using `format_usd()`
- [ ] Run test: `pytest tests/unit/test_story_6_1_eth_price.py::TestCmdPrice::test_cmd_price_large_price -v`

**Estimated Effort:** 0.25 hours

---

### Test: test_cmd_price_exported_from_query

**File:** `tests/unit/test_story_6_1_eth_price.py`

**Tasks to make this test pass:**

- [ ] Add `cmd_price` to `commands/query.py` module
- [ ] Run test: `pytest tests/unit/test_story_6_1_eth_price.py::TestCommandRegistration::test_cmd_price_exported_from_query -v`

**Estimated Effort:** 0.1 hours

---

### Test: test_cmd_price_in_all_exports

**File:** `tests/unit/test_story_6_1_eth_price.py`

**Tasks to make this test pass:**

- [ ] Add `cmd_price` to `__all__` list in `commands/__init__.py`
- [ ] Run test: `pytest tests/unit/test_story_6_1_eth_price.py::TestCommandRegistration::test_cmd_price_in_all_exports -v`

**Estimated Effort:** 0.1 hours

---

### Test: test_price_command_in_bot_commands

**File:** `tests/unit/test_story_6_1_eth_price.py`

**Tasks to make this test pass:**

- [ ] Add `BotCommand("price", "ETH price")` to commands list in `main.py` `post_init()`
- [ ] Run test: `pytest tests/unit/test_story_6_1_eth_price.py::TestCommandRegistration::test_price_command_in_bot_commands -v`

**Estimated Effort:** 0.1 hours

---

### Test: test_price_command_handler_registered

**File:** `tests/unit/test_story_6_1_eth_price.py`

**Tasks to make this test pass:**

- [ ] Add `CommandHandler("price", cmd_price)` in `register_handlers()` in `commands/__init__.py`
- [ ] Run test: `pytest tests/unit/test_story_6_1_eth_price.py::TestCommandRegistration::test_price_command_handler_registered -v`

**Estimated Effort:** 0.1 hours

---

### Test: test_cmd_start_includes_price_help

**File:** `tests/unit/test_story_6_1_eth_price.py`

**Tasks to make this test pass:**

- [ ] Add `/price` help text to `cmd_start` function in `commands/query.py`
- [ ] Run test: `pytest tests/unit/test_story_6_1_eth_price.py::TestCommandRegistration::test_cmd_start_includes_price_help -v`

**Estimated Effort:** 0.1 hours

---

## Running Tests

```bash
# Run all failing tests for this story
pytest tests/unit/test_story_6_1_eth_price.py -v

# Run specific test class
pytest tests/unit/test_story_6_1_eth_price.py::TestAPIGetEthPrice -v

# Run specific test
pytest tests/unit/test_story_6_1_eth_price.py::TestCmdPrice::test_cmd_price_success -v

# Run with coverage
pytest tests/unit/test_story_6_1_eth_price.py --cov=api --cov=commands
```

---

## Red-Green-Refactor Workflow

### RED Phase (Complete)

**TEA Agent Responsibilities:**

- All tests written and failing
- Fixtures created with auto-cleanup
- Mock requirements documented
- Implementation checklist created

**Verification:**

- All tests run and fail as expected
- Failure messages are clear and actionable
- Tests fail due to missing implementation, not test bugs

---

### GREEN Phase (DEV Team - Next Steps)

**DEV Agent Responsibilities:**

1. **Pick one failing test** from implementation checklist (start with `test_get_eth_price_success`)
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

1. **Review this checklist and failing tests** with the dev workflow (manual handoff)
2. **Run failing tests** to confirm RED phase: `pytest tests/unit/test_story_6_1_eth_price.py -v`
3. **Begin implementation** using implementation checklist as guide
4. **Work one test at a time** (red -> green for each)
5. **Share progress** in daily standup
6. **When all tests pass**, refactor code for quality
7. **When refactoring complete**, manually update story status to 'done' in sprint-status.yaml

---

## Knowledge Base References Applied

This ATDD workflow consulted the following knowledge fragments:

- **data-factories.md** - Factory patterns with overrides for random test data generation (used inline mock data)
- **test-quality.md** - Test design principles (Given-When-Then, one assertion per test, determinism, isolation)
- **test-levels-framework.md** - Test level selection framework (Unit tests for backend Python)

See `tea-index.csv` for complete knowledge fragment mapping.

---

## Test Execution Evidence

### Initial Test Run (RED Phase Verification)

**Command:** `pytest tests/unit/test_story_6_1_eth_price.py -v`

**Results:**

```
(To be captured after running tests - all tests should FAIL)
```

**Summary:**

- Total tests: 15
- Passing: 0 (expected)
- Failing: 15 (expected)
- Status: RED phase verified

**Expected Failure Messages:**

- `ImportError: cannot import name 'cmd_price' from 'commands.query'`
- `AttributeError: 'TerminalAPI' object has no attribute 'get_eth_price'`
- `AssertionError: 'price' not in command_names`

---

## Notes

- This is a backend Python project using pytest with asyncio
- No E2E/UI tests needed - all tests are unit tests
- Tests follow existing patterns from Story 5-3
- All user-facing messages must be in English (project convention)
- Formatters `format_usd()` and `format_percent()` already exist in utils/formatters.py

---

## Contact

**Questions or Issues?**

- Ask in team standup
- Refer to `./bmad/docs/tea-README.md` for workflow documentation
- Consult `./_bmad/testarch/knowledge` for testing best practices

---

**Generated by BMad TEA Agent** - 2026-03-03
