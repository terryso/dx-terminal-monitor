---
stepsCompleted:
  - step-01-preflight-and-context
  - step-02-generation-mode
  - step-03-test-strategy
  - step-04-generate-tests
  - step-05-validate-and-complete
lastStep: step-05-validate-and-complete
lastSaved: '2026-03-04'
workflowType: 'testarch-atdd'
inputDocuments:
  - _bmad-output/implementation-artifacts/8-3-suggestion-push.md
  - advisor.py
  - tests/conftest.py
  - tests/unit/test_story_8_2_ai_advisor.py
---

# ATDD Checklist - Epic 8, Story 8-3: Suggestion Push & Interaction

**Date:** 2026-03-04
**Author:** Nick
**Primary Test Level:** Unit (Backend Python)

---

## Story Summary

This story implements the push notification and interactive button system for AI strategy suggestions. Users receive periodic AI analysis via Telegram with Inline Keyboard buttons to execute or ignore suggestions.

**As a** user
**I want** to receive AI strategy suggestions via push notification with interactive buttons
**So that** I can quickly adjust trading strategies with one click

---

## Acceptance Criteria

1. Implement `format_suggestions_message(suggestions: list, context: dict) -> str` to format suggestion messages
2. Implement `build_suggestion_keyboard(suggestions: list, request_id: str) -> InlineKeyboardMarkup` to build interactive buttons
3. Create `AdvisorMonitor` class or extend existing monitor to periodically push suggestions
4. Generate unique `request_id` (UUID short format) for each batch of suggestions
5. Push message format includes:
   - Analysis time
   - Current status (balance, positions, strategies, PnL)
   - Suggestions with action type, content, priority, validity, reason
   - Inline keyboard with Execute[n], Execute All, Ignore buttons
6. Update button state after click (edit_message_reply_markup)
7. Implement control commands: `/advisor_on`, `/advisor_off`, `/advisor_status`
8. Configuration: `ADVISOR_INTERVAL_HOURS` (default: 2), `SUGGESTION_TTL_MINUTES` (default: 30)
9. Add unit tests

---

## Failing Tests Created (RED Phase)

### Unit Tests (80+ tests)

**File:** `tests/unit/test_story_8_3_suggestion_push.py` (870+ lines)

#### Test Classes:

- **TestFormatSuggestionsMessage** (12 tests) - AC1, AC5
  - `test_format_function_exists` - RED: advisor_monitor module not created
  - `test_format_accepts_suggestions_and_context` - RED: function not implemented
  - `test_format_includes_analysis_time` - RED: missing analysis time in output
  - `test_format_includes_current_status` - RED: missing status section
  - `test_format_add_suggestion` - RED: add suggestion formatting
  - `test_format_disable_suggestion` - RED: disable suggestion formatting
  - `test_format_multiple_suggestions` - RED: numbered indices
  - `test_format_uses_html_for_formatting` - RED: HTML tags

- **TestBuildSuggestionKeyboard** (11 tests) - AC2, AC4
  - `test_build_keyboard_function_exists` - RED: function not implemented
  - `test_build_keyboard_returns_inline_keyboard_markup` - RED: wrong return type
  - `test_build_keyboard_creates_individual_execute_buttons` - RED: missing buttons
  - `test_build_keyboard_creates_execute_all_button` - RED: missing button
  - `test_build_keyboard_creates_ignore_button` - RED: missing button
  - `test_build_keyboard_callback_data_format` - RED: wrong callback format
  - `test_build_keyboard_single_suggestion_callback` - RED: callback data format
  - `test_build_keyboard_execute_all_callback` - RED: callback data format
  - `test_build_keyboard_ignore_callback` - RED: callback data format

