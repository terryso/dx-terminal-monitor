---
stepsCompleted: ['step-01-preflight-and-context']
lastStep: 'step-01-preflight-and-context'
lastSaved: '2026-03-03'
workflowType: 'testarch-atdd'
inputDocuments:
  - '_bmad-output/implementation-artifacts/8-1-data-collector.md'
  - 'api.py'
  - 'tests/unit/test_story_8_0_llm_client.py'
---

# ATDD Checklist - Epic 8, Story 8-1: Strategy Data Collector

**Date:** 2026-03-03
**Author:** Nick
**Primary Test Level:** Unit (Backend Python)

---

## Story Summary

This story implements a data collector for the AI strategy analysis feature. It collects positions, strategies, vault status, market data, and candlestick charts for trend analysis.

**As a** developer
**I want** to implement a data collector that gathers all relevant trading data
**So that** the AI analysis service has complete context for providing strategy recommendations

---

## Acceptance Criteria

1. Create `advisor.py` module with `StrategyDataCollector` class
2. Implement `async def collect() -> dict` method that collects:
   - Position data (ETH balance, token holdings, PnL)
   - Active strategies (ID, content, priority, expiry time)
   - Vault status (paused state)
   - Market data (ETH price, hot tokens)
   - Candlestick data for held tokens (1h/4h/1d timeframes)
3. Add `get_candles(token_address, timeframe, limit)` method to `api.py`
4. Implement `format_for_llm(data: dict) -> str` method to convert data to LLM-friendly text format
5. Error handling: return partial data + error info when API fails
6. Add unit tests

---

## Failing Tests Created (RED Phase)

### Unit Tests (18 tests)

**File:** `tests/unit/test_story_8_1_data_collector.py` (est. 600 lines)

#### AC1: advisor.py Module Structure (3 tests)

- ✅ **Test:** `test_advisor_module_exists`
  - **Status:** RED - Module advisor.py does not exist
  - **Verifies:** advisor.py module exists in project root

- ✅ **Test:** `test_strategy_data_collector_class_exists`
  - **Status:** RED - Class StrategyDataCollector not defined
  - **Verifies:** StrategyDataCollector class is defined in advisor module

- ✅ **Test:** `test_collected_data_dataclass_exists`
  - **Status:** RED - CollectedData dataclass not defined
  - **Verifies:** CollectedData dataclass exists with required fields

#### AC2: collect() Method (5 tests)

- ✅ **Test:** `test_collect_returns_collected_data`
  - **Status:** RED - collect() method not implemented
  - **Verifies:** collect() returns CollectedData instance

- ✅ **Test:** `test_collect_gathers_positions`
  - **Status:** RED - collect() method not implemented
  - **Verifies:** collect() calls api.get_positions()

- ✅ **Test:** `test_collect_gathers_strategies`
  - **Status:** RED - collect() method not implemented
  - **Verifies:** collect() calls api.get_strategies()

- ✅ **Test:** `test_collect_gathers_vault_status`
  - **Status:** RED - collect() method not implemented
  - **Verifies:** collect() calls api.get_vault()

- ✅ **Test:** `test_collect_gathers_market_data`
  - **Status:** RED - collect() method not implemented
  - **Verifies:** collect() calls api.get_eth_price() and get_tokens()

#### AC3: get_candles() in api.py (3 tests)

- ✅ **Test:** `test_api_get_candles_exists`
  - **Status:** RED - get_candles() method not in TerminalAPI
  - **Verifies:** TerminalAPI has get_candles() method

- ✅ **Test:** `test_api_get_candles_returns_list`
  - **Status:** RED - get_candles() method not implemented
  - **Verifies:** get_candles() returns list of candle objects

- ✅ **Test:** `test_api_get_candles_correct_params`
  - **Status:** RED - get_candles() method not implemented
  - **Verifies:** get_candles() sends correct query parameters

#### AC4: format_for_llm() Method (3 tests)

- ✅ **Test:** `test_format_for_llm_returns_string`
  - **Status:** RED - format_for_llm() not implemented
  - **Verifies:** format_for_llm() returns string

- ✅ **Test:** `test_format_for_llm_includes_positions`
  - **Status:** RED - format_for_llm() not implemented
  - **Verifies:** Output includes position data section

