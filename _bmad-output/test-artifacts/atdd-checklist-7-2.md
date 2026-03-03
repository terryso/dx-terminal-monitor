---
stepsCompleted:
  - step-01-preflight-and-context
  - step-02-generation-mode
  - step-03-test-strategy
  - step-04-generate-tests
  - step-04c-aggregate
  - step-05-validate-and-complete
lastStep: 'step-05-validate-and-complete'
lastSaved: '2026-03-03'
workflowType: 'testarch-atdd'
inputDocuments:
  - '_bmad-output/implementation-artifacts/7-2-threshold-alert.md'
  - 'tests/conftest.py'
  - 'tests/unit/test_story_7_1_daily_report.py'
---

# ATDD Checklist - Epic 7, Story 7-2: Threshold Alert

**Date:** 2026-03-03
**Author:** Nick
**Primary Test Level:** Unit

---

## Story Summary

This story implements threshold-based alerts for PnL and position changes. Users will receive Telegram notifications when their portfolio PnL or individual position values change by more than a configured percentage threshold.

**As a** user
**I want** to receive alerts when PnL or position changes exceed a configured threshold
**So that** I can promptly respond to significant market movements

---

## Acceptance Criteria

1. **AC1:** Extend `ActivityMonitor` to support threshold checking
2. **AC2:** Configuration: `PNL_ALERT_THRESHOLD` (default 5%)
3. **AC3:** Configuration: `POSITION_ALERT_THRESHOLD` (default 10%)
4. **AC4:** Trigger alert when threshold exceeded: change type, change amount, current value
5. **AC5:** Support dynamic configuration via commands: `/alert_pnl <percent>`, `/alert_position <percent>`
6. **AC6:** Add unit tests

---

## Failing Tests Created (RED Phase)

### Unit Tests (51 tests)

**File:** `tests/unit/test_story_7_2_threshold_alert.py` (520 lines)

#### TestThresholdAlerterInit (12 tests) - AC1, AC2, AC3

- **Test:** `test_init_stores_api_instance`
  - **Status:** RED - Module alerter.py does not exist
  - **Verifies:** AC1 - ThresholdAlerter accepts TerminalAPI instance

- **Test:** `test_init_stores_notifier_instance`
  - **Status:** RED - Module alerter.py does not exist
  - **Verifies:** AC1 - ThresholdAlerter accepts TelegramNotifier instance

- **Test:** `test_init_default_pnl_threshold_5`
  - **Status:** RED - Module alerter.py does not exist
  - **Verifies:** AC2 - Default PnL threshold is 5%

- **Test:** `test_init_reads_pnl_threshold_from_env`
  - **Status:** RED - Module alerter.py does not exist
  - **Verifies:** AC2 - PNL_ALERT_THRESHOLD reads from environment

- **Test:** `test_init_default_position_threshold_10`
  - **Status:** RED - Module alerter.py does not exist
  - **Verifies:** AC3 - Default position threshold is 10%

- **Test:** `test_init_reads_position_threshold_from_env`
  - **Status:** RED - Module alerter.py does not exist
  - **Verifies:** AC3 - POSITION_ALERT_THRESHOLD reads from environment

- **Test:** `test_init_running_flag_false`
  - **Status:** RED - Module alerter.py does not exist
  - **Verifies:** AC1 - running flag initialized to False

- **Test:** `test_init_enabled_default_true`
  - **Status:** RED - Module alerter.py does not exist
  - **Verifies:** ALERT_ENABLED defaults to true

- **Test:** `test_init_enabled_from_env`
  - **Status:** RED - Module alerter.py does not exist
  - **Verifies:** ALERT_ENABLED reads from environment

- **Test:** `test_init_check_interval_default_60`
  - **Status:** RED - Module alerter.py does not exist
  - **Verifies:** Default check interval is 60 seconds

