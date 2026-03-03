# ATDD Checklist for Story 8-2: AI Strategy Analysis Service

**Generated**: 2026-03-03
**Story**: 8-2-ai-advisor
**Status**: Ready for TDD Red Phase

## Acceptance Criteria Coverage

### AC1: Implement `StrategyAdvisor` class in `advisor.py`
- [ ] Test: StrategyAdvisor class exists in advisor module
- [ ] Test: StrategyAdvisor accepts LLMClient in constructor
- [ ] Test: StrategyAdvisor accepts TerminalAPI in constructor
- [ ] Test: StrategyAdvisor creates StrategyDataCollector internally

### AC2: Implement `async def analyze() -> list[Suggestion]` method
- [ ] Test: analyze() method exists and is async
- [ ] Test: analyze() returns list of Suggestion objects
- [ ] Test: analyze() calls collector.collect() to gather data
- [ ] Test: analyze() calls collector.format_for_llm() to format data
- [ ] Test: analyze() calls llm.chat() with system prompt and user message
- [ ] Test: analyze() parses JSON response to extract suggestions
- [ ] Test: analyze() limits suggestions to MAX_SUGGESTIONS (3)

### AC3: Design system prompt (System Prompt)
- [ ] Test: SYSTEM_PROMPT constant exists in advisor module
- [ ] Test: SYSTEM_PROMPT includes advisor role definition
- [ ] Test: SYSTEM_PROMPT specifies JSON output format
- [ ] Test: SYSTEM_PROMPT includes example JSON structure
- [ ] Test: SYSTEM_PROMPT provides guidelines for recommendations

### AC4: Output structure `Suggestion`
- [ ] Test: Suggestion dataclass exists in advisor module
- [ ] Test: Suggestion has action field with Literal["add", "disable"] type
- [ ] Test: Suggestion has content field (optional, for add action)
- [ ] Test: Suggestion has priority field (default: 1)
- [ ] Test: Suggestion has expiry_hours field (default: 0)
- [ ] Test: Suggestion has strategy_id field (optional, for disable action)
- [ ] Test: Suggestion has reason field (default: "")
- [ ] Test: Suggestion validates action-specific required fields (__post_init__)
- [ ] Test: Suggestion raises ValueError when content missing for "add" action
- [ ] Test: Suggestion raises ValueError when strategy_id missing for "disable" action

### AC5: Scheduled task configuration
- [ ] Test: ADVISOR_INTERVAL_HOURS config exists (default: 2)
- [ ] Test: ADVISOR_ENABLED config exists (default: true)
- [ ] Test: .env.example includes ADVISOR_ENABLED documentation
- [ ] Test: .env.example includes ADVISOR_INTERVAL_HOURS documentation

### AC6: Add unit tests (Mock LLM response)
- [ ] Test: Test file created at tests/unit/test_story_8_2_ai_advisor.py
- [ ] Test: Test Suggestion dataclass creation and validation
- [ ] Test: Test StrategyAdvisor initialization
- [ ] Test: Test analyze() with successful LLM response (Mock)
- [ ] Test: Test analyze() with add strategy suggestion
- [ ] Test: Test analyze() with disable strategy suggestion
- [ ] Test: Test analyze() with multiple suggestions
- [ ] Test: Test _parse_suggestions() with valid JSON
- [ ] Test: Test _parse_suggestions() with JSON in markdown code block
- [ ] Test: Test _parse_suggestions() with invalid JSON
- [ ] Test: Test analyze() with LLM error response
- [ ] Test: Test analyze() with data collection errors

## Test Execution Plan

### Phase 1: RED (Current)
All tests should FAIL because implementation doesn't exist yet.

**Run Command**:
```bash
pytest tests/unit/test_story_8_2_ai_advisor.py -v
```

**Expected**: All tests fail with ImportError or AttributeError

### Phase 2: GREEN (After Implementation)
Implement the features to make all tests pass.

**Implementation Files**:
1. `advisor.py` - Add Suggestion dataclass and StrategyAdvisor class
2. `config.py` - Add ADVISOR_ENABLED and ADVISOR_INTERVAL_HOURS
3. `.env.example` - Add configuration documentation

### Phase 3: REFACTOR (Optional)
Optimize code while keeping tests green.

## Test Categories

### Unit Tests
- **Suggestion Dataclass Tests**: 6 tests
  - Test creation with valid data
  - Test validation for "add" action
  - Test validation for "disable" action
  - Test default values
  - Test invalid action types
  - Test field types

- **StrategyAdvisor Class Tests**: 4 tests
  - Test class exists
  - Test constructor with LLMClient and TerminalAPI
  - Test internal StrategyDataCollector creation
  - Test MAX_SUGGESTIONS constant

- **analyze() Method Tests**: 8 tests
  - Test method exists and is async
  - Test returns list of Suggestion
  - Test calls collect() and format_for_llm()
  - Test calls llm.chat() with correct params
  - Test successful parsing of suggestions
  - Test handles LLM errors gracefully
  - Test handles empty suggestions
  - Test limits to MAX_SUGGESTIONS

- **JSON Parsing Tests**: 6 tests
  - Test parse valid JSON response
  - Test parse JSON in markdown code block
  - Test parse JSON without code block
  - Test handle invalid JSON
  - Test handle missing suggestions key
  - Test handle malformed suggestion objects

- **Configuration Tests**: 4 tests
  - Test ADVISOR_ENABLED exists with default true
  - Test ADVISOR_INTERVAL_HOURS exists with default 2
  - Test .env.example includes both configs
  - Test config values are used correctly

### Integration Tests
- **End-to-End Flow**: 3 tests
  - Test full flow from data collection to suggestion output
  - Test error handling in full flow
  - Test empty data scenario

## Test File Structure

```
tests/unit/test_story_8_2_ai_advisor.py
├── Test Data Factory (SuggestionFactory)
├── Fixtures (mock_llm, mock_api, advisor)
├── Test Classes:
│   ├── TestSuggestionDataclass (AC4)
│   ├── TestStrategyAdvisorClass (AC1)
│   ├── TestAnalyzeMethod (AC2)
│   ├── TestSystemPrompt (AC3)
│   ├── TestJSONParsing (AC2, AC4)
│   ├── TestConfiguration (AC5)
│   └── TestErrorHandling (AC2, AC6)
```

## Dependencies

### Existing Modules (Implemented)
- `llm.py` - LLMClient with chat() method (Story 8-0)
- `api.py` - TerminalAPI with all data methods (Epic 1-7)
- `advisor.py` - StrategyDataCollector (Story 8-1)
- `config.py` - Configuration management

### Test Utilities
- `unittest.mock` - AsyncMock, MagicMock, patch
- `pytest` - Test framework
- `pytest-asyncio` - Async test support

## Success Criteria

- [ ] All 31 tests implemented
- [ ] All tests fail in RED phase (ImportError/AttributeError)
- [ ] Test coverage targets all acceptance criteria
- [ ] Tests follow patterns from 8-0 and 8-1
- [ ] Test file naming: `test_story_8_2_ai_advisor.py`
- [ ] Each test has clear GIVEN/WHEN/THEN structure

## Notes

- Follow test patterns from Story 8-0 (LLM Client) and 8-1 (Data Collector)
- Use StrategyDataFactory from Story 8-1 for test data
- Mock LLM responses to avoid external dependencies
- Test edge cases: empty suggestions, invalid JSON, API errors
- Ensure graceful degradation on errors (return empty list)