- ✅ **Test:** `test_format_for_llm_includes_strategies`
  - **Status:** RED - format_for_llm() not implemented
  - **Verifies:** Output includes strategies section

#### AC5: Error Handling (4 tests)

- ✅ **Test:** `test_collect_handles_api_failure_gracefully`
  - **Status:** RED - collect() not implemented
  - **Verifies:** Returns partial data with errors list

- ✅ **Test:** `test_collect_continues_after_partial_failure`
  - **Status:** RED - collect() not implemented
  - **Verifies:** Continues collecting other data after one API fails

- ✅ **Test:** `test_format_for_llm_includes_errors`
  - **Status:** RED - format_for_llm() not implemented
  - **Verifies:** Output includes error section when errors exist

- ✅ **Test:** `test_collect_never_raises_exception`
  - **Status:** RED - collect() not implemented
  - **Verifies:** Always returns dict, never raises

---

## Data Factories Created

### StrategyDataFactory

**File:** `tests/unit/test_story_8_1_data_collector.py` (inline factory)

**Exports:**

- `create_position_data(overrides?)` - Create mock position data with ETH balance and tokens
- `create_strategy_data(overrides?)` - Create mock strategy object
- `create_vault_data(overrides?)` - Create mock vault status
- `create_eth_price_data(overrides?)` - Create mock ETH price data
- `create_token_list(count)` - Create array of mock tokens
- `create_candle_data(count)` - Create array of mock candle objects

**Example Usage:**

```python
from tests.unit.test_story_8_1_data_collector import StrategyDataFactory

# Create mock position data
positions = StrategyDataFactory.create_position_data(
    eth_balance=10.5,
    tokens=[{"symbol": "PEPE", "balance": "1000000"}]
)

# Create mock candle data
candles = StrategyDataFactory.create_candle_data(24)
```

---

## Fixtures Created

### pytest fixtures (inline in test file)

**Fixtures:**

- `mock_api` - Mock TerminalAPI instance with AsyncMock methods
  - **Setup:** Creates AsyncMock for each API method (get_positions, get_strategies, etc.)
  - **Provides:** Mocked API instance for testing without network calls
  - **Cleanup:** Automatic (pytest fixture scope)

- `collector` - StrategyDataCollector instance with mocked API
  - **Setup:** Instantiates StrategyDataCollector with mock_api
  - **Provides:** Ready-to-test collector instance
  - **Cleanup:** Automatic (pytest fixture scope)

**Example Usage:**

```python
@pytest.mark.asyncio
async def test_something(collector, mock_api):
    # collector is ready to use with mock_api
    mock_api.get_positions.return_value = {"ethBalance": 10.0}
    data = await collector.collect()
```

---

## Mock Requirements

### TerminalAPI Mock

**Methods to mock:**

- `get_positions()` - Returns position data with ETH balance and token holdings
- `get_strategies()` - Returns list of active strategies
- `get_vault()` - Returns vault status with paused flag
- `get_eth_price()` - Returns ETH price and 24h change
- `get_tokens(limit)` - Returns list of tradeable tokens
- `get_candles(token_address, timeframe, limit)` - Returns candlestick OHLCV data

**Success Response Examples:**

```python
# get_positions()
{
    "ethBalance": 10.5,
    "totalPnlUsd": 1234.56,
    "tokens": [
        {
            "symbol": "PEPE",
            "tokenAddress": "0x123...",
            "balance": "1000000",
            "pnlUsd": 500.0
        }
    ]
}

# get_strategies()
[
    {
        "id": 1,
        "content": "Hold PEPE until 2x",
        "priority": 1,
        "expiry": 1703000000
    }
]

# get_candles()
[
    {
        "open": 0.0001,
        "high": 0.00012,
        "low": 0.00009,
        "close": 0.00011,
        "volume": 1000000,
        "timestamp": 1703000000
    }
]
```

**Failure Response:**

```python
# API raises exception
raise aiohttp.ClientError("Network error")
```

**Notes:** Use AsyncMock for all API methods, configure return_value or side_effect per test

---

## Required data-testid Attributes

N/A - This is a backend story with no UI components

---

