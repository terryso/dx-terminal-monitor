---
stepsCompleted:
  - step-01-preflight-and-context
  - step-02-generation-mode
  - step-03-test-strategy
  - step-04-generate-tests
  - step-05-validate-and-complete
lastStep: step-05-validate-and-complete
lastSaved: '2026-03-03'
workflowType: testarch-atdd
inputDocuments:
  - _bmad-output/implementation-artifacts/6-2-tokens-list.md
  - tests/unit/test_story_6_1_eth_price.py
---

# ATDD Checklist - Epic 6, Story 2: Tokens List Query

**Date:** 2026-03-03
**Author:** Nick
**Primary Test Level:** Unit (backend Python project)

---

## Story Summary

This story adds a `/tokens` command to query the list of tradeable tokens from the Terminal Markets API.

**As a** user
**I want** to query the list of tradeable tokens via `/tokens` command
**So that** I can understand which tokens are available for trading

---

## Acceptance Criteria

1. Add `get_tokens()` method to `api.py`
2. Call `/tokens` endpoint
3. Add `cmd_tokens` command handler to `commands/query.py`
4. Format output: token symbol, name, price, 24h change
5. Support pagination: `/tokens 2`
6. Add unit tests

---

## Failing Tests Created (RED Phase)

### Unit Tests (10 tests)

**File:** `tests/unit/test_story_6_2_tokens_list.py` (approximately 200 lines)

- **Test:** `test_get_tokens_success`
  - **Status:** RED - Method `get_tokens()` does not exist on TerminalAPI class
  - **Verifies:** AC #1, #2 - API method calls `/tokens` endpoint and returns data

- **Test:** `test_get_tokens_with_pagination`
  - **Status:** RED - Method `get_tokens()` does not support pagination parameters
  - **Verifies:** AC #5 - Pagination support via page/limit parameters

- **Test:** `test_cmd_tokens_success`
  - **Status:** RED - Function `cmd_tokens` does not exist
  - **Verifies:** AC #3, #4 - Command handler formats output with symbol, name, price, 24h change

- **Test:** `test_cmd_tokens_unauthorized`
  - **Status:** RED - Function `cmd_tokens` does not exist
  - **Verifies:** Security - Unauthorized users are rejected

- **Test:** `test_cmd_tokens_api_error`
  - **Status:** RED - Function `cmd_tokens` does not exist
  - **Verifies:** Error handling - API errors are displayed to user

- **Test:** `test_cmd_tokens_empty_list`
  - **Status:** RED - Function `cmd_tokens` does not exist
  - **Verifies:** Edge case - Empty token list displays appropriate message

- **Test:** `test_cmd_tokens_pagination`
  - **Status:** RED - Function `cmd_tokens` does not exist
  - **Verifies:** AC #5 - Pagination parameter parsing from command args

- **Test:** `test_cmd_tokens_exported_from_query`
  - **Status:** RED - Function `cmd_tokens` not exported
  - **Verifies:** Module exports

- **Test:** `test_tokens_command_in_bot_commands`
  - **Status:** RED - `tokens` not in bot commands list
  - **Verifies:** Bot menu registration

- **Test:** `test_cmd_start_includes_tokens_help`
  - **Status:** RED - `/tokens` not in help text
  - **Verifies:** Help documentation

---

## Test Strategy

### Test Level Selection (Backend Project)

| Level | Usage | Reason |
|-------|-------|--------|
| Unit | Primary | Pure functions, business logic, edge cases |
| Integration | N/A | Simple API call, covered by unit test with mocks |
| API/Contract | N/A | External API, not owned by this project |
| E2E | N/A | Backend only, no browser testing needed |

### Priority Matrix

| Test | Priority | Risk | Business Impact |
|------|----------|------|-----------------|
| test_cmd_tokens_success | P0 | High | Core functionality |
| test_cmd_tokens_unauthorized | P0 | High | Security |
| test_get_tokens_success | P0 | High | API integration |
| test_cmd_tokens_api_error | P1 | Medium | User experience |
| test_cmd_tokens_pagination | P1 | Medium | Feature completeness |
| test_cmd_tokens_empty_list | P2 | Low | Edge case |
| test_cmd_tokens_exported_from_query | P2 | Low | Code quality |
| test_tokens_command_in_bot_commands | P2 | Low | UX |
| test_cmd_start_includes_tokens_help | P2 | Low | Documentation |

---

## Mock Requirements

### Terminal API Mock

**Endpoint:** `GET /tokens`

**Success Response:**

```json
{
  "items": [
    {
      "symbol": "ETH",
      "name": "Ethereum",
      "priceUsd": "3000.00",
      "change24h": "2.5"
    },
    {
      "symbol": "USDC",
      "name": "USD Coin",
      "priceUsd": "1.00",
      "change24h": "0.1"
    }
  ],
  "total": 50,
  "page": 1,
  "limit": 10
}
```

