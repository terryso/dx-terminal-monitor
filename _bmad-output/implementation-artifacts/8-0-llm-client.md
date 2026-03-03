# Story 8.0: LLM Client Infrastructure

Status: review

## Story

As a developer, I need to set up LLM client infrastructure so that the system can interact with GLM5/OpenAI compatible large language models for AI strategy analysis.

## Acceptance Criteria

1. Create `llm.py` module with `LLMClient` class supporting OpenAI protocol
2. Configuration items: `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL`
3. Implement `async def chat(system_prompt: str, user_message: str) -> str` method
4. Support timeout configuration (`LLM_TIMEOUT`, default 60s)
5. Error handling: API timeout, rate limiting, invalid response
6. Add unit tests (Mock API)

## Tasks / Subtasks

- [x] **Task 1: Create llm.py module structure** (AC: #1)
  - [x] Create `llm.py` file in project root
  - [x] Import necessary modules (aiohttp, logging, os, dataclasses)
  - [x] Define `LLMClient` class with type annotations
  - [x] Add comprehensive docstrings

- [x] **Task 2: Implement LLMClient.__init__()** (AC: #2, #4)
  - [x] Parse `LLM_API_KEY` env variable (required)
  - [x] Parse `LLM_BASE_URL` env variable (default: https://open.bigmodel.cn/api/paas/v4)
  - [x] Parse `LLM_MODEL` env variable (default: glm-4)
  - [x] Parse `LLM_TIMEOUT` env variable (default: 60)
  - [x] Validate required configuration (API key must be present)

- [x] **Task 3: Implement chat() method** (AC: #3)
  - [x] Create `async def chat(system_prompt: str, user_message: str) -> str` method
  - [x] Build OpenAI-compatible request payload with messages array
  - [x] Set Authorization header with Bearer token
  - [x] Use aiohttp for async HTTP POST to `/chat/completions` endpoint
  - [x] Parse response and extract content from choices[0].message.content
  - [x] Return the response text string

- [x] **Task 4: Implement error handling** (AC: #5)
  - [x] Handle aiohttp timeout exceptions with clear error messages
  - [x] Handle HTTP error status codes (401, 429, 500, etc.)
  - [x] Handle invalid JSON response format
  - [x] Handle missing choices array in response
  - [x] Log errors appropriately with logger

- [x] **Task 5: Add environment configuration** (AC: #2, #4)
  - [x] Add `LLM_API_KEY` to `config.py`
  - [x] Add `LLM_BASE_URL` to `config.py`
  - [x] Add `LLM_MODEL` to `config.py`
  - [x] Add `LLM_TIMEOUT` to `config.py`
  - [x] Update `.env.example` with documentation

- [x] **Task 6: Add unit tests** (AC: #6)
  - [x] Create `tests/unit/test_story_8_0_llm_client.py`
  - [x] Test `LLMClient` initialization with defaults
  - [x] Test `LLMClient` initialization with custom env values
  - [x] Test `chat()` method with successful response (Mock aiohttp)
  - [x] Test `chat()` method with timeout error
  - [x] Test `chat()` method with HTTP error (401, 429, 500)
  - [x] Test `chat()` method with invalid JSON response
  - [x] Test `chat()` method with missing API key

## Dev Notes

### Architecture Patterns

This story establishes a new infrastructure layer for Epic 8 (AI Strategy Advisor):
- Similar pattern to `api.py` for async HTTP requests using aiohttp
- Follows same configuration approach via environment variables as other modules
- Uses same error handling patterns with dict return containing "error" key
- Will be consumed by `advisor.py` module in Story 8-2

### Source Tree Components to Touch

1. `/Users/nick/projects/dx-terminal-monitor/llm.py` - New file
2. `/Users/nick/projects/dx-terminal-monitor/config.py` - Add LLM configs
3. `/Users/nick/projects/dx-terminal-monitor/.env.example` - Add configuration docs
4. `/Users/nick/projects/dx-terminal-monitor/tests/unit/test_story_8_0_llm_client.py` - New test file

### Implementation Guide

**llm.py - LLMClient class:**
```python
"""
LLM Client Module for Story 8-0

Provides OpenAI-compatible API client for LLM interactions.
Supports GLM-4, OpenAI, and other compatible endpoints.
"""

import asyncio
import logging
import os
from dataclasses import dataclass
from typing import Any

import aiohttp

logger = logging.getLogger(__name__)


@dataclass
class LLMConfig:
    """Configuration for LLM client."""
    api_key: str
    base_url: str
    model: str
    timeout: int


class LLMClient:
    """OpenAI-compatible LLM client for chat completions.

    Supports GLM-4 (Zhipu AI), OpenAI, and other compatible APIs.

    Args:
        config: Optional LLMConfig instance. If not provided, reads from env.

    Example:
        client = LLMClient()
        response = await client.chat(
            system_prompt="You are a helpful assistant.",
            user_message="Hello!"
        )
    """

    def __init__(self, config: LLMConfig | None = None):
        if config:
            self.config = config
        else:
            self.config = self._load_from_env()

        self._session: aiohttp.ClientSession | None = None

    def _load_from_env(self) -> LLMConfig:
        """Load configuration from environment variables."""
        api_key = os.getenv('LLM_API_KEY', '')
        if not api_key:
            logger.warning("LLM_API_KEY not configured - LLM features will be disabled")

        return LLMConfig(
            api_key=api_key,
            base_url=os.getenv('LLM_BASE_URL', 'https://open.bigmodel.cn/api/paas/v4'),
            model=os.getenv('LLM_MODEL', 'glm-4'),
            timeout=int(os.getenv('LLM_TIMEOUT', '60'))
        )

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session

    async def close(self):
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def chat(self, system_prompt: str, user_message: str) -> str:
        """Send a chat completion request to the LLM.

        Args:
            system_prompt: System message to set the AI's behavior
            user_message: User's input message

        Returns:
            The assistant's response text, or error message string

        Example:
            response = await client.chat(
                system_prompt="You are a crypto trading advisor.",
                user_message="Should I buy ETH now?"
            )
        """
        if not self.config.api_key:
            logger.error("LLM_API_KEY not configured")
            return "Error: LLM API key not configured"

        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        }

        try:
            session = await self._get_session()
            url = f"{self.config.base_url}/chat/completions"

            async with session.post(url, headers=headers, json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    choices = data.get("choices", [])
                    if choices and len(choices) > 0:
                        message = choices[0].get("message", {})
                        content = message.get("content", "")
                        if content:
                            return content
                        else:
                            logger.error("Empty content in LLM response")
                            return "Error: Empty response from LLM"
                    else:
                        logger.error("No choices in LLM response: %s", data)
                        return "Error: Invalid LLM response format"
                elif resp.status == 401:
                    logger.error("LLM API authentication failed (401)")
                    return "Error: LLM API authentication failed"
                elif resp.status == 429:
                    logger.error("LLM API rate limit exceeded (429)")
                    return "Error: LLM API rate limit exceeded"
                else:
                    text = await resp.text()
                    logger.error("LLM API error (%d): %s", resp.status, text[:200])
                    return f"Error: LLM API returned status {resp.status}"

        except asyncio.TimeoutError:
            logger.error("LLM API request timed out after %ds", self.config.timeout)
            return f"Error: LLM request timed out after {self.config.timeout}s"
        except aiohttp.ClientError as e:
            logger.error("LLM API network error: %s", e)
            return f"Error: Network error - {e}"
        except Exception as e:
            logger.error("LLM API unexpected error: %s", e)
            return f"Error: Unexpected error - {e}"

    def __repr__(self) -> str:
        return f"LLMClient(model={self.config.model}, base_url={self.config.base_url})"
```

**config.py additions:**
```python
# LLM Configuration
LLM_API_KEY = os.getenv('LLM_API_KEY', '')
LLM_BASE_URL = os.getenv('LLM_BASE_URL', 'https://open.bigmodel.cn/api/paas/v4')
LLM_MODEL = os.getenv('LLM_MODEL', 'glm-4')
LLM_TIMEOUT = int(os.getenv('LLM_TIMEOUT', '60'))
```

**.env.example additions:**
```
# LLM Configuration (for AI Strategy Advisor - Epic 8)
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4
LLM_MODEL=glm-4
LLM_TIMEOUT=60
```

### API Endpoints Reference

| Provider | Base URL | Default Model |
|----------|----------|---------------|
| Zhipu AI (GLM) | https://open.bigmodel.cn/api/paas/v4 | glm-4 |
| OpenAI | https://api.openai.com/v1 | gpt-4 |
| DeepSeek | https://api.deepseek.com/v1 | deepseek-chat |

### Error Handling Patterns

Following established patterns from `api.py` and `contract.py`:
- Return error as string with "Error:" prefix for consistency
- Log errors with appropriate level (error for failures, warning for config issues)
- Handle timeout explicitly with asyncio.TimeoutError
- Handle HTTP status codes with specific messages

### Dependencies

No new dependencies required - `aiohttp` is already used in the project.

### Project Structure Notes

- New module `llm.py` follows same patterns as `api.py` for async HTTP
- Configuration integrated into `config.py` following existing patterns
- Test file naming: `test_story_8_0_llm_client.py`

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-8.0]
- [Source: docs/architecture.md#技术栈]
- [Source: api.py - TerminalAPI patterns for aiohttp usage]
- [Source: config.py - Environment variable patterns]

### Previous Story Intelligence (Story 7-2: Threshold Alert)

Key patterns to follow:
1. Configuration via environment variables parsed in `config.py`
2. Optional feature that gracefully degrades when not configured
3. Error handling with logging and user-friendly messages
4. Test file naming follows `test_story_X_Y_description.py` pattern
5. Use `asyncio.TimeoutError` for timeout handling
6. Lazy initialization pattern with `__init__` from env

### Git Intelligence (Recent Commits)

- `79dea1f` - docs: Update Epic 8 to use Inline Keyboard for user interaction
- `b0c06f0` - docs: Add Epic 8 - AI Strategy Advisor
- Recent Epic 7 stories established monitoring/alerting patterns

Key learnings:
- Graceful degradation when config not present (like ALERT_ENABLED)
- Integration with main.py post_init() for auto-start
- Use of TelegramNotifier for message delivery

### LLM API Protocol (OpenAI Compatible)

**Request Format:**
```json
{
  "model": "glm-4",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"}
  ]
}
```

**Response Format:**
```json
{
  "id": "chatcmpl-xxx",
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "Hello! How can I help you today?"
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

## Dev Agent Record

### Agent Model Used

GLM-5

### Debug Log References

N/A - All tests passed on first implementation

### Completion Notes List

- Successfully implemented LLMClient class with OpenAI-compatible API support
- Created comprehensive test suite with 32 tests covering all acceptance criteria
- Added configuration support to config.py with proper defaults
- Updated .env.example with LLM configuration documentation
- All 567 unit tests pass (32 new + 535 existing) - no regressions
- Error handling covers all specified scenarios: timeout, rate limiting, authentication, invalid responses
- Implementation follows established patterns from api.py (async HTTP with aiohttp)

### File List

**New Files:**
- llm.py - LLM client module with LLMClient class and LLMConfig dataclass
- tests/unit/test_story_8_0_llm_client.py - Comprehensive test suite (32 tests)

**Modified Files:**
- config.py - Added LLM configuration variables (LLM_API_KEY, LLM_BASE_URL, LLM_MODEL, LLM_TIMEOUT)
- .env.example - Added LLM configuration documentation section

## Change Log

- 2026-03-03: Story 8-0 completed - LLM Client Infrastructure implemented with full test coverage