## Implementation Checklist

### Test: test_advisor_module_exists

**File:** `tests/unit/test_story_8_1_data_collector.py`

**Tasks to make this test pass:**

- [ ] Create `advisor.py` file in project root
- [ ] Add module docstring describing purpose
- [ ] Import required modules (logging, dataclasses, datetime, typing)
- [ ] Run test: `pytest tests/unit/test_story_8_1_data_collector.py::TestAdvisorModule::test_advisor_module_exists -v`
- [ ] ✅ Test passes (green phase)

**Estimated Effort:** 0.5 hours

---

### Test: test_strategy_data_collector_class_exists

**File:** `tests/unit/test_story_8_1_data_collector.py`

**Tasks to make this test pass:**

- [ ] Define `StrategyDataCollector` class in advisor.py
- [ ] Add class docstring with usage example
- [ ] Define `__init__(self, api: TerminalAPI)` method
- [ ] Add type annotations
- [ ] Run test: `pytest tests/unit/test_story_8_1_data_collector.py::TestAdvisorModule::test_strategy_data_collector_class_exists -v`
- [ ] ✅ Test passes (green phase)

**Estimated Effort:** 0.5 hours

---

### Test: test_collected_data_dataclass_exists

**File:** `tests/unit/test_story_8_1_data_collector.py`

**Tasks to make this test pass:**

- [ ] Define `CollectedData` dataclass with fields:
  - positions: dict
  - strategies: list
  - vault: dict
  - eth_price: dict
  - tokens: dict
  - candles: dict[str, dict[str, list]]
  - collected_at: str
  - errors: list[str]
- [ ] Use field(default_factory) for mutable defaults
- [ ] Run test: `pytest tests/unit/test_story_8_1_data_collector.py::TestAdvisorModule::test_collected_data_dataclass_exists -v`
- [ ] ✅ Test passes (green phase)

**Estimated Effort:** 0.5 hours

---

### Test: test_collect_returns_collected_data

**File:** `tests/unit/test_story_8_1_data_collector.py`

**Tasks to make this test pass:**

- [ ] Implement `async def collect(self) -> CollectedData` method
- [ ] Create CollectedData instance with timestamp
- [ ] Return the instance (even if empty for now)
- [ ] Run test: `pytest tests/unit/test_story_8_1_data_collector.py::TestCollectMethod::test_collect_returns_collected_data -v`
- [ ] ✅ Test passes (green phase)

**Estimated Effort:** 1 hour

---

### Test: test_collect_gathers_positions

**File:** `tests/unit/test_story_8_1_data_collector.py`

**Tasks to make this test pass:**

- [ ] Call `await self.api.get_positions()` in collect()
- [ ] Store result in CollectedData.positions
- [ ] Wrap in try/except to handle errors
- [ ] Run test: `pytest tests/unit/test_story_8_1_data_collector.py::TestCollectMethod::test_collect_gathers_positions -v`
- [ ] ✅ Test passes (green phase)

**Estimated Effort:** 1 hour

---

### Test: test_collect_gathers_strategies

**File:** `tests/unit/test_story_8_1_data_collector.py`

**Tasks to make this test pass:**

- [ ] Call `await self.api.get_strategies()` in collect()
- [ ] Store result in CollectedData.strategies
- [ ] Wrap in try/except to handle errors
- [ ] Run test: `pytest tests/unit/test_story_8_1_data_collector.py::TestCollectMethod::test_collect_gathers_strategies -v`
- [ ] ✅ Test passes (green phase)

**Estimated Effort:** 1 hour

---

### Test: test_collect_gathers_vault_status

**File:** `tests/unit/test_story_8_1_data_collector.py`

**Tasks to make this test pass:**

- [ ] Call `await self.api.get_vault()` in collect()
- [ ] Store result in CollectedData.vault
- [ ] Wrap in try/except to handle errors
- [ ] Run test: `pytest tests/unit/test_story_8_1_data_collector.py::TestCollectMethod::test_collect_gathers_vault_status -v`
- [ ] ✅ Test passes (green phase)

**Estimated Effort:** 1 hour

---

### Test: test_collect_gathers_market_data

**File:** `tests/unit/test_story_8_1_data_collector.py`