- **TestAdvisorMonitorClass** (13 tests) - AC3
  - `test_advisor_monitor_class_exists` - RED: class not created
  - `test_advisor_monitor_accepts_advisor_and_api` - RED: constructor parameters
  - `test_advisor_monitor_accepts_callback` - RED: callback parameter
  - `test_advisor_monitor_accepts_admin_chat_id` - RED: chat_id parameter
  - `test_advisor_monitor_has_interval_hours_config` - RED: interval config
  - `test_advisor_monitor_default_interval_is_2_hours` - RED: default value
  - `test_advisor_monitor_has_start_method` - RED: start method
  - `test_advisor_monitor_has_stop_method` - RED: stop method
  - `test_advisor_monitor_has_start_background_method` - RED: async background start
  - `test_advisor_monitor_has_running_flag` - RED: running flag
  - `test_advisor_monitor_has_last_analysis_tracking` - RED: tracking field

- **TestAdvisorMonitorAsync** (3 tests) - AC3
  - `test_start_is_async` - RED: async method
  - `test_start_background_returns_task` - RED: returns asyncio.Task
  - `test_stop_sets_running_to_false` - RED: stop behavior

- **TestUUIDGeneration** (2 tests) - AC4
  - `test_push_suggestions_generates_short_uuid` - RED: UUID generation
  - `test_push_suggestions_unique_ids` - RED: unique IDs

- **TestPushSuggestions** (10 tests) - AC3, AC5
  - `test_push_suggestions_function_exists` - RED: function not implemented
  - `test_push_suggestions_calls_bot_send_message` - RED: bot integration
  - `test_push_suggestions_includes_reply_markup` - RED: inline keyboard
  - `test_push_suggestions_uses_html_parse_mode` - RED: HTML mode
  - `test_push_suggestions_stores_pending_request` - RED: pending storage

- **TestCallbackQueryHandler** (8 tests) - AC6
  - `test_callback_handler_exists` - RED: handler not implemented
  - `test_callback_handler_parses_callback_data` - RED: data parsing
  - `test_callback_handler_validates_request_exists` - RED: validation
  - `test_callback_handler_validates_request_not_expired` - RED: TTL check
  - `test_callback_handler_checks_admin_permission` - RED: admin check
  - `test_callback_handler_prevents_duplicate_execution` - RED: dedup
  - `test_callback_handler_handles_ignore_choice` - RED: ignore handling
  - `test_callback_handler_handles_all_choice` - RED: execute all

- **TestExecuteSuggestion** (5 tests) - AC6
  - `test_execute_suggestion_exists` - RED: function not implemented
  - `test_execute_add_suggestion_calls_contract` - RED: contract call
  - `test_execute_disable_suggestion_calls_contract` - RED: contract call
  - `test_execute_suggestion_returns_result_string` - RED: result format
  - `test_execute_suggestion_handles_errors` - RED: error handling

- **TestControlCommands** (15 tests) - AC7
  - `test_cmd_advisor_on_exists` - RED: command not implemented
  - `test_cmd_advisor_off_exists` - RED: command not implemented
  - `test_cmd_advisor_status_exists` - RED: command not implemented
  - `test_advisor_on_is_async` - RED: async function
  - `test_advisor_off_is_async` - RED: async function
  - `test_advisor_status_is_async` - RED: async function
  - `test_advisor_on_starts_monitor` - RED: monitor start
  - `test_advisor_off_stops_monitor` - RED: monitor stop
  - `test_advisor_status_reports_status` - RED: status report
  - `test_advisor_on_checks_admin_permission` - RED: admin check
  - `test_advisor_off_checks_admin_permission` - RED: admin check
  - `test_advisor_status_checks_admin_permission` - RED: admin check

- **TestConfiguration** (6 tests) - AC8
  - `test_advisor_enabled_config_exists` - RED: config not added
  - `test_advisor_interval_hours_config_exists` - RED: config not added
  - `test_advisor_interval_hours_default_is_2` - RED: default value
  - `test_suggestion_ttl_minutes_config_exists` - RED: config not added
  - `test_suggestion_ttl_minutes_default_is_30` - RED: default value

- **TestEnvExample** (3 tests) - AC8
  - `test_env_example_includes_advisor_enabled` - RED: not documented
  - `test_env_example_includes_advisor_interval_hours` - RED: not documented
  - `test_env_example_includes_suggestion_ttl_minutes` - RED: not documented

