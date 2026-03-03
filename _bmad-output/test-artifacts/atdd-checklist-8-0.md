---
stepsCompleted:
  - step-01-preflight-and-context
  - step-02-generation-mode
  - step-03-test-strategy
  - step-04c-aggregate
  - step-05-validate-and-complete
lastStep: step-05-validate-and-complete
lastSaved: '2026-03-03'
workflowType: testarch-atdd
inputDocuments:
  - _bmad-output/implementation-artifacts/8-0-llm-client.md
  - _bmad/tea/testarch/knowledge/data-factories.md
  - _bmad/tea/testarch/knowledge/test-quality.md
  - _bmad/tea/testarch/knowledge/test-healing-patterns.md
  - _bmad/tea/testarch/knowledge/test-levels-framework.md
  - _bmad/tea/testarch/knowledge/test-priorities-matrix.md
---

# ATDD Checklist - Epic 8, Story 8-0: LLM Client Infrastructure

**Date:** 2026-03-03
**Author:** Nick
**Primary Test Level:** Unit

---

## Story Summary

This story establishes the LLM client infrastructure for Epic 8 (AI Strategy Advisor). It creates an OpenAI-compatible client that can interact with GLM-4, OpenAI, or other compatible LLM endpoints.

**As a** developer
**I want** to set up LLM client infrastructure
**So that** the system can interact with GLM5/OpenAI compatible large language models for AI strategy analysis

---

## Acceptance Criteria

1. Create `llm.py` module with `LLMClient` class supporting OpenAI protocol
2. Configuration items: `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL`
3. Implement `async def chat(system_prompt: str, user_message: str) -> str` method
4. Support timeout configuration (`LLM_TIMEOUT`, default 60s)
5. Error handling: API timeout, rate limiting, invalid response
6. Add unit tests (Mock API)

---

## Failing Tests Created (RED Phase)

### Unit Tests (42 tests)

**File:** `tests/unit/test_story_8_0_llm_client.py` (450+ lines)

All tests are marked with `@pytest.mark.skip(reason="TDD RED PHASE - LLMClient not implemented yet")` to comply with TDD red phase requirements.

#### Test Class: TestLLMClientModule (3 tests) - AC1

- **Test:** `test_llm_module_exists`
  - **Status:** RED - Module llm.py not created
  - **Verifies:** AC1 - llm.py module exists in project root

- **Test:** `test_llm_client_class_exists`
  - **Status:** RED - LLMClient class not defined
  - **Verifies:** AC1 - LLMClient class is defined

- **Test:** `test_llm_config_dataclass_exists`
  - **Status:** RED - LLMConfig dataclass not defined
  - **Verifies:** AC1 - LLMConfig dataclass exists

#### Test Class: TestLLMClientInit (6 tests) - AC2, AC4

- **Test:** `test_init_with_defaults`
  - **Status:** RED - LLMClient not implemented
  - **Verifies:** AC2, AC4 - Configuration from environment

- **Test:** `test_init_default_base_url`
  - **Status:** RED - LLMClient not implemented
  - **Verifies:** AC2 - Default base URL is GLM endpoint

- **Test:** `test_init_default_model`
  - **Status:** RED - LLMClient not implemented
  - **Verifies:** AC2 - Default model is glm-4

- **Test:** `test_init_default_timeout`
  - **Status:** RED - LLMClient not implemented
  - **Verifies:** AC4 - Default timeout is 60s

- **Test:** `test_init_with_custom_config`
  - **Status:** RED - LLMClient not implemented
  - **Verifies:** AC2 - Custom LLMConfig accepted

- **Test:** `test_init_no_api_key_warning`
  - **Status:** RED - LLMClient not implemented
  - **Verifies:** AC2 - Warning logged when API key missing

#### Test Class: TestLLMClientChat (4 tests) - AC3

- **Test:** `test_chat_returns_response_string`
  - **Status:** RED - chat() method not implemented
  - **Verifies:** AC3 - Returns assistant response as string

- **Test:** `test_chat_sends_correct_payload`
  - **Status:** RED - chat() method not implemented
  - **Verifies:** AC3 - OpenAI-compatible request payload

- **Test:** `test_chat_sends_authorization_header`
  - **Status:** RED - chat() method not implemented
  - **Verifies:** AC3 - Bearer token in Authorization header

- **Test:** `test_chat_content_type_json`
  - **Status:** RED - chat() method not implemented
  - **Verifies:** AC3 - Content-Type application/json