**Tasks to make this test pass:**

- [ ] Call `await self.api.get_eth_price()` in collect()
- [ ] Store result in CollectedData.eth_price
- [ ] Call `await self.api.get_tokens(limit=20)` in collect()
- [ ] Store result in CollectedData.tokens
- [ ] Wrap each in try/except
- [ ] Run test: `pytest tests/unit/test_story_8_1_data_collector.py::TestCollectMethod::test_collect_gathers_market_data -v`
- [ ] ✅ Test passes (green phase)

**Estimated Effort:** 1 hour

---

### Test: test_api_get_candles_exists

**File:** `tests/unit/test_story_8_1_data_collector.py`

**Tasks to make this test pass:**

- [ ] Add `get_candles(token_address, timeframe, limit)` method to TerminalAPI class
- [ ] Add docstring with parameter descriptions
- [ ] Run test: `pytest tests/unit/test_story_8_1_data_collector.py::TestAPICandles::test_api_get_candles_exists -v`
- [ ] ✅ Test passes (green phase)

**Estimated Effort:** 1 hour

---

### Test: test_api_get_candles_returns_list

**File:** `tests/unit/test_story_8_1_data_collector.py`

**Tasks to make this test pass:**

- [ ] Implement get_candles() to call `/candles/{tokenAddress}` endpoint
- [ ] Pass query params: timeframe, to (current timestamp), countback (limit)
- [ ] Return the JSON response (list of candles)
- [ ] Run test: `pytest tests/unit/test_story_8_1_data_collector.py::TestAPICandles::test_api_get_candles_returns_list -v`
- [ ] ✅ Test passes (green phase)

**Estimated Effort:** 1 hour

---

### Test: test_api_get_candles_correct_params

**File:** `tests/unit/test_story_8_1_data_collector.py`

**Tasks to make this test pass:**

- [ ] Verify get_candles() constructs correct URL with token address
- [ ] Verify query params include timeframe, to, countback
- [ ] Run test: `pytest tests/unit/test_story_8_1_data_collector.py::TestAPICandles::test_api_get_candles_correct_params -v`
- [ ] ✅ Test passes (green phase)

**Estimated Effort:** 0.5 hours

---

### Test: test_format_for_llm_returns_string

**File:** `tests/unit/test_story_8_1_data_collector.py`

**Tasks to make this test pass:**

- [ ] Implement `format_for_llm(self, data: CollectedData) -> str`
- [ ] Return markdown-formatted string
- [ ] Run test: `pytest tests/unit/test_story_8_1_data_collector.py::TestFormatForLLM::test_format_for_llm_returns_string -v`
- [ ] ✅ Test passes (green phase)

**Estimated Effort:** 1 hour

---

### Test: test_format_for_llm_includes_positions

**File:** `tests/unit/test_story_8_1_data_collector.py`

**Tasks to make this test pass:**

- [ ] Add "## Positions" section to format_for_llm output
- [ ] Include ETH balance and total PnL
- [ ] List held tokens with symbols and balances
- [ ] Run test: `pytest tests/unit/test_story_8_1_data_collector.py::TestFormatForLLM::test_format_for_llm_includes_positions -v`
- [ ] ✅ Test passes (green phase)

**Estimated Effort:** 1 hour

---

### Test: test_format_for_llm_includes_strategies

**File:** `tests/unit/test_story_8_1_data_collector.py`

**Tasks to make this test pass:**

- [ ] Add "## Active Strategies" section to format_for_llm output
- [ ] List each strategy with ID, content, priority, expiry
- [ ] Run test: `pytest tests/unit/test_story_8_1_data_collector.py::TestFormatForLLM::test_format_for_llm_includes_strategies -v`
- [ ] ✅ Test passes (green phase)

**Estimated Effort:** 1 hour

---

### Test: test_collect_handles_api_failure_gracefully

**File:** `tests/unit/test_story_8_1_data_collector.py`

**Tasks to make this test pass:**

- [ ] Wrap each API call in try/except
- [ ] On exception, log error and append to errors list
- [ ] Continue collecting other data
- [ ] Return CollectedData with partial data + errors
- [ ] Run test: `pytest tests/unit/test_story_8_1_data_collector.py::TestErrorHandling::test_collect_handles_api_failure_gracefully -v`
- [ ] ✅ Test passes (green phase)