**Failure Response:**

```json
{
  "error": "API unavailable"
}
```

**Notes:** Use `AsyncMock` for async API methods

---

## Implementation Checklist

### Test: test_get_tokens_success

**File:** `tests/unit/test_story_6_2_tokens_list.py`

**Tasks to make this test pass:**

- [ ] Add `get_tokens()` async method to `api.py` TerminalAPI class
- [ ] Method should call `self._get("/tokens", {})` with no parameters
- [ ] Return dict response from API
- [ ] Run test: `python -m pytest tests/unit/test_story_6_2_tokens_list.py::TestGetTokens::test_get_tokens_success -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 0.5 hours

---

### Test: test_get_tokens_with_pagination

**File:** `tests/unit/test_story_6_2_tokens_list.py`

**Tasks to make this test pass:**

- [ ] Update `get_tokens()` to accept `page` and `limit` parameters
- [ ] Pass parameters to `_get("/tokens", {"page": page, "limit": limit})`
- [ ] Run test: `python -m pytest tests/unit/test_story_6_2_tokens_list.py::TestGetTokens::test_get_tokens_with_pagination -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 0.25 hours

---

### Test: test_cmd_tokens_success

**File:** `tests/unit/test_story_6_2_tokens_list.py`

**Tasks to make this test pass:**

- [ ] Add `cmd_tokens` async function to `commands/query.py`
- [ ] Check permission using `authorized(update)`
- [ ] Parse optional page argument from `ctx.args`
- [ ] Call `api.get_tokens(page)` via `_get_api()`
- [ ] Handle API error response (check for `"error"` key)
- [ ] Format output with token details (symbol, name, price, 24h change)
- [ ] Use `format_usd()` and `format_percent()` from utils/formatters.py
- [ ] Run test: `python -m pytest tests/unit/test_story_6_2_tokens_list.py::TestCmdTokens::test_cmd_tokens_success -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 1 hour

---

### Test: test_cmd_tokens_unauthorized

**File:** `tests/unit/test_story_6_2_tokens_list.py`

**Tasks to make this test pass:**

- [ ] Ensure `cmd_tokens` calls `authorized(update)` at the start
- [ ] Return early if not authorized (no reply_text call)
- [ ] Run test: `python -m pytest tests/unit/test_story_6_2_tokens_list.py::TestCmdTokens::test_cmd_tokens_unauthorized -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 0.25 hours (covered by above)

---

### Test: test_cmd_tokens_api_error

**File:** `tests/unit/test_story_6_2_tokens_list.py`

**Tasks to make this test pass:**

- [ ] Add error handling for `{"error": ...}` in response
- [ ] Reply with error message to user
- [ ] Run test: `python -m pytest tests/unit/test_story_6_2_tokens_list.py::TestCmdTokens::test_cmd_tokens_api_error -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 0.25 hours (covered by above)

---

### Test: test_cmd_tokens_empty_list

**File:** `tests/unit/test_story_6_2_tokens_list.py`

**Tasks to make this test pass:**

- [ ] Handle case where `items` list is empty
- [ ] Reply with "No tokens available" message
- [ ] Run test: `python -m pytest tests/unit/test_story_6_2_tokens_list.py::TestCmdTokens::test_cmd_tokens_empty_list -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 0.25 hours (covered by above)

---

### Test: test_cmd_tokens_pagination

**File:** `tests/unit/test_story_6_2_tokens_list.py`

**Tasks to make this test pass:**

- [ ] Parse page number from `ctx.args[0]` if present
- [ ] Default to page 1 if no argument
- [ ] Calculate display range (start_num, end_num) for output header
- [ ] Run test: `python -m pytest tests/unit/test_story_6_2_tokens_list.py::TestCmdTokens::test_cmd_tokens_pagination -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 0.5 hours (covered by above)

---

### Test: test_cmd_tokens_exported_from_query

**File:** `tests/unit/test_story_6_2_tokens_list.py`

**Tasks to make this test pass:**

- [ ] Add `cmd_tokens` to `commands/__init__.py` `__all__` list
- [ ] Add `CommandHandler("tokens", cmd_tokens)` in `register_handlers()`
- [ ] Run test: `python -m pytest tests/unit/test_story_6_2_tokens_list.py::TestCommandRegistration::test_cmd_tokens_exported_from_query -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 0.25 hours

---

### Test: test_tokens_command_in_bot_commands

**File:** `tests/unit/test_story_6_2_tokens_list.py`

**Tasks to make this test pass:**

