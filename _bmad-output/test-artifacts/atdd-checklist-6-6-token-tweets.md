---
stepsCompleted:
  - step-01-preflight-and-context
  - step-02-generation-mode
  - step-03-test-strategy
  - step-04-generate-tests
  - step-04c-aggregate
lastStep: step-04c-aggregate
lastSaved: '2026-03-03'
workflowType: testarch-atdd
inputDocuments:
  - _bmad-output/implementation-artifacts/6-6-token-tweets.md
  - tests/unit/test_story_6_5_leaderboard.py
  - _bmad/tea/testarch/knowledge/data-factories.md
  - _bmad/tea/testarch/knowledge/test-quality.md
  - _bmad/tea/testarch/knowledge/test-healing-patterns.md
  - _bmad/tea/testarch/knowledge/test-levels-framework.md
---

# ATDD Checklist - Epic 6, Story 6: Token Tweets Query

**Date:** 2026-03-03
**Author:** Nick
**Primary Test Level:** Unit (Python backend)

---

## Story Summary

As a user, I want to check token-related tweets via the `/tweets <symbol>` command, so that I can understand market sentiment and latest updates for specific tokens.

**As a** Telegram bot user
**I want** to query token-related tweets with `/tweets <symbol> [limit]`
**So that** I can see recent tweets about a token including content, author, timestamp, and link

---

## Acceptance Criteria

1. Add `get_token_tweets(symbol, limit)` method to `api.py` that calls `/tweets/{tokenSymbol}` endpoint
2. Add `cmd_tweets` command handler in `commands/query.py`
3. Command format: `/tweets <symbol> [limit]` - symbol required, optional limit parameter (default 5)
4. Format output: tweet content, author, time, link
5. Handle missing symbol with usage hint
6. Handle empty results with appropriate message
7. Register `/tweets` command in Bot command menu
8. Add unit tests for the new command

---

## Failing Tests Created (RED Phase)

### Unit Tests (17 tests)

**File:** `tests/unit/test_story_6_6_token_tweets.py` (estimated ~380 lines)

#### Test Class: TestGetTokenTweets (API Method Tests) - AC1

- **Test:** `test_get_token_tweets_success`
  - **Status:** RED - Method `get_token_tweets` does not exist on TerminalAPI class
  - **Verifies:** AC1 - API method exists and calls correct endpoint

- **Test:** `test_get_token_tweets_with_custom_limit`
  - **Status:** RED - Method `get_token_tweets` does not accept limit parameter
  - **Verifies:** AC1, AC3 - API method accepts optional limit parameter

- **Test:** `test_get_token_tweets_empty`
  - **Status:** RED - Method `get_token_tweets` does not exist
  - **Verifies:** AC1 - API method handles empty response

- **Test:** `test_get_token_tweets_api_error`
  - **Status:** RED - Method `get_token_tweets` does not exist
  - **Verifies:** AC1 - API method handles error response

#### Test Class: TestCmdTweets (Command Handler Tests) - AC2, AC3, AC4, AC5, AC6

- **Test:** `test_cmd_tweets_success`
  - **Status:** RED - Function `cmd_tweets` does not exist in commands.query
  - **Verifies:** AC2, AC4 - Command handler formats output correctly

- **Test:** `test_cmd_tweets_unauthorized`
  - **Status:** RED - Function `cmd_tweets` does not exist
  - **Verifies:** AC2 - Command handler rejects unauthorized users

- **Test:** `test_cmd_tweets_missing_symbol`
  - **Status:** RED - Function `cmd_tweets` does not exist
  - **Verifies:** AC5 - Command handler shows usage hint for missing symbol

- **Test:** `test_cmd_tweets_empty_results`
  - **Status:** RED - Function `cmd_tweets` does not exist
  - **Verifies:** AC6 - Command handler shows appropriate message for empty results

- **Test:** `test_cmd_tweets_api_error`
  - **Status:** RED - Function `cmd_tweets` does not exist
  - **Verifies:** AC2 - Command handler displays API errors

- **Test:** `test_cmd_tweets_with_limit_arg`
  - **Status:** RED - Function `cmd_tweets` does not exist
  - **Verifies:** AC3 - Command handler parses optional limit argument

- **Test:** `test_cmd_tweets_invalid_limit_arg`
  - **Status:** RED - Function `cmd_tweets` does not exist
  - **Verifies:** AC3 - Command handler uses default for invalid limit argument

- **Test:** `test_cmd_tweets_symbol_case_insensitive`
  - **Status:** RED - Function `cmd_tweets` does not exist
  - **Verifies:** AC3 - Symbol is converted to uppercase