- **Test:** `test_init_reads_check_interval_from_env`
  - **Status:** RED - Module alerter.py does not exist
  - **Verifies:** ALERT_CHECK_INTERVAL reads from environment

- **Test:** `test_init_previous_pnl_none`
  - **Status:** RED - Module alerter.py does not exist
  - **Verifies:** AC1 - Previous PnL initialized to None

#### TestPnLThresholdChecking (7 tests) - AC4

- **Test:** `test_check_pnl_no_alert_on_first_check`
  - **Status:** RED - Method _check_pnl_threshold does not exist
  - **Verifies:** AC4 - First check returns None (no comparison possible)

- **Test:** `test_check_pnl_no_alert_below_threshold`
  - **Status:** RED - Method _check_pnl_threshold does not exist
  - **Verifies:** AC4 - No alert when change below threshold

- **Test:** `test_check_pnl_alert_when_threshold_exceeded`
  - **Status:** RED - Method _check_pnl_threshold does not exist
  - **Verifies:** AC4 - Alert data returned when threshold exceeded

- **Test:** `test_check_pnl_handles_negative_change`
  - **Status:** RED - Method _check_pnl_threshold does not exist
  - **Verifies:** AC4 - Detects negative PnL changes

- **Test:** `test_check_pnl_handles_zero_previous`
  - **Status:** RED - Method _check_pnl_threshold does not exist
  - **Verifies:** AC4 - Handles edge case of zero previous PnL

- **Test:** `test_check_pnl_handles_api_error`
  - **Status:** RED - Method _check_pnl_threshold does not exist
  - **Verifies:** AC4 - Graceful API error handling

#### TestPositionThresholdChecking (7 tests) - AC4

- **Test:** `test_check_position_no_alert_on_first_check`
  - **Status:** RED - Method _check_position_threshold does not exist
  - **Verifies:** AC4 - First check returns empty list

- **Test:** `test_check_position_no_alert_below_threshold`
  - **Status:** RED - Method _check_position_threshold does not exist
  - **Verifies:** AC4 - No alert when change below threshold

- **Test:** `test_check_position_alert_when_threshold_exceeded`
  - **Status:** RED - Method _check_position_threshold does not exist
  - **Verifies:** AC4 - Alert data returned when threshold exceeded

- **Test:** `test_check_position_multiple_positions`
  - **Status:** RED - Method _check_position_threshold does not exist
  - **Verifies:** AC4 - Detects multiple position changes

- **Test:** `test_check_position_handles_new_positions`
  - **Status:** RED - Method _check_position_threshold does not exist
  - **Verifies:** AC4 - Handles new positions not in previous data

- **Test:** `test_check_position_handles_api_error`
  - **Status:** RED - Method _check_position_threshold does not exist
  - **Verifies:** AC4 - Graceful API error handling

#### TestAlertFormatting (9 tests) - AC4

- **Test:** `test_format_pnl_alert_includes_change_type`
  - **Status:** RED - Method _format_pnl_alert does not exist
  - **Verifies:** AC4 - PnL alert includes change type

- **Test:** `test_format_pnl_alert_includes_change_amount`
  - **Status:** RED - Method _format_pnl_alert does not exist
  - **Verifies:** AC4 - PnL alert includes change amount

- **Test:** `test_format_pnl_alert_includes_current_value`
  - **Status:** RED - Method _format_pnl_alert does not exist
  - **Verifies:** AC4 - PnL alert includes current value

- **Test:** `test_format_pnl_alert_includes_threshold`
  - **Status:** RED - Method _format_pnl_alert does not exist
  - **Verifies:** AC4 - PnL alert includes threshold percentage

- **Test:** `test_format_position_alert_includes_symbol`
  - **Status:** RED - Method _format_position_alert does not exist
  - **Verifies:** AC4 - Position alert includes token symbol

- **Test:** `test_format_position_alert_includes_change_amount`
  - **Status:** RED - Method _format_position_alert does not exist
  - **Verifies:** AC4 - Position alert includes change amount

