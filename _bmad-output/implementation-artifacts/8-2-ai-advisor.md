# Story 8.2: AI Strategy Analysis Service

Status: done

## Story

As a system, I need to periodically call AI to analyze position data so that strategy suggestions can be generated for user confirmation.

## Acceptance Criteria

1. Implement `StrategyAdvisor` class in `advisor.py`
2. Implement `async def analyze() -> list[Suggestion]` method
3. Design system prompt (System Prompt):
   - Role: Professional cryptocurrency trading strategy advisor
   - Task: Analyze positions and strategies, provide add/disable recommendations
   - Output format: JSON structured data
4. Output structure `Suggestion`:
   ```python
   @dataclass
   class Suggestion:
       action: Literal["add", "disable"]  # Operation type
       # Parameters for adding strategy
       content: str | None = None         # Strategy prompt text
       priority: int = 1                  # Priority (0-2)
       expiry_hours: int = 0              # Validity period (hours), 0=permanent
       # Parameters for disabling strategy
       strategy_id: int | None = None     # Strategy ID to disable
       # Explanation
       reason: str = ""                   # Reason for recommendation
   ```
5. Scheduled task: Execute every 2 hours by default (configurable via `ADVISOR_INTERVAL_HOURS`)
6. Add unit tests (Mock LLM response)

## Tasks / Subtasks