#### Test Class: TestCommandRegistration - AC7

- **Test:** `test_cmd_tweets_exported_from_query`
  - **Status:** RED - Function `cmd_tweets` not exported
  - **Verifies:** AC7 - Function is exported from commands.query

- **Test:** `test_cmd_tweets_in_all_exports`
  - **Status:** RED - `cmd_tweets` not in __all__ list
  - **Verifies:** AC7 - Function is in __all__ exports

- **Test:** `test_tweets_command_in_bot_commands`
  - **Status:** RED - `tweets` not registered in bot menu
  - **Verifies:** AC7 - Command is registered in bot menu

- **Test:** `test_cmd_start_includes_tweets_help`
  - **Status:** RED - `/tweets` not in help text
  - **Verifies:** AC7 - Help text includes new command

#### Test Class: TestOutputFormatting - AC4

- **Test:** `test_output_format_includes_author_and_timestamp`
  - **Status:** RED - Function `cmd_tweets` does not exist
  - **Verifies:** AC4 - Output includes author and timestamp

- **Test:** `test_output_format_includes_content_and_link`
  - **Status:** RED - Function `cmd_tweets` does not exist
  - **Verifies:** AC4 - Output includes tweet content and link

---

## Data Factories Created

### Tweet Entry Factory

**File:** `tests/support/factories/tweet.factory.py` (embedded in test file)

**Exports:**

- `create_tweet_entry(overrides?)` - Create single entry with optional overrides
- `create_tweet_entries(count)` - Create array of entries

**Example Usage:**

```python
entry = create_tweet_entry({"author": "VitalikButerin"})
entries = create_tweet_entries(5)  # Generate 5 entries
```

---

## Fixtures Created

### Test Fixtures (in test file)

**Fixtures:**

- `mock_update` - Mock Telegram Update object with AsyncMock message
- `mock_context` - Mock Telegram Context object with args support
- `mock_tweets_response` - Sample tweets API response with 3 entries
- `mock_empty_tweets_response` - Empty list for edge case testing
- `mock_api_error_response` - Error dict for error handling tests

---

## Mock Requirements

### TerminalAPI Mock

**Method:** `get_token_tweets(symbol: str, limit: int = 5)`

**Success Response:**

```python
[
    {
        "author": "VitalikButerin",
        "content": "Excited about the new ETH upgrade...",
        "timestamp": "2026-03-01",
        "link": "https://x.com/VitalikButerin/status/123456"
    },
    {
        "author": "ethereum",
        "content": "The merge is complete!",
        "timestamp": "2026-03-01",
        "link": "https://x.com/ethereum/status/789012"
    }
]
```

**Failure Response:**

```python
{"error": "HTTP 500 - Internal Server Error"}
```

**Notes:** API calls should be mocked using `patch.object(api, "_get", new_callable=AsyncMock)`

---

## Required data-testid Attributes

N/A - This is a Python backend Telegram bot, not a frontend application.

---

## Implementation Checklist

### Test: test_get_token_tweets_success

**File:** `tests/unit/test_story_6_6_token_tweets.py`

**Tasks to make this test pass:**

- [ ] Add `get_token_tweets(symbol: str, limit: int = 5)` method to `api.py` TerminalAPI class
- [ ] Method should call `await self._get(f"/tweets/{symbol}", {"limit": limit})`
- [ ] Run test: `pytest tests/unit/test_story_6_6_token_tweets.py::TestGetTokenTweets::test_get_token_tweets_success -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 0.25 hours

---

### Test: test_get_token_tweets_with_custom_limit

**File:** `tests/unit/test_story_6_6_token_tweets.py`

**Tasks to make this test pass:**

- [ ] Ensure `get_token_tweets` method accepts `limit` parameter
- [ ] Pass limit as query parameter to `_get()` call
- [ ] Run test: `pytest tests/unit/test_story_6_6_token_tweets.py::TestGetTokenTweets::test_get_token_tweets_with_custom_limit -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 0.1 hours

---

### Test: test_cmd_tweets_success

**File:** `tests/unit/test_story_6_6_token_tweets.py`

**Tasks to make this test pass:**

