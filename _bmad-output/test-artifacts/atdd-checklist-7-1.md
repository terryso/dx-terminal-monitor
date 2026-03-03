---
stepsCompleted: ['step-01-preflight-and-context', 'step-02-generation-mode', 'step-03-generate-tests', 'step-04-generate-factories', 'step-05-implementation-checklist']
lastStep: 'step-05-implementation-checklist'
lastSaved: '2026-03-03'
workflowType: 'testarch-atdd'
inputDocuments:
  - '_bmad-output/implementation-artifacts/7-1-daily-report.md'
  - 'tests/conftest.py'
  - 'monitor.py'
  - 'notifier.py'
  - 'api.py'
  - 'commands/query.py'
---

# ATDD Checklist - Epic 7, Story 1: Daily Report Push

**Date:** 2026-03-03
**Author:** Nick
**Primary Test Level:** Unit (Python backend)

---

## Story Summary

As a user, I want to receive an automatic daily Vault status summary, so that I can stay informed about my account status without having to actively query it.

**As a** Vault user
**I want** automatic daily status reports pushed to Telegram
**So that** I can stay informed about my account status without manual queries

---

## Acceptance Criteria

1. Extend `monitor.py` to support scheduled tasks
2. Create `reporter.py` module with `DailyReporter` class
3. Default daily push at 08:00 (configurable via `REPORT_TIME` env variable)
4. Report content: balance, 24h PnL, position changes, active strategy count
5. Support toggle commands: `/report_on`, `/report_off`
6. Add unit tests

---

## Failing Tests Created (RED Phase)

### Unit Tests (31 tests)

**File:** `tests/unit/test_story_7_1_daily_report.py` (~450 lines)

#### Test Class: TestDailyReporterInit (8 tests)

- **Test:** `test_init_stores_api_instance`
  - **Status:** RED - Module `reporter.py` does not exist
  - **Verifies:** DailyReporter stores TerminalAPI instance

- **Test:** `test_init_stores_notifier_instance`
  - **Status:** RED - Module `reporter.py` does not exist
  - **Verifies:** DailyReporter stores TelegramNotifier instance

- **Test:** `test_init_default_report_time_08_00`
  - **Status:** RED - Module `reporter.py` does not exist
  - **Verifies:** Default report time is 08:00 UTC

- **Test:** `test_init_reads_report_time_from_env`
  - **Status:** RED - Module `reporter.py` does not exist
  - **Verifies:** REPORT_TIME environment variable is read

- **Test:** `test_init_handles_invalid_report_time`
  - **Status:** RED - Module `reporter.py` does not exist
  - **Verifies:** Invalid REPORT_TIME falls back to 08:00

- **Test:** `test_init_running_flag_false`
  - **Status:** RED - Module `reporter.py` does not exist
  - **Verifies:** running flag initialized to False

- **Test:** `test_init_enabled_default_true`
  - **Status:** RED - Module `reporter.py` does not exist
  - **Verifies:** REPORT_ENABLED defaults to true

- **Test:** `test_init_enabled_from_env`
  - **Status:** RED - Module `reporter.py` does not exist
  - **Verifies:** REPORT_ENABLED read from environment

#### Test Class: TestParseReportTime (4 tests)

- **Test:** `test_parse_valid_time`
  - **Status:** RED - Module `reporter.py` does not exist
  - **Verifies:** Valid HH:MM format parsed correctly

- **Test:** `test_parse_invalid_format`
  - **Status:** RED - Module `reporter.py` does not exist
  - **Verifies:** Invalid format returns default 08:00

- **Test:** `test_parse_missing_parts`
  - **Status:** RED - Module `reporter.py` does not exist
  - **Verifies:** Malformed time string handled gracefully

- **Test:** `test_parse_empty_string`
  - **Status:** RED - Module `reporter.py` does not exist
  - **Verifies:** Empty string returns default

#### Test Class: TestCalculateNextRun (5 tests)