- **Test:** `test_format_position_alert_includes_current_value`
  - **Status:** RED - Method _format_position_alert does not exist
  - **Verifies:** AC4 - Position alert includes current value

#### TestAlertCommands (8 tests) - AC5

- **Test:** `test_cmd_alert_pnl_shows_current_threshold`
  - **Status:** RED - Command cmd_alert_pnl does not exist
  - **Verifies:** AC5 - /alert_pnl shows current threshold

- **Test:** `test_cmd_alert_pnl_sets_threshold`
  - **Status:** RED - Command cmd_alert_pnl does not exist
  - **Verifies:** AC5 - /alert_pnl <percent> updates threshold

- **Test:** `test_cmd_alert_pnl_rejects_invalid_value`
  - **Status:** RED - Command cmd_alert_pnl does not exist
  - **Verifies:** AC5 - Invalid values rejected (1-100 range)

- **Test:** `test_cmd_alert_position_shows_current_threshold`
  - **Status:** RED - Command cmd_alert_position does not exist
  - **Verifies:** AC5 - /alert_position shows current threshold

- **Test:** `test_cmd_alert_position_sets_threshold`
  - **Status:** RED - Command cmd_alert_position does not exist
  - **Verifies:** AC5 - /alert_position <percent> updates threshold

- **Test:** `test_cmd_alert_status_shows_all_settings`
  - **Status:** RED - Command cmd_alert_status does not exist
  - **Verifies:** AC5 - /alert_status shows all settings

#### TestSetThresholdMethods (2 tests) - AC5

- **Test:** `test_set_pnl_threshold_updates_value`
  - **Status:** RED - Method set_pnl_threshold does not exist
  - **Verifies:** AC5 - Dynamic PnL threshold update

- **Test:** `test_set_position_threshold_updates_value`
  - **Status:** RED - Method set_position_threshold does not exist
  - **Verifies:** AC5 - Dynamic position threshold update

#### TestStartStop (4 tests)

- **Test:** `test_start_sets_running_true`
  - **Status:** RED - Method start does not exist
  - **Verifies:** Monitoring loop starts correctly

- **Test:** `test_stop_sets_running_false`
  - **Status:** RED - Method stop does not exist
  - **Verifies:** Monitoring loop stops correctly

- **Test:** `test_start_respects_enabled_flag`
  - **Status:** RED - Method start does not exist
  - **Verifies:** Disabled alerter does not start

- **Test:** `test_start_background_creates_task`
  - **Status:** RED - Method start_background does not exist
  - **Verifies:** Background task creation

#### TestSendAlerts (2 tests)

- **Test:** `test_send_alerts_checks_pnl_threshold`
  - **Status:** RED - Method _send_alerts does not exist
  - **Verifies:** PnL threshold checking in alert loop

- **Test:** `test_send_alerts_sends_to_all_notify_users`
  - **Status:** RED - Method _send_alerts does not exist
  - **Verifies:** Alerts sent to all users in notify_users

#### TestEnvironmentConfiguration (5 tests)

- **Test:** `test_reads_pnl_threshold_from_env`
  - **Status:** RED - Module alerter.py does not exist
  - **Verifies:** AC2 - Environment variable reading

- **Test:** `test_reads_position_threshold_from_env`
  - **Status:** RED - Module alerter.py does not exist
  - **Verifies:** AC3 - Environment variable reading

- **Test:** `test_reads_check_interval_from_env`
  - **Status:** RED - Module alerter.py does not exist
  - **Verifies:** ALERT_CHECK_INTERVAL reading

- **Test:** `test_handles_invalid_pnl_threshold`
  - **Status:** RED - Module alerter.py does not exist
  - **Verifies:** AC2 - Graceful handling of invalid env values

- **Test:** `test_handles_invalid_position_threshold`
  - **Status:** RED - Module alerter.py does not exist
  - **Verifies:** AC3 - Graceful handling of invalid env values