- [ ] Add `cmd_tweets` async function in `commands/query.py`
- [ ] Add permission check: `if not authorized(update): return`
- [ ] Parse required symbol argument from `ctx.args[0]`
- [ ] Parse optional limit argument from `ctx.args[1]` if present
- [ ] Call `api.get_token_tweets(symbol, limit)` using lazy import pattern
- [ ] Format output with tweet content, author, timestamp, link
- [ ] Run test: `pytest tests/unit/test_story_6_6_token_tweets.py::TestCmdTweets::test_cmd_tweets_success -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 0.5 hours

---

### Test: test_cmd_tweets_missing_symbol

**File:** `tests/unit/test_story_6_6_token_tweets.py`

**Tasks to make this test pass:**

- [ ] Check if `ctx.args` is empty
- [ ] Return usage hint: "Usage: /tweets <symbol> [limit]"
- [ ] Run test: `pytest tests/unit/test_story_6_6_token_tweets.py::TestCmdTweets::test_cmd_tweets_missing_symbol -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 0.1 hours

---

### Test: test_cmd_tweets_empty_results

**File:** `tests/unit/test_story_6_6_token_tweets.py`

**Tasks to make this test pass:**

- [ ] Handle empty data list with "No tweets found for {symbol}" message
- [ ] Run test: `pytest tests/unit/test_story_6_6_token_tweets.py::TestCmdTweets::test_cmd_tweets_empty_results -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 0.1 hours

---

### Test: test_cmd_tweets_with_limit_arg

**File:** `tests/unit/test_story_6_6_token_tweets.py`

**Tasks to make this test pass:**

- [ ] Parse `ctx.args[1]` as integer limit if present
- [ ] Pass parsed limit to API call
- [ ] Run test: `pytest tests/unit/test_story_6_6_token_tweets.py::TestCmdTweets::test_cmd_tweets_with_limit_arg -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 0.1 hours

---

### Test: test_tweets_command_in_bot_commands

**File:** `tests/unit/test_story_6_6_token_tweets.py`

**Tasks to make this test pass:**

- [ ] Add `BotCommand("tweets", "Token-related tweets")` to `post_init()` in `main.py`
- [ ] Run test: `pytest tests/unit/test_story_6_6_token_tweets.py::TestCommandRegistration::test_tweets_command_in_bot_commands -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 0.1 hours

---

### Test: test_cmd_tweets_exported_from_query

**File:** `tests/unit/test_story_6_6_token_tweets.py`

**Tasks to make this test pass:**

- [ ] Add import in `commands/__init__.py`: `from .query import cmd_tweets`
- [ ] Add to `__all__` list: `'cmd_tweets'`
- [ ] Add handler registration: `CommandHandler("tweets", cmd_tweets)`
- [ ] Run test: `pytest tests/unit/test_story_6_6_token_tweets.py::TestCommandRegistration::test_cmd_tweets_exported_from_query -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 0.1 hours

---

### Test: test_cmd_start_includes_tweets_help

**File:** `tests/unit/test_story_6_6_token_tweets.py`

**Tasks to make this test pass:**

- [ ] Update `cmd_start` help text in `commands/query.py`
- [ ] Add line: `/tweets <symbol> [limit] - Token-related tweets`
- [ ] Run test: `pytest tests/unit/test_story_6_6_token_tweets.py::TestCommandRegistration::test_cmd_start_includes_tweets_help -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 0.1 hours

---

## Running Tests

```bash
# Run all failing tests for this story
pytest tests/unit/test_story_6_6_token_tweets.py -v

# Run specific test class
pytest tests/unit/test_story_6_6_token_tweets.py::TestGetTokenTweets -v
pytest tests/unit/test_story_6_6_token_tweets.py::TestCmdTweets -v
pytest tests/unit/test_story_6_6_token_tweets.py::TestCommandRegistration -v

# Run specific test
pytest tests/unit/test_story_6_6_token_tweets.py::TestGetTokenTweets::test_get_token_tweets_success -v

# Run with coverage
pytest tests/unit/test_story_6_6_token_tweets.py --cov=api --cov=commands -v

# Run all tests and show failures
pytest tests/unit/test_story_6_6_token_tweets.py -v --tb=short
```

---

## Red-Green-Refactor Workflow

### RED Phase (Complete)

**TEA Agent Responsibilities:**

- All tests written and failing
- Fixtures created with mock data
- Mock requirements documented
- Implementation checklist created

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
3. **Run failing tests** to confirm RED phase: `pytest tests/unit/test_story_6_6_token_tweets.py -v`
4. **Begin implementation** using implementation checklist as guide
5. **Work one test at a time** (red -> green for each)
6. **Share progress** in daily standup
7. **When all tests pass**, refactor code for quality
8. **When refactoring complete**, manually update story status to 'done' in sprint-status.yaml

---

## Knowledge Base References Applied

This ATDD workflow consulted the following knowledge fragments:

- **data-factories.md** - Factory patterns for test data generation with overrides support
- **test-quality.md** - Test design principles (Given-When-Then, one assertion per test, determinism, isolation)
- **test-healing-patterns.md** - Common failure patterns and automated fixes
- **test-levels-framework.md** - Test level selection framework (Unit for backend)

See `tea-index.csv` for complete knowledge fragment mapping.

---

## Test Execution Evidence

### Initial Test Run (RED Phase Verification)

**Command:** `pytest tests/unit/test_story_6_6_token_tweets.py -v --tb=short`

**Expected Results:**

```
============================= test session starts ==============================
platform darwin -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: /Users/nick/projects/dx-terminal-monitor
plugins: anyio-4.12.1, asyncio-1.3.0
collected 17 items