- [ ] **Task 1: Define Suggestion dataclass** (AC: #4)
  - [ ] Add `Suggestion` dataclass to `advisor.py`
  - [ ] Define `action` field with `Literal["add", "disable"]` type
  - [ ] Define optional fields for add strategy: `content`, `priority`, `expiry_hours`
  - [ ] Define optional fields for disable strategy: `strategy_id`
  - [ ] Define `reason` field for explanation
  - [ ] Add `__post_init__` validation for action-specific required fields

- [ ] **Task 2: Implement StrategyAdvisor class** (AC: #1, #2)
  - [ ] Create `StrategyAdvisor` class in `advisor.py`
  - [ ] Accept `LLMClient` and `TerminalAPI` in constructor
  - [ ] Create `StrategyDataCollector` instance internally
  - [ ] Implement `async def analyze() -> list[Suggestion]` method

- [ ] **Task 3: Design system prompt** (AC: #3)
  - [ ] Create `SYSTEM_PROMPT` constant with advisor role definition
  - [ ] Include position data placeholder in prompt
  - [ ] Include active strategies placeholder in prompt
  - [ ] Specify JSON output format with example
  - [ ] Add guidelines for reasonable recommendations

- [ ] **Task 4: Implement analyze() method** (AC: #2)
  - [ ] Call `collector.collect()` to gather data
  - [ ] Call `collector.format_for_llm()` to format data
  - [ ] Build user message with formatted data
  - [ ] Call `llm.chat()` with system prompt and user message
  - [ ] Parse JSON response to extract suggestions
  - [ ] Return list of `Suggestion` objects

- [ ] **Task 5: Implement JSON parsing** (AC: #2, #4)
  - [ ] Create `_parse_suggestions(response: str) -> list[Suggestion]` method
  - [ ] Extract JSON from LLM response (handle markdown code blocks)
  - [ ] Parse JSON array of suggestions
  - [ ] Validate each suggestion has required fields
  - [ ] Convert to `Suggestion` dataclass instances
  - [ ] Handle JSON parse errors gracefully

- [ ] **Task 6: Add configuration** (AC: #5)
  - [ ] Add `ADVISOR_INTERVAL_HOURS` to `config.py` (default: 2)
  - [ ] Add `ADVISOR_ENABLED` to `config.py` (default: true)
  - [ ] Update `.env.example` with documentation

- [ ] **Task 7: Add unit tests** (AC: #6)
  - [ ] Create `tests/unit/test_story_8_2_ai_advisor.py`
  - [ ] Test `Suggestion` dataclass creation and validation
  - [ ] Test `StrategyAdvisor` initialization
  - [ ] Test `analyze()` with successful LLM response (Mock)
  - [ ] Test `analyze()` with add strategy suggestion
  - [ ] Test `analyze()` with disable strategy suggestion
  - [ ] Test `analyze()` with multiple suggestions
  - [ ] Test `_parse_suggestions()` with valid JSON
  - [ ] Test `_parse_suggestions()` with JSON in markdown code block
  - [ ] Test `_parse_suggestions()` with invalid JSON
  - [ ] Test `analyze()` with LLM error response
  - [ ] Test `analyze()` with data collection errors

## Dev Notes

### Architecture Patterns

This story builds on Epic 8 infrastructure:
- Depends on Story 8-0 (LLM Client) - completed
- Depends on Story 8-1 (Data Collector) - completed
- Uses `StrategyDataCollector` to gather analysis data
- Uses `LLMClient` to call AI for analysis
- Will be consumed by Story 8-3 (Suggestion Push) for user interaction

### Source Tree Components to Touch

1. `/Users/nick/projects/dx-terminal-monitor/advisor.py` - Add Suggestion dataclass and StrategyAdvisor class
2. `/Users/nick/projects/dx-terminal-monitor/config.py` - Add ADVISOR_INTERVAL_HOURS, ADVISOR_ENABLED
3. `/Users/nick/projects/dx-terminal-monitor/.env.example` - Add configuration docs
4. `/Users/nick/projects/dx-terminal-monitor/tests/unit/test_story_8_2_ai_advisor.py` - New test file

### Implementation Guide

**advisor.py - Add Suggestion dataclass and StrategyAdvisor class:**
```python
"""
Strategy Data Collector and Advisor Module for Story 8-1 and 8-2

Collects position, strategy, market, and candlestick data
for AI strategy analysis and generates suggestions.
"""

import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal

from api import TerminalAPI
from llm import LLMClient

logger = logging.getLogger(__name__)


@dataclass
class CollectedData:
    """Container for all collected analysis data."""
    # ... existing code ...


@dataclass
class Suggestion:
    """Strategy suggestion from AI analysis.

    Attributes:
        action: Type of action - "add" to add strategy, "disable" to disable
        content: Strategy prompt text (required for "add" action)
        priority: Strategy priority 0=LOW, 1=MEDIUM, 2=HIGH (default: 1)
        expiry_hours: Validity in hours, 0=permanent (default: 0)
        strategy_id: Strategy ID to disable (required for "disable" action)
        reason: Explanation for this suggestion
    """
    action: Literal["add", "disable"]
    content: str | None = None
    priority: int = 1
    expiry_hours: int = 0
    strategy_id: int | None = None
    reason: str = ""

    def __post_init__(self):
        """Validate action-specific required fields."""
        if self.action == "add" and not self.content:
            raise ValueError("content is required for 'add' action")
        if self.action == "disable" and self.strategy_id is None:
            raise ValueError("strategy_id is required for 'disable' action")


class StrategyDataCollector:
    """Collects all data needed for AI strategy analysis."""
    # ... existing code ...


# System prompt for AI strategy advisor
SYSTEM_PROMPT = """You are a professional cryptocurrency trading strategy advisor.

Your role is to analyze the user's current positions, active strategies, and market data to provide actionable trading strategy recommendations.

## Guidelines for Recommendations

1. **Be Conservative**: Only suggest strategies that have clear technical or fundamental justification
2. **Consider Risk**: Factor in current market volatility and position concentration
3. **Avoid Redundancy**: Don't suggest strategies similar to existing active ones
4. **Timeliness**: Consider time-sensitive opportunities based on candlestick trends
5. **Clear Logic**: Each suggestion must have a clear, explainable reason

## Output Format

You MUST respond with a valid JSON object in this exact format:
```json
{
  "suggestions": [
    {
      "action": "add",
      "content": "When BTC breaks 70000, sell 50% of ETH position",
      "priority": 2,
      "expiry_hours": 24,
      "reason": "BTC breaking key resistance may trigger market correction"
    },
    {
      "action": "disable",
      "strategy_id": 3,
      "reason": "Strategy condition has become invalid due to market changes"
    }
  ]
}
```

## Priority Levels
- 0 (LOW): Non-urgent, opportunistic strategies
- 1 (MEDIUM): Standard strategies (default)
- 2 (HIGH): Time-sensitive or risk-management strategies

## Important Notes
- Return empty suggestions array if no actionable recommendations
- Maximum 3 suggestions per analysis to avoid overwhelming user
- Never suggest adding more than 8 total strategies (contract limit)
- Always verify strategy_id exists before suggesting disable action

Analyze the following data and provide your recommendations:"""


class StrategyAdvisor:
    """AI-powered strategy advisor that analyzes positions and generates suggestions.

    Uses LLM to analyze current positions, strategies, and market data
    to generate actionable strategy recommendations.

    Args:
        llm: LLMClient instance for AI interactions
        api: TerminalAPI instance for data fetching

    Example:
        advisor = StrategyAdvisor(llm, api)
        suggestions = await advisor.analyze()
        for s in suggestions:
            print(f"{s.action}: {s.reason}")
    """

    MAX_SUGGESTIONS = 3

    def __init__(self, llm: LLMClient, api: TerminalAPI):
        self.llm = llm
        self.collector = StrategyDataCollector(api)

    async def analyze(self) -> list[Suggestion]:
        """Analyze current data and generate strategy suggestions.

        Returns:
            List of Suggestion objects, empty list if analysis fails
        """
        # Collect data
        data = await self.collector.collect()

        # Format for LLM
        formatted_data = self.collector.format_for_llm(data)

        # Call LLM
        response = await self.llm.chat(SYSTEM_PROMPT, formatted_data)

        # Check for error response
        if response.startswith("Error:"):
            logger.error("LLM analysis failed: %s", response)
            return []

        # Parse suggestions
        suggestions = self._parse_suggestions(response)

        # Limit to max suggestions
        return suggestions[:self.MAX_SUGGESTIONS]

    def _parse_suggestions(self, response: str) -> list[Suggestion]:
        """Parse LLM response into Suggestion objects.

        Args:
            response: Raw LLM response text

        Returns:
            List of valid Suggestion objects
        """
        suggestions = []

        # Try to extract JSON from response
        json_str = self._extract_json(response)
        if not json_str:
            logger.warning("No valid JSON found in LLM response")
            return suggestions

        try:
            data = json.loads(json_str)
            raw_suggestions = data.get("suggestions", [])

            for item in raw_suggestions:
                try:
                    suggestion = Suggestion(
                        action=item.get("action", "add"),
                        content=item.get("content"),
                        priority=item.get("priority", 1),
                        expiry_hours=item.get("expiry_hours", 0),
                        strategy_id=item.get("strategy_id"),
                        reason=item.get("reason", "")
                    )
                    suggestions.append(suggestion)
                except (ValueError, TypeError) as e:
                    logger.warning("Invalid suggestion skipped: %s", e)
                    continue

        except json.JSONDecodeError as e:
            logger.error("Failed to parse JSON: %s", e)

        return suggestions

    def _extract_json(self, text: str) -> str | None:
        """Extract JSON from text, handling markdown code blocks.

        Args:
            text: Text that may contain JSON

        Returns:
            Extracted JSON string or None
        """
        # Try to find JSON in markdown code block first
        code_block_pattern = r'```(?:json)?\s*([\s\S]*?)```'
        match = re.search(code_block_pattern, text)
        if match:
            return match.group(1).strip()

        # Try to find raw JSON object
        json_pattern = r'\{[\s\S]*"suggestions"[\s\S]*\}'
        match = re.search(json_pattern, text)
        if match:
            return match.group(0)

        return None
```

**config.py additions:**
```python
# Advisor Configuration
ADVISOR_ENABLED = os.getenv('ADVISOR_ENABLED', 'true').lower() == 'true'
ADVISOR_INTERVAL_HOURS = int(os.getenv('ADVISOR_INTERVAL_HOURS', '2'))
```

**.env.example additions:**
```
# AI Strategy Advisor Configuration (Epic 8)
ADVISOR_ENABLED=true
ADVISOR_INTERVAL_HOURS=2
```

### System Prompt Design Rationale

The system prompt is designed to:
1. **Establish Role**: Professional crypto trading advisor
2. **Set Boundaries**: Conservative, risk-aware recommendations
3. **Ensure Format**: Strict JSON output for reliable parsing
4. **Provide Context**: Priority levels, max suggestions, contract limits
5. **Handle Edge Cases**: Empty suggestions when no action needed

### Suggestion Data Flow

```
1. StrategyAdvisor.analyze() called
2. StrategyDataCollector.collect() gathers:
   - positions (ETH balance, token holdings, PnL)
   - strategies (active strategies with IDs, content, priority)
   - vault status (paused/active)
   - market data (ETH price, token list)
   - candles (1h/4h/1d trends for held tokens)
3. format_for_llm() creates human-readable text
4. LLMClient.chat() sends to AI with system prompt
5. AI returns JSON with suggestions
6. _parse_suggestions() extracts and validates
7. Returns list of Suggestion objects
```

### Dependencies

- No new dependencies required
- Uses existing `aiohttp` via LLMClient
- Uses `dataclasses` from Python standard library
- Uses `json` and `re` from Python standard library

### Project Structure Notes

- Extends existing `advisor.py` module (from Story 8-1)
- Adds `Suggestion` dataclass and `StrategyAdvisor` class
- Test file naming: `test_story_8_2_ai_advisor.py`
- Follows same patterns as Story 8-0 and 8-1

### Error Handling Patterns

Following established patterns from Story 8-0 and 8-1:
- Return empty list on LLM errors (graceful degradation)
- Log errors with appropriate severity
- Handle JSON parse errors without crashing
- Validate suggestion data before creating Suggestion objects
- Skip invalid suggestions rather than failing entire batch

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-8.2]
- [Source: _bmad-output/implementation-artifacts/8-0-llm-client.md - LLM Client patterns]
- [Source: _bmad-output/implementation-artifacts/8-1-data-collector.md - Data Collector patterns]
- [Source: advisor.py - Existing StrategyDataCollector class]
- [Source: llm.py - LLMClient.chat() method]

### Previous Story Intelligence (Story 8-1: Data Collector)

Key patterns to follow:
1. Use `@dataclass` for structured data containers with validation
2. Comprehensive error handling - each operation wrapped independently
3. Logging with appropriate severity levels
4. Return empty/error values rather than raising exceptions
5. Test file naming follows `test_story_X_Y_description.py` pattern
6. Async methods with proper type annotations

### Previous Story Intelligence (Story 8-0: LLM Client)

Key patterns established:
1. Configuration via environment variables
2. Error handling returns error string with "Error:" prefix
3. Graceful degradation when not configured
4. Comprehensive docstrings with examples
5. Mock API responses in unit tests

### Git Intelligence (Recent Commits)

- `6964ec2` - feat: Add LLM Client infrastructure (Story 8-0)
- `79dea1f` - docs: Update Epic 8 to use Inline Keyboard for user interaction
- `b0c06f0` - docs: Add Epic 8 - AI Strategy Advisor

Key learnings from Epic 8 stories:
- Use dataclasses for structured data
- Handle LLM responses with JSON extraction
- Graceful error handling throughout
- Comprehensive test coverage

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List