- [ ] Add `BotCommand("tokens", "Tradeable tokens")` to bot commands in `main.py` `post_init()`
- [ ] Run test: `python -m pytest tests/unit/test_story_6_2_tokens_list.py::TestCommandRegistration::test_tokens_command_in_bot_commands -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 0.25 hours

---

### Test: test_cmd_start_includes_tokens_help

**File:** `tests/unit/test_story_6_2_tokens_list.py`

**Tasks to make this test pass:**

- [ ] Add `/tokens` help text in `cmd_start` function in `commands/query.py`
- [ ] Format: `/tokens - Query tradeable tokens list`
- [ ] Run test: `python -m pytest tests/unit/test_story_6_2_tokens_list.py::TestCommandRegistration::test_cmd_start_includes_tokens_help -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 0.25 hours

---

## Running Tests

```bash
# Run all failing tests for this story
python -m pytest tests/unit/test_story_6_2_tokens_list.py -v

# Run specific test class
python -m pytest tests/unit/test_story_6_2_tokens_list.py::TestCmdTokens -v
python -m pytest tests/unit/test_story_6_2_tokens_list.py::TestGetTokens -v
python -m pytest tests/unit/test_story_6_2_tokens_list.py::TestCommandRegistration -v

# Run with coverage
python -m pytest tests/unit/test_story_6_2_tokens_list.py --cov=api --cov=commands -v
```

---

## Red-Green-Refactor Workflow

### RED Phase (Complete)

**TEA Agent Responsibilities:**

- [x] All tests written and failing
- [x] Mock requirements documented
- [x] Implementation checklist created

**Verification:**

All tests run and fail as expected (ImportError or AttributeError for missing functions).

---

### GREEN Phase (DEV Team - Next Steps)

**DEV Agent Responsibilities:**

1. Pick one failing test from implementation checklist (start with P0 priority)
2. Read the test to understand expected behavior
3. Implement minimal code to make that specific test pass
4. Run the test to verify it now passes (green)
5. Check off the task in implementation checklist
6. Move to next test and repeat

**Recommended Order:**

1. `test_get_tokens_success` (P0)
2. `test_get_tokens_with_pagination` (P0)
3. `test_cmd_tokens_success` (P0)
4. `test_cmd_tokens_unauthorized` (P0)
5. Remaining tests in priority order

---

### REFACTOR Phase (DEV Team - After All Tests Pass)

1. Verify all tests pass
2. Review code for quality
3. Extract duplications (DRY principle)
4. Ensure tests still pass after each refactor

---

## Notes

- **Language:** All user-facing messages must be in English (project convention)
- **Test Pattern:** Follow Given-When-Then structure with `AsyncMock` and `MagicMock`
- **Formatters:** Use existing `format_usd()` and `format_percent()` from `utils/formatters.py`
- **Reference:** See `tests/unit/test_story_6_1_eth_price.py` for similar test patterns

---

**Generated by BMad TEA Agent** - 2026-03-03

---

## Test Execution Evidence

### Initial Test Run (RED Phase Verification)

**Command:** `python -m pytest tests/unit/test_story_6_2_tokens_list.py -v`

**Results:**

```
============================= test session starts ==============================
platform darwin -- Python 3.12.10, pytest-9.0.2
collected 11 items

tests/unit/test_story_6_2_tokens_list.py::TestGetTokens::test_get_tokens_success FAILED
tests/unit/test_story_6_2_tokens_list.py::TestGetTokens::test_get_tokens_with_pagination FAILED
tests/unit/test_story_6_2_tokens_list.py::TestCmdTokens::test_cmd_tokens_success FAILED
tests/unit/test_story_6_2_tokens_list.py::TestCmdTokens::test_cmd_tokens_unauthorized FAILED
tests/unit/test_story_6_2_tokens_list.py::TestCmdTokens::test_cmd_tokens_api_error FAILED
tests/unit/test_story_6_2_tokens_list.py::TestCmdTokens::test_cmd_tokens_empty_list FAILED
tests/unit/test_story_6_2_tokens_list.py::TestCmdTokens::test_cmd_tokens_pagination FAILED
tests/unit/test_story_6_2_tokens_list.py::TestCommandRegistration::test_cmd_tokens_exported_from_query FAILED
tests/unit/test_story_6_2_tokens_list.py::TestCommandRegistration::test_cmd_tokens_in_all_exports FAILED
tests/unit/test_story_6_2_tokens_list.py::TestCommandRegistration::test_tokens_command_in_bot_commands FAILED
tests/unit/test_story_6_2_tokens_list.py::TestCommandRegistration::test_cmd_start_includes_tokens_help FAILED

============================== 11 failed in 0.53s ===============================
```

**Summary:**

- Total tests: 11
- Passing: 0 (expected)
- Failing: 11 (expected)
- Status: RED phase verified

**Expected Failure Messages:**

1. `AttributeError: 'TerminalAPI' object has no attribute 'get_tokens'`
2. `ImportError: cannot import name 'cmd_tokens' from 'commands.query'`
3. `AssertionError: assert 'cmd_tokens' in [...]`
4. `AssertionError: assert 'tokens' in [...]`
5. `AssertionError: assert '/tokens' in [...]`