TestGetTokenTweets::test_get_token_tweets_success FAILED [  5%]
TestGetTokenTweets::test_get_token_tweets_with_custom_limit FAILED [ 11%]
TestGetTokenTweets::test_get_token_tweets_empty FAILED [ 17%]
TestGetTokenTweets::test_get_token_tweets_api_error FAILED [ 23%]
TestCmdTweets::test_cmd_tweets_success FAILED [ 29%]
TestCmdTweets::test_cmd_tweets_unauthorized FAILED [ 35%]
TestCmdTweets::test_cmd_tweets_missing_symbol FAILED [ 41%]
TestCmdTweets::test_cmd_tweets_empty_results FAILED [ 47%]
TestCmdTweets::test_cmd_tweets_api_error FAILED [ 52%]
TestCmdTweets::test_cmd_tweets_with_limit_arg FAILED [ 58%]
TestCmdTweets::test_cmd_tweets_invalid_limit_arg FAILED [ 64%]
TestCmdTweets::test_cmd_tweets_symbol_case_insensitive FAILED [ 70%]
TestCommandRegistration::test_cmd_tweets_exported_from_query FAILED [ 76%]
TestCommandRegistration::test_cmd_tweets_in_all_exports FAILED [ 82%]
TestCommandRegistration::test_tweets_command_in_bot_commands FAILED [ 88%]
TestCommandRegistration::test_cmd_start_includes_tweets_help FAILED [ 94%]
TestOutputFormatting::test_output_format_includes_author_and_timestamp FAILED [100%]
TestOutputFormatting::test_output_format_includes_content_and_link FAILED [100%]

=================================== FAILURES ===================================
TestGetTokenTweets::test_get_token_tweets_success
E   AttributeError: 'TerminalAPI' object has no attribute 'get_token_tweets'

TestCmdTweets::test_cmd_tweets_success
E   ImportError: cannot import name 'cmd_tweets' from 'commands.query'

TestCommandRegistration::test_cmd_tweets_in_all_exports
E   AssertionError: assert 'cmd_tweets' in ['register_handlers', 'cmd_start', ...]

TestCommandRegistration::test_tweets_command_in_bot_commands
E   AssertionError: assert 'tweets' in ['start', 'balance', 'pnl', ...]

TestCommandRegistration::test_cmd_start_includes_tweets_help
E   AssertionError: assert '/tweets' in help text

============================== 17 failed in 0.23s ==============================
```

**Summary:**

- Total tests: 17
- Passing: 0 (expected)
- Failing: 17 (expected)
- Status: RED phase verified

**Expected Failure Messages:**

1. `AttributeError: 'TerminalAPI' object has no attribute 'get_token_tweets'` - API method not implemented
2. `ImportError: cannot import name 'cmd_tweets' from 'commands.query'` - Command handler not implemented
3. `AssertionError: assert 'cmd_tweets' in commands.__all__` - Not exported from module
4. `AssertionError: assert 'tweets' in command_names` - Not registered in bot menu
5. `AssertionError: assert '/tweets' in call_args` - Not in help text

---

## Notes

- This story follows the exact pattern established in Stories 6-1 through 6-5
- The `/tweets/{tokenSymbol}` endpoint returns token-related tweets
- Output format should match the specification from epics.md
- Use lazy import pattern to avoid circular imports: `from main import api` inside function
- Update both `main.py` `post_init()` and `commands/__init__.py` for command registration
- Also update `tests/unit/test_story_1_3_menu_help.py` expected commands list
- Symbol argument is required and should be converted to uppercase
- Limit argument is optional with default of 5

---

## Contact

**Questions or Issues?**

- Ask in team standup
- Refer to `./_bmad/tea/docs/tea-README.md` for workflow documentation
- Consult `./_bmad/tea/testarch/knowledge` for testing best practices

---

**Generated by BMad TEA Agent** - 2026-03-03
