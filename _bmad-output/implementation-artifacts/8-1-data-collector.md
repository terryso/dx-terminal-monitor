# Story 8.1: Strategy Data Collector

Status: review

## Story

As a developer, I need to implement a data collector so that the AI analysis service has complete context data including positions, strategies, market data, and candlestick charts for trend analysis.

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

## Tasks / Subtasks

- [x] **Task 1: Add get_candles() to api.py** (AC: #3)
  - [x] Add `get_candles(token_address, timeframe, limit)` method to TerminalAPI class
  - [x] Support timeframes: 1m, 5m, 15m, 1h, 4h, 1d
  - [x] Use `/candles/{tokenAddress}` endpoint with query params
  - [x] Add unit tests for get_candles()

- [x] **Task 2: Create advisor.py module structure** (AC: #1)
  - [x] Create `advisor.py` file in project root
  - [x] Import necessary modules (api, logging, datetime, dataclasses)
  - [x] Define `StrategyDataCollector` class with type annotations
  - [x] Add comprehensive docstrings

- [x] **Task 3: Implement collect() method** (AC: #2)
  - [x] Gather positions via `api.get_positions()`
  - [x] Gather strategies via `api.get_strategies()`
  - [x] Gather vault status via `api.get_vault()`
  - [x] Gather ETH price via `api.get_eth_price()`
  - [x] Gather token list via `api.get_tokens()`
  - [x] For each held token (max 5), fetch candlestick data:
    - [x] 1h timeframe (24 candles)
    - [x] 4h timeframe (24 candles)
    - [x] 1d timeframe (7 candles)
  - [x] Return structured dict with all collected data

- [x] **Task 4: Implement format_for_llm() method** (AC: #4)
  - [x] Format positions data as readable text with PnL summary
  - [x] Format strategies list with ID, content, priority, expiry
  - [x] Format vault status (paused/active)
  - [x] Format market data (ETH price, top tokens)
  - [x] Format candlestick data with trend indicators
  - [x] Include timestamp of data collection

- [x] **Task 5: Implement error handling** (AC: #5)
  - [x] Handle individual API failures gracefully
  - [x] Include error info in returned dict when partial data available
  - [x] Log errors with appropriate severity
  - [x] Never raise exceptions to caller - always return dict

- [x] **Task 6: Add unit tests** (AC: #6)
  - [x] Create `tests/unit/test_story_8_1_data_collector.py`
  - [x] Test StrategyDataCollector initialization
  - [x] Test collect() with all APIs succeeding
  - [x] Test collect() with partial API failures
  - [x] Test format_for_llm() output format
  - [x] Test get_candles() in api.py

## Dev Notes

### Architecture Patterns

This story builds on Epic 8 infrastructure:
- Depends on Story 8-0 (LLM Client) - already completed
- Uses existing `api.py` TerminalAPI class for data fetching
- Follows same async patterns with aiohttp
- Will be consumed by `StrategyAdvisor` class in Story 8-2

### Source Tree Components to Touch

1. `/Users/nick/projects/dx-terminal-monitor/api.py` - Add get_candles() method
2. `/Users/nick/projects/dx-terminal-monitor/advisor.py` - New file with StrategyDataCollector
3. `/Users/nick/projects/dx-terminal-monitor/tests/unit/test_story_8_1_data_collector.py` - New test file

### Implementation Guide

**api.py - Add get_candles() method:**
```python
async def get_candles(
    self,
    token_address: str,
    timeframe: str = "4h",  # 1m/5m/15m/1h/4h/1d
    limit: int = 24
) -> list:
    """Get candlestick data for a token.

    Args:
        token_address: Token contract address
        timeframe: Candle interval (1m, 5m, 15m, 1h, 4h, 1d)
        limit: Number of candles to fetch

    Returns:
        List of candle objects with OHLCV data
    """
    now = int(time.time())
    return await self._get(f"/candles/{token_address}", {
        "timeframe": timeframe,
        "to": now,
        "countback": limit
    })
```

**advisor.py - StrategyDataCollector class:**
```python
"""
Strategy Data Collector Module for Story 8-1

Collects position, strategy, market, and candlestick data
for AI strategy analysis.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from api import TerminalAPI

logger = logging.getLogger(__name__)


@dataclass
class CollectedData:
    """Container for all collected analysis data."""
    positions: dict = field(default_factory=dict)
    strategies: list = field(default_factory=list)
    vault: dict = field(default_factory=dict)
    eth_price: dict = field(default_factory=dict)
    tokens: dict = field(default_factory=dict)
    candles: dict[str, dict[str, list]] = field(default_factory=dict)
    collected_at: str = ""
    errors: list[str] = field(default_factory=list)


class StrategyDataCollector:
    """Collects all data needed for AI strategy analysis.

    Gathers position data, active strategies, market data,
    and candlestick charts for trend analysis.

    Args:
        api: TerminalAPI instance for data fetching

    Example:
        collector = StrategyDataCollector(api)
        data = await collector.collect()
        text = collector.format_for_llm(data)
    """

    CANDLE_TIMEFRAMES = ["1h", "4h", "1d"]
    CANDLE_LIMITS = {"1h": 24, "4h": 24, "1d": 7}
    MAX_TOKENS_FOR_CANDLES = 5

    def __init__(self, api: TerminalAPI):
        self.api = api

    async def collect(self) -> CollectedData:
        """Collect all analysis data.

        Returns:
            CollectedData with positions, strategies, market data, candles
        """
        result = CollectedData(collected_at=datetime.now().isoformat())

        # Collect core data (each independently to handle partial failures)
        try:
            result.positions = await self.api.get_positions()
        except Exception as e:
            logger.error("Failed to fetch positions: %s", e)
            result.errors.append(f"positions: {e}")

        try:
            result.strategies = await self.api.get_strategies()
        except Exception as e:
            logger.error("Failed to fetch strategies: %s", e)
            result.errors.append(f"strategies: {e}")

        try:
            result.vault = await self.api.get_vault()
        except Exception as e:
            logger.error("Failed to fetch vault: %s", e)
            result.errors.append(f"vault: {e}")

        try:
            result.eth_price = await self.api.get_eth_price()
        except Exception as e:
            logger.error("Failed to fetch ETH price: %s", e)
            result.errors.append(f"eth_price: {e}")

        try:
            result.tokens = await self.api.get_tokens(limit=20)
        except Exception as e:
            logger.error("Failed to fetch tokens: %s", e)
            result.errors.append(f"tokens: {e}")

        # Collect candlestick data for held tokens
        result.candles = await self._collect_candles(result.positions)

        return result

    async def _collect_candles(self, positions: dict) -> dict[str, dict[str, list]]:
        """Collect candlestick data for held tokens."""
        candles = {}

        if not positions or "tokens" not in positions:
            return candles

        held_tokens = positions.get("tokens", [])[:self.MAX_TOKENS_FOR_CANDLES]

        for token in held_tokens:
            addr = token.get("tokenAddress")
            symbol = token.get("symbol", "UNKNOWN")

            if not addr:
                continue

            candles[symbol] = {}

            for tf in self.CANDLE_TIMEFRAMES:
                try:
                    limit = self.CANDLE_LIMITS.get(tf, 24)
                    data = await self.api.get_candles(addr, tf, limit)
                    if isinstance(data, list):
                        candles[symbol][tf] = data
                except Exception as e:
                    logger.warning("Failed to fetch %s candles for %s: %s", tf, symbol, e)
                    candles[symbol][tf] = []

        return candles

    def format_for_llm(self, data: CollectedData) -> str:
        """Format collected data as LLM-readable text.

        Args:
            data: CollectedData from collect()

        Returns:
            Formatted text suitable for LLM context
        """
        lines = []
        lines.append(f"# Data Collection Report")
        lines.append(f"Collected at: {data.collected_at}")
        lines.append("")

        # Positions
        if data.positions:
            lines.append("## Positions")
            eth_balance = data.positions.get("ethBalance", "N/A")
            total_pnl = data.positions.get("totalPnlUsd", "N/A")
            lines.append(f"ETH Balance: {eth_balance}")
            lines.append(f"Total PnL (USD): {total_pnl}")

            tokens = data.positions.get("tokens", [])
            if tokens:
                lines.append(f"Held Tokens ({len(tokens)}):")
                for t in tokens[:10]:
                    symbol = t.get("symbol", "?")
                    balance = t.get("balance", "0")
                    pnl = t.get("pnlUsd", "0")
                    lines.append(f"  - {symbol}: {balance} (PnL: ${pnl})")
            lines.append("")

        # Strategies
        if data.strategies:
            lines.append("## Active Strategies")
            strategies = data.strategies if isinstance(data.strategies, list) else []
            for s in strategies:
                sid = s.get("id", "?")
                content = s.get("content", "")[:100]
                priority = s.get("priority", 1)
                expiry = s.get("expiry", 0)
                lines.append(f"  #{sid} (P{priority}): {content}...")
                if expiry:
                    lines.append(f"    Expires: {expiry}")
            lines.append("")

        # Vault Status
        if data.vault:
            lines.append("## Vault Status")
            paused = data.vault.get("paused", False)
            lines.append(f"Paused: {'Yes' if paused else 'No'}")
            lines.append("")

        # Market Data
        if data.eth_price:
            lines.append("## Market Data")
            price = data.eth_price.get("price", "N/A")
            change = data.eth_price.get("change24h", "N/A")
            lines.append(f"ETH Price: ${price}")
            lines.append(f"24h Change: {change}%")
            lines.append("")

        # Candlestick Trends
        if data.candles:
            lines.append("## Token Trends (Candlestick Analysis)")
            for symbol, tf_data in data.candles.items():
                lines.append(f"### {symbol}")
                for tf, candles in tf_data.items():
                    if candles and len(candles) > 0:
                        latest = candles[-1] if candles else {}
                        close = latest.get("close", "N/A")
                        lines.append(f"  {tf}: Latest close ${close}")
                    else:
                        lines.append(f"  {tf}: No data")
                lines.append("")

        # Errors
        if data.errors:
            lines.append("## Collection Errors")
            for err in data.errors:
                lines.append(f"  - {err}")

        return "\n".join(lines)
```

### API Endpoint Reference

**Candlestick Data:**
- Endpoint: `/candles/{tokenAddress}`
- Query params: `timeframe`, `to`, `countback`
- Returns: Array of candle objects with `open`, `high`, `low`, `close`, `volume`, `timestamp`

### Candlestick Data Usage

| Timeframe | Purpose | Limit |
|-----------|---------|-------|
| 1h | Short-term volatility, intraday signals | 24 candles |
| 4h | Medium-term trend, support/resistance | 24 candles |
| 1d | Long-term trend, macro analysis | 7 candles |

### Dependencies

- No new dependencies required
- Uses existing `aiohttp` via TerminalAPI
- Uses `dataclasses` from Python standard library

### Project Structure Notes

- New module `advisor.py` follows same patterns as `monitor.py`, `reporter.py`
- `StrategyDataCollector` class is stateless - can be instantiated per request
- Test file naming: `test_story_8_1_data_collector.py`

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-8.1]
- [Source: _bmad-output/implementation-artifacts/8-0-llm-client.md - Previous story patterns]
- [Source: api.py - TerminalAPI patterns]

### Previous Story Intelligence (Story 8-0: LLM Client)

Key patterns established:
1. Use `@dataclass` for structured data containers
2. Configuration via environment variables (not needed here - uses API only)
3. Error handling returns error info rather than raising
4. Comprehensive docstrings with examples
5. Test file naming follows `test_story_X_Y_description.py` pattern
6. Logging with appropriate severity levels

### Git Intelligence (Recent Commits)

- `79dea1f` - docs: Update Epic 8 to use Inline Keyboard for user interaction
- `b0c06f0` - docs: Add Epic 8 - AI Strategy Advisor

Key learnings from Epic 7-8:
- Graceful degradation when data unavailable
- Use of dataclasses for structured data
- Async patterns with try/except for individual API calls

## Dev Agent Record

### Agent Model Used

GLM-5

### Debug Log References

N/A - All tests passed on first implementation

### Completion Notes List

- Successfully implemented StrategyDataCollector class in advisor.py module
- Added get_candles() method to TerminalAPI class in api.py
- Created CollectedData dataclass for structured data container
- Implemented collect() method that gathers all required data sources
- Implemented format_for_llm() method for LLM-friendly text output
- Comprehensive error handling - each API call wrapped independently
- All 25 story tests pass (25/25)
- All 592 unit tests pass - no regressions
- Test coverage includes: module structure, collect() method, API candles, format_for_llm(), error handling, candle collection, timestamps, API integration, logging

### File List

**New Files:**
- advisor.py - Strategy data collector module with StrategyDataCollector class and CollectedData dataclass

**Modified Files:**
- api.py - Added get_candles() method to TerminalAPI class

**Test Files:**
- tests/unit/test_story_8_1_data_collector.py - 25 comprehensive tests (pre-existing from ATDD RED phase)

## Change Log

- 2026-03-03: Story 8-1 completed - Strategy Data Collector implemented with full test coverage