- **Test:** `test_calculate_next_run_future_time`
  - **Status:** RED - Module `reporter.py` does not exist
  - **Verifies:** Correct calculation when target is in future

- **Test:** `test_calculate_next_run_past_time`
  - **Status:** RED - Module `reporter.py` does not exist
  - **Verifies:** Past time results in next day calculation

- **Test:** `test_calculate_next_run_same_time`
  - **Status:** RED - Module `reporter.py` does not exist
  - **Verifies:** Current time results in 24h wait (next occurrence)

- **Test:** `test_calculate_next_run_returns_seconds`
  - **Status:** RED - Module `reporter.py` does not exist
  - **Verifies:** Returns value in seconds (float)

- **Test:** `test_calculate_next_run_uses_utc`
  - **Status:** RED - Module `reporter.py` does not exist
  - **Verifies:** Uses UTC timezone consistently

#### Test Class: TestGatherReportData (4 tests)

- **Test:** `test_gather_report_data_success`
  - **Status:** RED - Module `reporter.py` does not exist
  - **Verifies:** All API calls made and data collected

- **Test:** `test_gather_report_data_handles_api_error`
  - **Status:** RED - Module `reporter.py` does not exist
  - **Verifies:** API errors handled gracefully with fallback

- **Test:** `test_gather_report_data_empty_responses`
  - **Status:** RED - Module `reporter.py` does not exist
  - **Verifies:** Empty API responses handled correctly

- **Test:** `test_gather_report_data_partial_failure`
  - **Status:** RED - Module `reporter.py` does not exist
  - **Verifies:** Partial API failures don't break report

#### Test Class: TestFormatDailyReport (4 tests)

- **Test:** `test_format_daily_report_includes_balance`
  - **Status:** RED - Module `reporter.py` does not exist
  - **Verifies:** Report includes ETH balance and USD value

- **Test:** `test_format_daily_report_includes_pnl`
  - **Status:** RED - Module `reporter.py` does not exist
  - **Verifies:** Report includes 24h PnL with sign and percentage

- **Test:** `test_format_daily_report_includes_positions`
  - **Status:** RED - Module `reporter.py` does not exist
  - **Verifies:** Report includes position count

- **Test:** `test_format_daily_report_includes_strategies`
  - **Status:** RED - Module `reporter.py` does not exist
  - **Verifies:** Report includes active strategy count

#### Test Class: TestStartStop (4 tests)

- **Test:** `test_start_sets_running_true`
  - **Status:** RED - Module `reporter.py` does not exist
  - **Verifies:** start() sets running flag to True

- **Test:** `test_stop_sets_running_false`
  - **Status:** RED - Module `reporter.py` does not exist
  - **Verifies:** stop() sets running flag to False

- **Test:** `test_start_respects_enabled_flag`
  - **Status:** RED - Module `reporter.py` does not exist
  - **Verifies:** Disabled reporter does not start loop

- **Test:** `test_start_background_creates_task`
  - **Status:** RED - Module `reporter.py` does not exist
  - **Verifies:** start_background() creates asyncio Task

#### Test Class: TestReportCommands (2 tests)

- **Test:** `test_cmd_report_on_responds`
  - **Status:** RED - Commands not implemented
  - **Verifies:** /report_on command responds with confirmation

- **Test:** `test_cmd_report_off_responds`
  - **Status:** RED - Commands not implemented
  - **Verifies:** /report_off command responds with confirmation

---

## Data Factories Created

### ReportDataFactory

**File:** `tests/support/factories/report_data.py` (uses existing conftest.py patterns)

**Exports:**

- `create_report_data(overrides?)` - Create complete report data dict with optional overrides
- `create_balance_data(overrides?)` - Create balance data for testing
- `create_pnl_data(overrides?)` - Create PnL data for testing
- `create_positions_data(overrides?)` - Create positions data for testing
- `create_strategies_data(overrides?)` - Create strategies data for testing

**Example Usage:**

```python
from tests.conftest import ReportDataFactory

data = ReportDataFactory.create_report_data(balance_eth='2.5', pnl_usd='150.00')
```