- **TestIntegration** (3 tests) - Full flow
  - `test_full_flow_suggestion_push` - RED: end-to-end
  - `test_monitor_analysis_cycle` - RED: periodic analysis
  - `test_callback_execution_flow` - RED: button execution

---

## Data Factories Created

### SuggestionPushFactory

**File:** `tests/unit/test_story_8_3_suggestion_push.py`

**Exports:**

- `create_suggestion_add(overrides?)` - Create mock add suggestion
- `create_suggestion_disable(overrides?)` - Create mock disable suggestion
- `create_context(overrides?)` - Create mock context dict

**Example Usage:**

```python
factory = SuggestionPushFactory()
suggestion = factory.create_suggestion_add(
    content="When BTC breaks 70000",
    priority=2,
    expiry_hours=24
)
context = factory.create_context(
    balance="1.5 ETH ($4,500)",
    positions=3
)
```

---

## Fixtures Created

### Test Fixtures

**File:** `tests/unit/test_story_8_3_suggestion_push.py`

**Fixtures:**

- `push_factory` - SuggestionPushFactory instance
- `mock_bot` - Mocked Telegram Bot with AsyncMock for send_message, edit_message_reply_markup
- `mock_llm` - Mocked LLMClient
- `mock_api` - Mocked TerminalAPI
- `mock_contract` - Mocked contract with add_strategy, disable_strategy

**Example Usage:**

```python
@pytest.mark.asyncio
async def test_example(mock_bot, push_factory):
    suggestions = [push_factory.create_suggestion_add()]
    context = push_factory.create_context()

    await push_suggestions(123, suggestions, context, mock_bot)

    mock_bot.send_message.assert_called_once()
```

---

## Mock Requirements

### Telegram Bot Mock

**Methods to Mock:**

- `bot.send_message(chat_id, text, reply_markup, parse_mode)` - Send suggestion message
- `bot.edit_message_reply_markup(chat_id, message_id, reply_markup)` - Remove keyboard after action

**Success Response:**

```json
{
  "message_id": 123,
  "chat": { "id": 123456789 }
}
```

### Contract Mock

**Methods to Mock:**

- `contract.add_strategy(prompt, priority, expiry)` - Add strategy
- `contract.disable_strategy(strategy_id)` - Disable strategy

**Success Response:**

```json
{
  "tx_hash": "0xabc123..."
}
```

---

## Implementation Checklist

### Test: test_format_function_exists

**File:** `tests/unit/test_story_8_3_suggestion_push.py`

**Tasks to make this test pass:**

- [ ] Create `advisor_monitor.py` module
- [ ] Import necessary types (list, dict, str)
- [ ] Define `format_suggestions_message(suggestions: list, context: dict) -> str` function
- [ ] Run test: `pytest tests/unit/test_story_8_3_suggestion_push.py::TestFormatSuggestionsMessage::test_format_function_exists -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 0.5 hours

---

### Test: test_format_add_suggestion

**File:** `tests/unit/test_story_8_3_suggestion_push.py`

**Tasks to make this test pass:**

- [ ] Import Suggestion dataclass from advisor.py
- [ ] Format add suggestion with icon "[ADD]"
- [ ] Include content, priority (LOW/MEDIUM/HIGH), expiry_hours, reason
- [ ] Use numbered index [1], [2], etc.
- [ ] Run test: `pytest tests/unit/test_story_8_3_suggestion_push.py::TestFormatSuggestionsMessage::test_format_add_suggestion -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 1 hour

---

### Test: test_build_keyboard_returns_inline_keyboard_markup

**File:** `tests/unit/test_story_8_3_suggestion_push.py`

**Tasks to make this test pass:**