---

## Data Factories Created

### AlertDataFactory

**File:** `tests/unit/test_story_7_2_threshold_alert.py` (inline)

**Exports:**

- `create_positions_data(pnl_usd, pnl_percent, **overrides)` - Create positions data for PnL testing
- `create_position_change(symbol, previous_value, current_value)` - Create position change data
- `create_pnl_change(previous_pnl, current_pnl)` - Create PnL change data

**Example Usage:**

```python
# Create positions data with custom PnL
data = AlertDataFactory.create_positions_data(pnl_usd="150.00")

# Create position change for threshold testing
change = AlertDataFactory.create_position_change("ETH", 1000.0, 1200.0)
```

---

## Fixtures Created

### Core Fixtures

**File:** `tests/unit/test_story_7_2_threshold_alert.py` (inline)

**Fixtures:**

- `alert_data_factory` - Provides AlertDataFactory instance
- `mock_api` - Mock TerminalAPI with AsyncMock get_positions
- `mock_notifier` - Mock TelegramNotifier with bot and notify_users

**Uses shared fixtures from `tests/conftest.py`:**
- `mock_telegram_update` - Mock Telegram Update object
- `mock_telegram_context` - Mock Telegram Context object

---

## Implementation Checklist

### Test: TestThresholdAlerterInit tests

**File:** `tests/unit/test_story_7_2_threshold_alert.py`

**Tasks to make these tests pass:**

- [ ] Create `alerter.py` file in project root
- [ ] Import necessary modules (asyncio, logging, os, typing)
- [ ] Define `ThresholdAlerter` class with type annotations
- [ ] Implement `__init__()` with api, notifier parameters
- [ ] Parse `PNL_ALERT_THRESHOLD` env variable (default 5)
- [ ] Parse `POSITION_ALERT_THRESHOLD` env variable (default 10)
- [ ] Parse `ALERT_CHECK_INTERVAL` env variable (default 60)
- [ ] Parse `ALERT_ENABLED` env variable (default true)
- [ ] Initialize `running: bool = False`
- [ ] Initialize `_previous_pnl_usd: float | None = None`
- [ ] Initialize `_previous_positions: dict[str, float] = {}`
- [ ] Run tests: `pytest tests/unit/test_story_7_2_threshold_alert.py::TestThresholdAlerterInit -v`
- [ ] Tests pass (green phase)

**Estimated Effort:** 1 hour

---

### Test: TestPnLThresholdChecking tests

**File:** `tests/unit/test_story_7_2_threshold_alert.py`

**Tasks to make these tests pass:**

- [ ] Implement `_check_pnl_threshold()` async method
- [ ] Fetch current PnL via `self.api.get_positions()`
- [ ] Handle API error responses gracefully
- [ ] Compare with `self._previous_pnl_usd`
- [ ] Calculate percentage change
- [ ] Return alert data dict if threshold exceeded
- [ ] Return None if no alert
- [ ] Update `self._previous_pnl_usd` after check
- [ ] Run tests: `pytest tests/unit/test_story_7_2_threshold_alert.py::TestPnLThresholdChecking -v`
- [ ] Tests pass (green phase)

**Estimated Effort:** 1 hour

---

### Test: TestPositionThresholdChecking tests

**File:** `tests/unit/test_story_7_2_threshold_alert.py`

**Tasks to make these tests pass:**

- [ ] Implement `_check_position_threshold()` async method
- [ ] Fetch current positions via `self.api.get_positions()`
- [ ] Handle API error responses gracefully
- [ ] Iterate over positions list
- [ ] Compare each position with `self._previous_positions[symbol]`
- [ ] Calculate percentage change per position
- [ ] Collect all alerts exceeding threshold
- [ ] Update `self._previous_positions` after check
- [ ] Run tests: `pytest tests/unit/test_story_7_2_threshold_alert.py::TestPositionThresholdChecking -v`
- [ ] Tests pass (green phase)