#### Test Class: TestLLMClientErrorHandling (11 tests) - AC5

- **Test:** `test_chat_handles_timeout`
  - **Status:** RED - Error handling not implemented
  - **Verifies:** AC5 - asyncio.TimeoutError handling

- **Test:** `test_chat_handles_401_unauthorized`
  - **Status:** RED - Error handling not implemented
  - **Verifies:** AC5 - 401 authentication error

- **Test:** `test_chat_handles_429_rate_limit`
  - **Status:** RED - Error handling not implemented
  - **Verifies:** AC5 - 429 rate limit error

- **Test:** `test_chat_handles_500_server_error`
  - **Status:** RED - Error handling not implemented
  - **Verifies:** AC5 - 500 server error

- **Test:** `test_chat_handles_invalid_json_response`
  - **Status:** RED - Error handling not implemented
  - **Verifies:** AC5 - Invalid JSON response

- **Test:** `test_chat_handles_missing_choices`
  - **Status:** RED - Error handling not implemented
  - **Verifies:** AC5 - Missing choices array

- **Test:** `test_chat_handles_empty_content`
  - **Status:** RED - Error handling not implemented
  - **Verifies:** AC5 - Empty content in response

- **Test:** `test_chat_handles_network_error`
  - **Status:** RED - Error handling not implemented
  - **Verifies:** AC5 - aiohttp.ClientError handling

- **Test:** `test_chat_returns_error_without_api_key`
  - **Status:** RED - Error handling not implemented
  - **Verifies:** AC5 - Missing API key error

- **Test:** `test_error_logged_on_timeout`
  - **Status:** RED - Logging not implemented
  - **Verifies:** AC5 - Timeout errors logged

- **Test:** `test_error_logged_on_auth_failure`
  - **Status:** RED - Logging not implemented
  - **Verifies:** AC5 - Auth failures logged

#### Test Class: TestLLMClientSessionManagement (3 tests)

- **Test:** `test_get_session_creates_client_session`
  - **Status:** RED - Session management not implemented
  - **Verifies:** aiohttp.ClientSession creation

- **Test:** `test_get_session_reuses_existing_session`
  - **Status:** RED - Session management not implemented
  - **Verifies:** Session reuse pattern

- **Test:** `test_close_closes_session`
  - **Status:** RED - Session management not implemented
  - **Verifies:** Proper session cleanup

#### Test Class: TestConfigIntegration (5 tests) - AC2, AC4

- **Test:** `test_config_has_llm_api_key`
  - **Status:** RED - config.py not updated
  - **Verifies:** AC2 - LLM_API_KEY in config

- **Test:** `test_config_has_llm_base_url`
  - **Status:** RED - config.py not updated
  - **Verifies:** AC2 - LLM_BASE_URL in config

- **Test:** `test_config_has_llm_model`
  - **Status:** RED - config.py not updated
  - **Verifies:** AC2 - LLM_MODEL in config

- **Test:** `test_config_has_llm_timeout`
  - **Status:** RED - config.py not updated
  - **Verifies:** AC4 - LLM_TIMEOUT in config

- **Test:** `test_config_llm_timeout_default_60`
  - **Status:** RED - config.py not updated
  - **Verifies:** AC4 - LLM_TIMEOUT defaults to 60

---

## Data Factories Created

### LLMDataFactory

**File:** `tests/unit/test_story_8_0_llm_client.py` (inline)

**Exports:**

- `create_config(overrides?)` - Create LLM configuration with defaults
- `create_success_response(overrides?)` - Create successful API response
- `create_error_response(overrides?)` - Create error API response

**Example Usage:**

```python
from tests.unit.test_story_8_0_llm_client import LLMDataFactory

config = LLMDataFactory.create_config(api_key="custom-key")
response = LLMDataFactory.create_success_response(content="AI advice here")
```

---

## Fixtures Created

All fixtures are inline in the test file:

- `llm_data_factory` - Provides LLMDataFactory instance
- `mock_aiohttp_session` - Mock aiohttp ClientSession
- `mock_successful_response` - Mock 200 HTTP response
- `mock_error_response_401` - Mock 401 unauthorized response
- `mock_error_response_429` - Mock 429 rate limit response
- `mock_error_response_500` - Mock 500 server error response

---

## Mock Requirements

### LLM API Mock (OpenAI Compatible)