- [ ] Import InlineKeyboardMarkup, InlineKeyboardButton from telegram
- [ ] Define `build_suggestion_keyboard(suggestions, request_id)` function
- [ ] Return InlineKeyboardMarkup instance
- [ ] Run test: `pytest tests/unit/test_story_8_3_suggestion_push.py::TestBuildSuggestionKeyboard::test_build_keyboard_returns_inline_keyboard_markup -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 1 hour

---

### Test: test_build_keyboard_callback_data_format

**File:** `tests/unit/test_story_8_3_suggestion_push.py`

**Tasks to make this test pass:**

- [ ] Set callback_data format: `adv:{request_id}:{choice}`
- [ ] Create individual buttons with choice = 1, 2, 3...
- [ ] Create "Execute All" button with choice = "all"
- [ ] Create "Ignore" button with choice = "ignore"
- [ ] Run test: `pytest tests/unit/test_story_8_3_suggestion_push.py::TestBuildSuggestionKeyboard::test_build_keyboard_callback_data_format -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 1 hour

---

### Test: test_advisor_monitor_class_exists

**File:** `tests/unit/test_story_8_3_suggestion_push.py`

**Tasks to make this test pass:**

- [ ] Define `AdvisorMonitor` class in advisor_monitor.py
- [ ] Accept StrategyAdvisor, TerminalAPI, callback, admin_chat_id in constructor
- [ ] Add interval_hours parameter (default: 2)
- [ ] Calculate interval_seconds from interval_hours
- [ ] Initialize running = False
- [ ] Initialize last_analysis = None
- [ ] Run test: `pytest tests/unit/test_story_8_3_suggestion_push.py::TestAdvisorMonitorClass::test_advisor_monitor_class_exists -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 1 hour

---

### Test: test_start_background_returns_task

**File:** `tests/unit/test_story_8_3_suggestion_push.py`

**Tasks to make this test pass:**

- [ ] Import asyncio
- [ ] Implement `start()` async method with while running loop
- [ ] Implement `start_background()` method returning asyncio.create_task(start())
- [ ] Run test: `pytest tests/unit/test_story_8_3_suggestion_push.py::TestAdvisorMonitorAsync::test_start_background_returns_task -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 2 hours

---

### Test: test_push_suggestions_calls_bot_send_message

**File:** `tests/unit/test_story_8_3_suggestion_push.py`

**Tasks to make this test pass:**

- [ ] Define `push_suggestions(chat_id, suggestions, context, bot)` async function
- [ ] Generate request_id with uuid.uuid4().hex[:8]
- [ ] Store request in pending_requests dict
- [ ] Call format_suggestions_message() and build_suggestion_keyboard()
- [ ] Call bot.send_message() with reply_markup and parse_mode="HTML"
- [ ] Run test: `pytest tests/unit/test_story_8_3_suggestion_push.py::TestPushSuggestions::test_push_suggestions_calls_bot_send_message -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 2 hours

---

### Test: test_callback_handler_parses_callback_data

**File:** `tests/unit/test_story_8_3_suggestion_push.py`

**Tasks to make this test pass:**

- [ ] Define `handle_advisor_callback(update, context)` async function
- [ ] Parse update.callback_query.data to extract request_id and choice
- [ ] Validate request exists in pending_requests
- [ ] Check request not expired (SUGGESTION_TTL)
- [ ] Check admin permission via is_admin()
- [ ] Check not already executed
- [ ] Run test: `pytest tests/unit/test_story_8_3_suggestion_push.py::TestCallbackQueryHandler::test_callback_handler_parses_callback_data -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 3 hours

---

### Test: test_execute_add_suggestion_calls_contract

**File:** `tests/unit/test_story_8_3_suggestion_push.py`

**Tasks to make this test pass:**

- [ ] Define `execute_suggestion(suggestion)` async function
- [ ] Import contract module
- [ ] For "add" action: call contract.add_strategy()
- [ ] For "disable" action: call contract.disable_strategy()
- [ ] Return formatted result string with TX hash
- [ ] Handle errors gracefully
- [ ] Run test: `pytest tests/unit/test_story_8_3_suggestion_push.py::TestExecuteSuggestion::test_execute_add_suggestion_calls_contract -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 2 hours

---

### Test: test_advisor_on_starts_monitor

**File:** `tests/unit/test_story_8_3_suggestion_push.py`

**Tasks to make this test pass:**

- [ ] Create `commands/advisor.py` module
- [ ] Define `cmd_advisor_on(update, context)` async function
- [ ] Check admin permission
- [ ] Call monitor.start_background()
- [ ] Reply with confirmation
- [ ] Define `set_advisor_monitor(monitor)` function for dependency injection
- [ ] Run test: `pytest tests/unit/test_story_8_3_suggestion_push.py::TestControlCommands::test_advisor_on_starts_monitor -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 2 hours