---

## Fixtures Created

### DailyReporter Fixtures (in conftest.py extension)

**File:** `tests/conftest.py` (extended)

**Fixtures:**

- `mock_daily_reporter` - Pre-configured DailyReporter with mocked dependencies
  - **Setup:** Creates mocks for TerminalAPI and TelegramNotifier
  - **Provides:** DailyReporter instance ready for testing
  - **Cleanup:** No cleanup needed (no external resources)

- `report_data_factory` - Factory for creating test report data
  - **Setup:** Provides ReportDataFactory class
  - **Provides:** Factory methods for various data types
  - **Cleanup:** N/A

**Example Usage:**

```python
def test_example(mock_daily_reporter, report_data_factory):
    data = report_data_factory.create_report_data()
    # mock_daily_reporter is ready to use
```

---

## Mock Requirements

### TerminalAPI Mock

**Methods to Mock:**
- `get_positions()` - Returns balance and position data
- `get_pnl()` - Returns PnL data (may need to add to api.py)
- `get_strategies()` - Returns active strategies

**Success Response (positions):**
```json
{
  "ethBalance": "1500000000000000000",
  "overallValueUsd": "4500.00",
  "overallPnlUsd": "120.50",
  "overallPnlPercent": "2.75",
  "positions": [...]
}
```

**Success Response (strategies):**
```json
[
  {"strategyId": "1", "content": "...", "active": true},
  {"strategyId": "2", "content": "...", "active": true}
]
```

---

## Required data-testid Attributes

N/A - This is a backend Python project with no UI components.

---

## Implementation Checklist

### Test: `test_init_stores_api_instance`

**File:** `tests/unit/test_story_7_1_daily_report.py`

**Tasks to make this test pass:**

- [ ] Create `reporter.py` file in project root
- [ ] Import TerminalAPI from api module
- [ ] Define DailyReporter class with __init__ method
- [ ] Store api parameter as self.api
- [ ] Run test: `pytest tests/unit/test_story_7_1_daily_report.py::TestDailyReporterInit::test_init_stores_api_instance -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 0.5 hours

---

### Test: `test_init_stores_notifier_instance`

**File:** `tests/unit/test_story_7_1_daily_report.py`

**Tasks to make this test pass:**

- [ ] Import TelegramNotifier from notifier module
- [ ] Accept notifier parameter in __init__
- [ ] Store notifier as self.notifier
- [ ] Run test: `pytest tests/unit/test_story_7_1_daily_report.py::TestDailyReporterInit::test_init_stores_notifier_instance -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 0.25 hours

---

### Test: `test_init_default_report_time_08_00`

**File:** `tests/unit/test_story_7_1_daily_report.py`

**Tasks to make this test pass:**

- [ ] Create _parse_report_time method
- [ ] Default to "08:00" when no env var set
- [ ] Store as self.report_time tuple (hour, minute)
- [ ] Run test: `pytest tests/unit/test_story_7_1_daily_report.py::TestDailyReporterInit::test_init_default_report_time_08_00 -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 0.25 hours

---

### Test: `test_init_reads_report_time_from_env`

**File:** `tests/unit/test_story_7_1_daily_report.py`

**Tasks to make this test pass:**

- [ ] Read REPORT_TIME from os.environ
- [ ] Parse HH:MM format
- [ ] Run test: `pytest tests/unit/test_story_7_1_daily_report.py::TestDailyReporterInit::test_init_reads_report_time_from_env -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 0.25 hours

---

### Test: `test_calculate_next_run_future_time`

**File:** `tests/unit/test_story_7_1_daily_report.py`

**Tasks to make this test pass:**