**Estimated Effort:** 1 hour

---

### Test: TestAlertFormatting tests

**File:** `tests/unit/test_story_7_2_threshold_alert.py`

**Tasks to make these tests pass:**

- [ ] Implement `_format_pnl_alert(data)` method
- [ ] Include timestamp in message
- [ ] Include threshold percentage in message
- [ ] Include current PnL value with sign
- [ ] Include change amount with sign
- [ ] Include percentage change
- [ ] Implement `_format_position_alert(data)` method
- [ ] Include symbol, previous/current values, change
- [ ] Follow formatting patterns from `notifier.py`
- [ ] Run tests: `pytest tests/unit/test_story_7_2_threshold_alert.py::TestAlertFormatting -v`
- [ ] Tests pass (green phase)

**Estimated Effort:** 0.5 hours

---

### Test: TestAlertCommands tests

**File:** `tests/unit/test_story_7_2_threshold_alert.py`

**Tasks to make these tests pass:**

- [ ] Create `cmd_alert_pnl` in `commands/query.py`
- [ ] Show current threshold when no args provided
- [ ] Parse and validate threshold value (1-100 range)
- [ ] Call `alerter.set_pnl_threshold(value)`
- [ ] Send confirmation message
- [ ] Create `cmd_alert_position` in `commands/query.py`
- [ ] Same pattern as cmd_alert_pnl
- [ ] Create `cmd_alert_status` in `commands/query.py`
- [ ] Show enabled status, both thresholds, check interval
- [ ] Add `get_alerter()` function in `main.py` or patch target
- [ ] Register commands in bot menu
- [ ] Run tests: `pytest tests/unit/test_story_7_2_threshold_alert.py::TestAlertCommands -v`
- [ ] Tests pass (green phase)

**Estimated Effort:** 1.5 hours

---

### Test: TestSetThresholdMethods tests

**File:** `tests/unit/test_story_7_2_threshold_alert.py`

**Tasks to make these tests pass:**

- [ ] Implement `set_pnl_threshold(value)` method
- [ ] Implement `set_position_threshold(value)` method
- [ ] Add logging for threshold changes
- [ ] Run tests: `pytest tests/unit/test_story_7_2_threshold_alert.py::TestSetThresholdMethods -v`
- [ ] Tests pass (green phase)

**Estimated Effort:** 0.25 hours

---

### Test: TestStartStop tests

**File:** `tests/unit/test_story_7_2_threshold_alert.py`

**Tasks to make these tests pass:**

- [ ] Implement `start()` async method
- [ ] Check `self.enabled` flag at start
- [ ] Set `self.running = True`
- [ ] Implement monitoring loop with `while self.running`
- [ ] Use `asyncio.sleep(self.check_interval)` for timing
- [ ] Implement `stop()` method to set running = False
- [ ] Implement `start_background()` async method
- [ ] Create and return asyncio.Task for start()
- [ ] Run tests: `pytest tests/unit/test_story_7_2_threshold_alert.py::TestStartStop -v`
- [ ] Tests pass (green phase)

**Estimated Effort:** 0.5 hours

---

### Test: TestSendAlerts tests

**File:** `tests/unit/test_story_7_2_threshold_alert.py`

**Tasks to make these tests pass:**

- [ ] Implement `_send_alerts()` async method
- [ ] Call `_check_pnl_threshold()` and handle result
- [ ] Call `_check_position_threshold()` and handle results
- [ ] Format alerts using `_format_pnl_alert()` and `_format_position_alert()`
- [ ] Send messages to all users in `self.notifier.notify_users`
- [ ] Add error handling for send failures
- [ ] Add logging for sent alerts
- [ ] Run tests: `pytest tests/unit/test_story_7_2_threshold_alert.py::TestSendAlerts -v`
- [ ] Tests pass (green phase)