---

### Test: test_suggestion_ttl_minutes_config_exists

**File:** `tests/unit/test_story_8_3_suggestion_push.py`

**Tasks to make this test pass:**

- [ ] Add SUGGESTION_TTL_MINUTES to config.py
- [ ] Set default value to 30
- [ ] Read from environment variable
- [ ] Run test: `pytest tests/unit/test_story_8_3_suggestion_push.py::TestConfiguration::test_suggestion_ttl_minutes_config_exists -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 0.5 hours

---

## Running Tests

```bash
# Run all failing tests for this story
pytest tests/unit/test_story_8_3_suggestion_push.py -v

# Run specific test class
pytest tests/unit/test_story_8_3_suggestion_push.py::TestFormatSuggestionsMessage -v

# Run specific test
pytest tests/unit/test_story_8_3_suggestion_push.py::TestFormatSuggestionsMessage::test_format_function_exists -v

# Run with coverage
pytest tests/unit/test_story_8_3_suggestion_push.py --cov=advisor_monitor --cov-report=term-missing

# Run tests matching pattern
pytest tests/unit/test_story_8_3_suggestion_push.py -k "keyboard" -v
```

---

## Red-Green-Refactor Workflow

### RED Phase (Complete)

**TEA Agent Responsibilities:**

- All tests written and failing
- Test fixtures and factories created
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

1. **Run failing tests** to confirm RED phase: `pytest tests/unit/test_story_8_3_suggestion_push.py -v`
2. **Create advisor_monitor.py** module with format_suggestions_message function
3. **Implement build_suggestion_keyboard** with InlineKeyboardMarkup
4. **Create AdvisorMonitor class** with start/stop/start_background methods
5. **Implement push_suggestions** function with UUID generation and bot integration
6. **Implement handle_advisor_callback** for button handling
7. **Implement execute_suggestion** for contract calls
8. **Create commands/advisor.py** with control commands
9. **Add configuration** to config.py and .env.example
10. **Register handlers** in main.py post_init()
11. **Run all tests** until GREEN phase complete
12. **Refactor** for code quality

---

## Knowledge Base References Applied

This ATDD workflow consulted the following knowledge fragments:

- **test-quality.md** - Test design principles (Given-When-Then, one assertion per test, determinism, isolation)
- **test-levels-framework.md** - Test level selection framework (Unit vs Integration)
- **data-factories.md** - Factory patterns for test data generation
- **component-tdd.md** - TDD red-green-refactor cycle

---

## Test Execution Evidence

### Initial Test Run (RED Phase Verification)

**Command:** `pytest tests/unit/test_story_8_3_suggestion_push.py -v`

**Expected Results:**

```
tests/unit/test_story_8_3_suggestion_push.py::TestFormatSuggestionsMessage::test_format_function_exists FAILED
tests/unit/test_story_8_3_suggestion_push.py::TestFormatSuggestionsMessage::test_format_accepts_suggestions_and_context FAILED
... (80+ FAILED tests)
```

**Summary:**

- Total tests: 80+
- Passing: 0 (expected)
- Failing: 80+ (expected)
- Status: RED phase verified

**Expected Failure Messages:**

- `ModuleNotFoundError: No module named 'advisor_monitor'`
- `ImportError: cannot import name 'format_suggestions_message' from 'advisor_monitor'`
- `AttributeError: module 'advisor_monitor' has no attribute 'AdvisorMonitor'`

---

## Notes

- Tests follow existing pytest patterns from test_story_8_2_ai_advisor.py
- Uses Suggestion dataclass from advisor.py (already implemented in Story 8-2)
- Tests mock Telegram Bot for isolation
- Tests check admin permission using ADMIN_USERS from config
- Configuration tests verify both config.py and .env.example

---

**Generated by BMad TEA Agent** - 2026-03-04