- [ ] Create _calculate_next_run method
- [ ] Use datetime.utcnow() for current time
- [ ] Calculate seconds until next scheduled time
- [ ] Run test: `pytest tests/unit/test_story_7_1_daily_report.py::TestCalculateNextRun::test_calculate_next_run_future_time -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 0.5 hours

---

### Test: `test_gather_report_data_success`

**File:** `tests/unit/test_story_7_1_daily_report.py`

**Tasks to make this test pass:**

- [ ] Create async _gather_report_data method
- [ ] Call api.get_positions() for balance
- [ ] Call api.get_strategies() for strategy count
- [ ] Handle API response structures correctly
- [ ] Run test: `pytest tests/unit/test_story_7_1_daily_report.py::TestGatherReportData::test_gather_report_data_success -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 0.5 hours

---

### Test: `test_format_daily_report_includes_balance`

**File:** `tests/unit/test_story_7_1_daily_report.py`

**Tasks to make this test pass:**

- [ ] Create _format_daily_report method
- [ ] Include date in header
- [ ] Format balance using format_eth and format_usd
- [ ] Run test: `pytest tests/unit/test_story_7_1_daily_report.py::TestFormatDailyReport::test_format_daily_report_includes_balance -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 0.5 hours

---

### Test: `test_start_sets_running_true`

**File:** `tests/unit/test_story_7_1_daily_report.py`

**Tasks to make this test pass:**

- [ ] Create async start method
- [ ] Set self.running = True
- [ ] Run test: `pytest tests/unit/test_story_7_1_daily_report.py::TestStartStop::test_start_sets_running_true -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 0.5 hours

---

### Test: `test_cmd_report_on_responds`

**File:** `tests/unit/test_story_7_1_daily_report.py`

**Tasks to make this test pass:**

- [ ] Create cmd_report_on in commands/query.py
- [ ] Add authorized check
- [ ] Send confirmation message
- [ ] Register in commands/__init__.py
- [ ] Run test: `pytest tests/unit/test_story_7_1_daily_report.py::TestReportCommands::test_cmd_report_on_responds -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 0.5 hours

---

## Running Tests

```bash
# Run all failing tests for this story
pytest tests/unit/test_story_7_1_daily_report.py -v

# Run specific test class
pytest tests/unit/test_story_7_1_daily_report.py::TestDailyReporterInit -v

# Run with coverage
pytest tests/unit/test_story_7_1_daily_report.py --cov=. --cov-report=term-missing

# Run in debug mode
pytest tests/unit/test_story_7_1_daily_report.py -v --pdb
```

---

## Red-Green-Refactor Workflow

### RED Phase (Complete)

**TEA Agent Responsibilities:**

- All tests written and failing
- Factory patterns documented
- Mock requirements documented
- Implementation checklist created

**Verification:**

- All tests fail due to missing `reporter.py` module
- Failure messages are clear (ImportError: No module named 'reporter')
- Tests ready for implementation phase

---

### GREEN Phase (DEV Team - Next Steps)

**DEV Agent Responsibilities:**

1. **Pick one failing test** from implementation checklist (start with test_init_stores_api_instance)
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

1. **Review this checklist** with team
2. **Run failing tests** to confirm RED phase: `pytest tests/unit/test_story_7_1_daily_report.py -v`
3. **Begin implementation** using implementation checklist as guide
4. **Work one test at a time** (red -> green for each)
5. **When all tests pass**, add command registration to main.py
6. **Update /start help text** to include /report_on and /report_off
7. **When complete**, update story status to 'done' in sprint-status.yaml

---

## Knowledge Base References Applied

This ATDD workflow consulted the following knowledge fragments:

- **data-factories.md** - Factory patterns using existing conftest.py patterns
- **test-quality.md** - Test design principles (Given-When-Then, one assertion per test, determinism, isolation)
- **test-levels-framework.md** - Test level selection framework (Unit tests for backend Python)

---

## Notes

- Story follows patterns established in Story 4-1 (ActivityMonitor)
- Uses same scheduling pattern with start(), stop(), start_background()
- Reuses format_eth and format_usd from notifier.py
- Test file naming follows established pattern: test_story_X_Y_description.py

---

**Generated by BMad TEA Agent** - 2026-03-03