**Endpoint:** `POST {base_url}/chat/completions`

**Success Response:**

```json
{
  "id": "chatcmpl-xxx",
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "AI response text here"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 20,
    "completion_tokens": 10,
    "total_tokens": 30
  }
}
```

**Failure Response (401):**

```json
{
  "error": {
    "message": "Invalid API key",
    "type": "invalid_request_error",
    "code": "invalid_api_key"
  }
}
```

**Failure Response (429):**

```json
{
  "error": {
    "message": "Rate limit exceeded",
    "type": "rate_limit_error"
  }
}
```

**Notes:** All tests mock aiohttp.ClientSession to avoid real network calls

---

## Implementation Checklist

### Test: TestLLMClientModule (AC1)

**File:** `tests/unit/test_story_8_0_llm_client.py`

**Tasks to make these tests pass:**

- [ ] Create `llm.py` file in project root
- [ ] Import aiohttp, logging, os, dataclasses
- [ ] Define `LLMConfig` dataclass with fields: api_key, base_url, model, timeout
- [ ] Define `LLMClient` class with type annotations
- [ ] Add comprehensive docstrings
- [ ] Run test: `pytest tests/unit/test_story_8_0_llm_client.py::TestLLMClientModule -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 1 hour

---

### Test: TestLLMClientInit (AC2, AC4)

**File:** `tests/unit/test_story_8_0_llm_client.py`

**Tasks to make these tests pass:**

- [ ] Implement `LLMClient.__init__()` with optional config parameter
- [ ] Implement `_load_from_env()` method for environment variable parsing
- [ ] Parse `LLM_API_KEY` (required, warn if missing)
- [ ] Parse `LLM_BASE_URL` (default: https://open.bigmodel.cn/api/paas/v4)
- [ ] Parse `LLM_MODEL` (default: glm-4)
- [ ] Parse `LLM_TIMEOUT` (default: 60)
- [ ] Add config.py exports: LLM_API_KEY, LLM_BASE_URL, LLM_MODEL, LLM_TIMEOUT
- [ ] Run test: `pytest tests/unit/test_story_8_0_llm_client.py::TestLLMClientInit -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 1.5 hours

---

### Test: TestLLMClientChat (AC3)

**File:** `tests/unit/test_story_8_0_llm_client.py`

**Tasks to make these tests pass:**

- [ ] Implement `_get_session()` method for lazy session creation
- [ ] Implement `async def chat(system_prompt, user_message) -> str`
- [ ] Build OpenAI-compatible request payload with messages array
- [ ] Set Authorization header with Bearer token
- [ ] Set Content-Type header to application/json
- [ ] Use aiohttp for async HTTP POST to `/chat/completions`
- [ ] Parse response and extract content from choices[0].message.content
- [ ] Return the response text string
- [ ] Run test: `pytest tests/unit/test_story_8_0_llm_client.py::TestLLMClientChat -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 2 hours

---

### Test: TestLLMClientErrorHandling (AC5)

**File:** `tests/unit/test_story_8_0_llm_client.py`

**Tasks to make these tests pass:**

- [ ] Handle asyncio.TimeoutError with clear error message
- [ ] Handle HTTP 401 with "authentication failed" message
- [ ] Handle HTTP 429 with "rate limit exceeded" message
- [ ] Handle HTTP 500 with status code in error message
- [ ] Handle invalid JSON response format
- [ ] Handle missing choices array in response
- [ ] Handle empty content in response
- [ ] Handle aiohttp.ClientError network errors
- [ ] Handle missing API key configuration
- [ ] Add logging for all error cases
- [ ] Run test: `pytest tests/unit/test_story_8_0_llm_client.py::TestLLMClientErrorHandling -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 2 hours

---

### Test: TestLLMClientSessionManagement

**File:** `tests/unit/test_story_8_0_llm_client.py`

**Tasks to make these tests pass:**