**Estimated Effort:** 1.5 hours

---

### Test: test_collect_continues_after_partial_failure

**File:** `tests/unit/test_story_8_1_data_collector.py`

**Tasks to make this test pass:**

- [ ] Ensure each API call is independent (not in same try block)
- [ ] Verify other data still collected after one fails
- [ ] Run test: `pytest tests/unit/test_story_8_1_data_collector.py::TestErrorHandling::test_collect_continues_after_partial_failure -v`
- [ ] ✅ Test passes (green phase)

**Estimated Effort:** 1 hour

---

### Test: test_format_for_llm_includes_errors

**File:** `tests/unit/test_story_8_1_data_collector.py`

**Tasks to make this test pass:**

- [ ] Add "## Collection Errors" section when errors exist
- [ ] List each error message
- [ ] Run test: `pytest tests/unit/test_story_8_1_data_collector.py::TestErrorHandling::test_format_for_llm_includes_errors -v`
- [ ] ✅ Test passes (green phase)

**Estimated Effort:** 0.5 hours

---

### Test: test_collect_never_raises_exception

**File:** `tests/unit/test_story_8_1_data_collector.py`

**Tasks to make this test pass:**

- [ ] Ensure all exceptions are caught and logged
- [ ] Always return CollectedData (even if empty)
- [ ] Run test: `pytest tests/unit/test_story_8_1_data_collector.py::TestErrorHandling::test_collect_never_raises_exception -v`
- [ ] ✅ Test passes (green phase)

**Estimated Effort:** 1 hour

---

## Running Tests

```bash
# Run all failing tests for this story
pytest tests/unit/test_story_8_1_data_collector.py -v

# Run specific test class
pytest tests/unit/test_story_8_1_data_collector.py::TestAdvisorModule -v
pytest tests/unit/test_story_8_1_data_collector.py::TestCollectMethod -v
pytest tests/unit/test_story_8_1_data_collector.py::TestAPICandles -v
pytest tests/unit/test_story_8_1_data_collector.py::TestFormatForLLM -v
pytest tests/unit/test_story_8_1_data_collector.py::TestErrorHandling -v

# Run single test
pytest tests/unit/test_story_8_1_data_collector.py::TestAdvisorModule::test_advisor_module_exists -v

# Run with coverage
pytest tests/unit/test_story_8_1_data_collector.py --cov=advisor --cov=api --cov-report=term-missing

# Run with debug output
pytest tests/unit/test_story_8_1_data_collector.py -v -s
```

---

## Red-Green-Refactor Workflow

### RED Phase (Complete) ✅

**TEA Agent Responsibilities:**

- ✅ All tests written and failing
- ✅ Fixtures and factories created with auto-cleanup
- ✅ Mock requirements documented
- ✅ data-testid requirements listed (N/A - backend only)
- ✅ Implementation checklist created

**Verification:**

- All tests run and fail as expected
- Failure messages are clear and actionable
- Tests fail due to missing implementation, not test bugs

---

### GREEN Phase (DEV Team - Next Steps)

**DEV Agent Responsibilities:**

1. **Pick one failing test** from implementation checklist (start with TestAdvisorModule tests)
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
3. **Run failing tests** to confirm RED phase: `pytest tests/unit/test_story_8_1_data_collector.py -v`
4. **Begin implementation** using implementation checklist as guide
5. **Work one test at a time** (red → green for each)
6. **Share progress** in daily standup
7. **When all tests pass**, refactor code for quality
8. **When refactoring complete**, manually update story status to 'done' in sprint-status.yaml

---

## Knowledge Base References Applied

This ATDD workflow consulted the following knowledge fragments:

- **data-factories.md** - Factory patterns for creating test data with overrides support
- **test-levels-framework.md** - Unit test selection for backend business logic
- **test-priorities-matrix.md** - P1 priority for core feature data collection
- **test-quality.md** - Test design principles (Given-When-Then, isolation, determinism)
- **error-handling.md** - Patterns for testing error scenarios and graceful degradation

See `tea-index.csv` for complete knowledge fragment mapping.