**Estimated Effort:** 0.5 hours

---

## Running Tests

```bash
# Run all failing tests for this story
pytest tests/unit/test_story_7_2_threshold_alert.py -v

# Run specific test class
pytest tests/unit/test_story_7_2_threshold_alert.py::TestThresholdAlerterInit -v

# Run with coverage
pytest tests/unit/test_story_7_2_threshold_alert.py -v --cov=alerter --cov-report=term-missing

# Run in parallel (if multiple workers available)
pytest tests/unit/test_story_7_2_threshold_alert.py -v -n auto
```

---

## Red-Green-Refactor Workflow

### RED Phase (Complete)

**TEA Agent Responsibilities:**

- [x] All tests written and failing
- [x] Test data factory created with helper methods
- [x] Fixtures created for mock API and notifier
- [x] Implementation checklist created

**Verification:**

- All tests fail due to missing `alerter.py` module
- Failure messages are clear (ImportError: cannot import name 'ThresholdAlerter')
- Tests fail due to missing implementation, not test bugs

---

### GREEN Phase (DEV Team - Next Steps)

**DEV Agent Responsibilities:**

1. **Pick one failing test group** from implementation checklist (start with TestThresholdAlerterInit)
2. **Read the tests** to understand expected behavior
3. **Implement minimal code** to make those specific tests pass
4. **Run the tests** to verify they now pass (green)
5. **Check off the tasks** in implementation checklist
6. **Move to next test group** and repeat

**Key Principles:**

- One test group at a time (don't try to fix all at once)
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

**Completion:**

- All tests pass
- Code quality meets team standards
- No duplications or code smells
- Ready for code review and story approval

---

## Next Steps

1. **Review this checklist** with team in standup or planning
2. **Run failing tests** to confirm RED phase: `pytest tests/unit/test_story_7_2_threshold_alert.py -v`
3. **Begin implementation** using implementation checklist as guide
4. **Work one test group at a time** (red -> green for each)
5. **Update `/start` help text** with new commands
6. **Add environment variables to `.env.example`**
7. **When all tests pass**, refactor code for quality
8. **When refactoring complete**, manually update story status to 'done'

---

## Knowledge Base References Applied

This ATDD workflow consulted the following patterns:

- **test_story_7_1_daily_report.py** - Similar test structure and factory patterns
- **conftest.py** - Shared fixture patterns for mocking Telegram and API
- **test-levels-framework.md** - Unit test level selection for Python backend

---

## Test Execution Evidence

### Initial Test Run (RED Phase Verification)

**Command:** `pytest tests/unit/test_story_7_2_threshold_alert.py -v`

**Expected Results:**

```
================================ test session starts ================================
collected 44 items

tests/unit/test_story_7_2_threshold_alert.py::TestThresholdAlerterInit::test_init_stores_api_instance FAILED
tests/unit/test_story_7_2_threshold_alert.py::TestThresholdAlerterInit::test_init_stores_notifier_instance FAILED
... (all 44 tests fail with ImportError)
```

**Summary:**

- Total tests: 51
- Passing: 0 (expected)
- Failing: 51 (expected)
- Status: RED phase verified

**Expected Failure Messages:**

All tests fail with: `ModuleNotFoundError: No module named 'alerter'`

---

## Notes

- Tests follow the same patterns established in Story 7-1 (Daily Report)
- The `ThresholdAlerter` class follows the same lifecycle pattern as `DailyReporter` and `ActivityMonitor`
- Commands should be registered in both `commands/query.py` and `main.py`
- Consider adding validation that threshold values are positive numbers
- The alerter should integrate with the main.py `post_init()` function similar to the reporter

---

## Contact

**Questions or Issues?**

- Ask in team standup
- Refer to `_bmad-output/implementation-artifacts/7-2-threshold-alert.md` for detailed implementation guide

---

**Generated by BMad TEA Agent** - 2026-03-03