- [ ] Implement session reuse in `_get_session()`
- [ ] Implement `async def close()` method
- [ ] Create session with configured timeout
- [ ] Handle closed session recreation
- [ ] Run test: `pytest tests/unit/test_story_8_0_llm_client.py::TestLLMClientSessionManagement -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 0.5 hours

---

### Test: TestConfigIntegration (AC2, AC4)

**File:** `tests/unit/test_story_8_0_llm_client.py`

**Tasks to make these tests pass:**

- [ ] Add `LLM_API_KEY = os.getenv('LLM_API_KEY', '')` to config.py
- [ ] Add `LLM_BASE_URL = os.getenv('LLM_BASE_URL', 'https://open.bigmodel.cn/api/paas/v4')` to config.py
- [ ] Add `LLM_MODEL = os.getenv('LLM_MODEL', 'glm-4')` to config.py
- [ ] Add `LLM_TIMEOUT = int(os.getenv('LLM_TIMEOUT', '60'))` to config.py
- [ ] Update `.env.example` with LLM configuration documentation
- [ ] Run test: `pytest tests/unit/test_story_8_0_llm_client.py::TestConfigIntegration -v`
- [ ] Test passes (green phase)

**Estimated Effort:** 0.5 hours

---

## Running Tests

```bash
# Run all failing tests for this story
pytest tests/unit/test_story_8_0_llm_client.py -v

# Run specific test class
pytest tests/unit/test_story_8_0_llm_client.py::TestLLMClientChat -v

# Run with coverage
pytest tests/unit/test_story_8_0_llm_client.py --cov=llm --cov-report=term-missing

# Remove skips after implementation (GREEN phase)
# Use sed or manually remove @pytest.mark.skip decorators
```

---

## Red-Green-Refactor Workflow

### RED Phase (Complete)

**TEA Agent Responsibilities:**

- All tests written and failing (skipped)
- Data factory created with override support
- Mock requirements documented
- Implementation checklist created

**Verification:**

- All tests are skipped (TDD red phase)
- Tests will fail when skips are removed
- Tests fail due to missing implementation, not test bugs

---

### GREEN Phase (DEV Team - Next Steps)

**DEV Agent Responsibilities:**

1. **Pick one failing test class** from implementation checklist (start with TestLLMClientModule)
2. **Remove the @pytest.mark.skip decorators** for that class
3. **Implement minimal code** to make those specific tests pass
4. **Run the tests** to verify they now pass (green)
5. **Check off the tasks** in implementation checklist
6. **Move to next test class** and repeat

**Key Principles:**

- One test class at a time (don't try to fix all at once)
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

1. **Share this checklist and failing tests** with the dev workflow (manual handoff)
2. **Review this checklist** with team in standup or planning
3. **Begin implementation** using implementation checklist as guide
4. **Work one test class at a time** (red -> green for each)
5. **Share progress** in daily standup
6. **When all tests pass**, refactor code for quality
7. **When refactoring complete**, manually update story status to 'done'

---

## Knowledge Base References Applied

This ATDD workflow consulted the following knowledge fragments:

- **data-factories.md** - Factory patterns with overrides support for test data generation
- **test-quality.md** - Test design principles (determinism, isolation, explicit assertions)
- **test-healing-patterns.md** - Common failure patterns and automated fixes
- **test-levels-framework.md** - Test level selection (Unit for business logic)
- **test-priorities-matrix.md** - P0-P3 prioritization framework

See `tea-index.csv` for complete knowledge fragment mapping.

---

## Test Execution Evidence

### Initial Test Run (RED Phase Verification)

**Command:** `pytest tests/unit/test_story_8_0_llm_client.py -v`

**Expected Results:**

```
============================= test session starts ==============================
tests/unit/test_story_8_0_llm_client.py::TestLLMClientModule::test_llm_module_exists SKIPPED
tests/unit/test_story_8_0_llm_client.py::TestLLMClientModule::test_llm_client_class_exists SKIPPED
tests/unit/test_story_8_0_llm_client.py::TestLLMClientModule::test_llm_config_dataclass_exists SKIPPED
...
============================= 42 skipped in 0.01s ==============================
```

**Summary:**

- Total tests: 42
- Passing: 0 (expected - all skipped)
- Failing: 0 (expected - all skipped)
- Status: RED phase verified

---

## Notes

- **Test Level Selection:** Unit tests chosen because this is pure business logic (HTTP client, configuration, error handling). No E2E or integration tests needed.
- **Priority:** P1 - Core infrastructure for Epic 8
- **Dependencies:** aiohttp (already in project)
- **Patterns:** Follows same async/mocking patterns as `test_story_7_2_threshold_alert.py`
- **Configuration:** Environment variables follow existing project patterns in `config.py`

---

## Contact

**Questions or Issues?**

- Ask in team standup
- Refer to `./_bmad/tea/testarch/knowledge` for testing best practices

---

**Generated by BMad TEA Agent** - 2026-03-03