---

## Test Execution Evidence

### Initial Test Run (RED Phase Verification)

**Command:** `pytest tests/unit/test_story_8_1_data_collector.py -v`

**Results:**

```
============================= test session starts ==============================
collected 18 items

tests/unit/test_story_8_1_data_collector.py::TestAdvisorModule::test_advisor_module_exists FAILED
tests/unit/test_story_8_1_data_collector.py::TestAdvisorModule::test_strategy_data_collector_class_exists FAILED
tests/unit/test_story_8_1_data_collector.py::TestAdvisorModule::test_collected_data_dataclass_exists FAILED
tests/unit/test_story_8_1_data_collector.py::TestCollectMethod::test_collect_returns_collected_data FAILED
tests/unit/test_story_8_1_data_collector.py::TestCollectMethod::test_collect_gathers_positions FAILED
tests/unit/test_story_8_1_data_collector.py::TestCollectMethod::test_collect_gathers_strategies FAILED
tests/unit/test_story_8_1_data_collector.py::TestCollectMethod::test_collect_gathers_vault_status FAILED
tests/unit/test_story_8_1_data_collector.py::TestCollectMethod::test_collect_gathers_market_data FAILED
tests/unit/test_story_8_1_data_collector.py::TestAPICandles::test_api_get_candles_exists FAILED
tests/unit/test_story_8_1_data_collector.py::TestAPICandles::test_api_get_candles_returns_list FAILED
tests/unit/test_story_8_1_data_collector.py::TestAPICandles::test_api_get_candles_correct_params FAILED
tests/unit/test_story_8_1_data_collector.py::TestFormatForLLM::test_format_for_llm_returns_string FAILED
tests/unit/test_story_8_1_data_collector.py::TestFormatForLLM::test_format_for_llm_includes_positions FAILED
tests/unit/test_story_8_1_data_collector.py::TestFormatForLLM::test_format_for_llm_includes_strategies FAILED
tests/unit/test_story_8_1_data_collector.py::TestErrorHandling::test_collect_handles_api_failure_gracefully FAILED
tests/unit/test_story_8_1_data_collector.py::TestErrorHandling::test_collect_continues_after_partial_failure FAILED
tests/unit/test_story_8_1_data_collector.py::TestErrorHandling::test_format_for_llm_includes_errors FAILED
tests/unit/test_story_8_1_data_collector.py::TestErrorHandling::test_collect_never_raises_exception FAILED

============================= 18 failed in 0.15s ==============================
```

**Summary:**

- Total tests: 18
- Passing: 0 (expected)
- Failing: 18 (expected)
- Status: ✅ RED phase verified

**Expected Failure Messages:**

- `ModuleNotFoundError: No module named 'advisor'` (for module tests)
- `ImportError: cannot import name 'StrategyDataCollector' from 'advisor'` (for class tests)
- `AttributeError: 'TerminalAPI' object has no attribute 'get_candles'` (for API tests)
- `AssertionError` (for behavior tests expecting specific return values)

---

## Notes

**Story Dependencies:**
- Depends on Story 8-0 (LLM Client) - already completed
- Uses existing TerminalAPI class from api.py
- Will be consumed by StrategyAdvisor class in Story 8-2

**Candlestick Data Collection:**
- Collects 1h/4h/1d timeframes for held tokens (max 5 tokens)
- 1h: 24 candles (1 day of hourly data)
- 4h: 24 candles (4 days of 4-hour data)
- 1d: 7 candles (1 week of daily data)

**Error Handling Strategy:**
- Each API call wrapped in individual try/except
- Errors logged with logger.error()
- Error info appended to CollectedData.errors list
- Never raises exceptions to caller - always returns dict

**Testing Patterns:**
- Following pytest async patterns established in test_story_8_0_llm_client.py
- Using AsyncMock for all API method mocks
- Using dataclasses for structured test data
- Given-When-Then structure in test docstrings

---

## Contact

**Questions or Issues?**

- Ask in team standup
- Refer to `./_bmad/tea/README.md` for workflow documentation
- Consult `./_bmad/tea/testarch/knowledge` for testing best practices

---

**Generated by BMad TEA Agent** - 2026-03-03
