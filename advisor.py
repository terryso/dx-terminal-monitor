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
from pathlib import Path
from typing import Literal

from api import TerminalAPI
from llm import LLMClient

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
  # Constants for validation
  MAX_CONTENT_LENGTH = 1000
  MAX_REASON_LENGTH = 500
  VALID_ACTIONS = ("add", "disable")
  VALID_PRIORITIES = (0, 1, 2)

  action: Literal["add", "disable"]
  content: str | None = None
  priority: int = 1
  expiry_hours: int = 0
  strategy_id: int | None = None
  reason: str = ""

  def __post_init__(self):
    """Validate all fields with type and range checks."""
    # Validate action is exactly "add" or "disable"
    if self.action not in self.VALID_ACTIONS:
      raise ValueError(f"action must be 'add' or 'disable', got: {self.action!r}")

    # Validate priority is int in range [0, 2]
    if not isinstance(self.priority, int) or self.priority not in self.VALID_PRIORITIES:
      raise ValueError(f"priority must be int in [0, 1, 2], got: {self.priority!r}")

    # Validate expiry_hours is non-negative int
    if not isinstance(self.expiry_hours, int) or self.expiry_hours < 0:
      raise ValueError(f"expiry_hours must be non-negative int, got: {self.expiry_hours!r}")

    # Validate content length if provided
    if self.content is not None and len(self.content) > self.MAX_CONTENT_LENGTH:
      raise ValueError(f"content exceeds max length {self.MAX_CONTENT_LENGTH}")

    # Validate reason length
    if len(self.reason) > self.MAX_REASON_LENGTH:
      raise ValueError(f"reason exceeds max length {self.MAX_REASON_LENGTH}")

    # Validate action-specific required fields
    if self.action == "add" and not self.content:
      raise ValueError("content is required for 'add' action")

    if self.action == "disable":
      if self.strategy_id is None:
        raise ValueError("strategy_id is required for 'disable' action")
      if not isinstance(self.strategy_id, int) or self.strategy_id <= 0:
        raise ValueError(f"strategy_id must be positive int, got: {self.strategy_id!r}")


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
    lines.append("# Data Collection Report")
    lines.append(f"Collected at: {data.collected_at}")
    lines.append("")

    # Supported Tokens (IMPORTANT: LLM must only suggest strategies for these tokens)
    if data.tokens:
      lines.append("## Supported Tokens")
      lines.append("IMPORTANT: You can ONLY suggest strategies involving these tokens:")
      tokens_list = data.tokens if isinstance(data.tokens, list) else data.tokens.get("items", [])
      symbols = [t.get("symbol", "?") for t in tokens_list if t.get("symbol")]
      lines.append(f"  {', '.join(symbols)}")
      lines.append("")

    # Positions
    if data.positions:
      lines.append("## Positions")
      from utils.formatters import format_eth
      eth_balance_raw = data.positions.get("ethBalance", "N/A")
      eth_balance = format_eth(eth_balance_raw) if eth_balance_raw != "N/A" else "N/A"
      total_pnl = data.positions.get("overallPnlUsd", data.positions.get("totalPnlUsd", "N/A"))
      lines.append(f"ETH Balance: {eth_balance} ETH")
      lines.append(f"Total PnL (USD): {total_pnl}")

      # Support both API formats: positions/tokenSymbol and tokens/symbol
      tokens = data.positions.get("positions", data.positions.get("tokens", []))
      if tokens:
        lines.append(f"Held Tokens ({len(tokens)}):")
        for t in tokens[:10]:
          # Support both tokenSymbol (API) and symbol (test)
          symbol = t.get("tokenSymbol", t.get("symbol", "?"))
          # Support both currentValueUsd (API) and balance (test)
          val = t.get("currentValueUsd", t.get("balance", "0"))
          pnl = t.get("totalPnlUsd", t.get("pnlUsd", "0"))
          lines.append(f"  - {symbol}: ${val} (PnL: ${pnl})")
      lines.append("")

    # Strategies
    if data.strategies:
      lines.append("## Active Strategies")
      strategies = data.strategies if isinstance(data.strategies, list) else []
      current_time = int(datetime.now().timestamp())
      # Filter to only show non-expired strategies
      active_strategies = [
        s for s in strategies
        if s.get('expiry', 0) == 0 or s.get('expiry', 0) > current_time
      ]
      for s in active_strategies:
        sid = s.get("strategyId", s.get("id", "?"))
        content = s.get("content", "")
        priority = s.get("strategyPriority", s.get("priority", 1))
        expiry = s.get("expiry", 0)
        lines.append(f"  #{sid} (P{priority}): {content}")
        if expiry:
          from utils.formatters import format_time
          lines.append(f"    Expires: {format_time(expiry)}")
      if not active_strategies:
        lines.append("  (No active strategies)")
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
      price = data.eth_price.get("priceUsd", data.eth_price.get("price", "N/A"))
      change = data.eth_price.get("change24h", "N/A")
      lines.append(f"ETH Price: ${price}")
      lines.append(f"24h Change: {change}%")
      lines.append("")

    # Candlestick Trends
    if data.candles:
      lines.append("## Token Trends (Candlestick Analysis)")
      for symbol, tf_data in data.candles.items():
        lines.append(f"### {symbol}")
        for tf, candle_list in tf_data.items():
          if candle_list and len(candle_list) > 0:
            latest = candle_list[-1] if candle_list else {}
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


# Default system prompt (used as fallback if advisor_prompt.txt not found)
DEFAULT_SYSTEM_PROMPT = """You are a professional cryptocurrency trading strategy advisor.

Your role is to analyze the user's current positions, active strategies, and market data to provide actionable trading strategy recommendations.

Analyze the following data and provide your recommendations:"""

# System prompt loaded from file
PROMPT_FILE = Path(__file__).parent / "advisor_prompt.txt"


def _load_system_prompt() -> str:
  """Load system prompt from advisor_prompt.txt file."""
  try:
    return PROMPT_FILE.read_text().strip()
  except FileNotFoundError:
    logger.warning("advisor_prompt.txt not found, using default prompt")
    return DEFAULT_SYSTEM_PROMPT


SYSTEM_PROMPT = _load_system_prompt()


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
  MAX_STRATEGIES = 8  # Contract limit

  def __init__(self, llm: LLMClient, api: TerminalAPI):
    self.llm = llm
    self.api = api
    self.collector = StrategyDataCollector(api)
    self._last_record_id: str | None = None

  @property
  def last_record_id(self) -> str | None:
    return self._last_record_id

  async def analyze(self) -> list[Suggestion]:
    """Analyze current data and generate strategy suggestions.

    Returns:
        List of Suggestion objects, empty list if analysis fails
    """
    try:
      # Collect data
      data = await self.collector.collect()

      # Count current active strategies
      current_time = int(datetime.now().timestamp())
      active_strategies = [
        s for s in (data.strategies or [])
        if s.get('active', True) and (s.get('expiry', 0) == 0 or s.get('expiry', 0) > current_time)
      ]
      current_count = len(active_strategies)
      slots_available = self.MAX_STRATEGIES - current_count

      logger.info("Current active strategies: %d, slots available: %d", current_count, slots_available)

      # Format for LLM
      formatted_data = self.collector.format_for_llm(data)

      # Build full request content (for saving)
      full_request = f"{SYSTEM_PROMPT}\n\n{formatted_data}"

      # Call LLM
      response = await self.llm.chat(SYSTEM_PROMPT, formatted_data)

      # Check for error response
      if response.startswith("Error:"):
        logger.error("LLM analysis failed: %s", response)
        return []

      # Parse suggestions
      suggestions = self._parse_suggestions(response)

      # Filter suggestions to respect strategy limit
      filtered_suggestions = self._filter_by_strategy_limit(suggestions, slots_available)

      # Save analysis record (Story 8-6)
      from advisor_history import save_analysis
      record_id = save_analysis(
        request=full_request,
        response=response,
        suggestions=[s.__dict__ for s in filtered_suggestions]
      )
      self._last_record_id = record_id

      return filtered_suggestions

    except Exception as e:
      logger.error("Analysis failed: %s", e)
      return []

  def _filter_by_strategy_limit(self, suggestions: list[Suggestion], slots_available: int) -> list[Suggestion]:
    """Filter suggestions to respect max strategy limit.

    Prioritizes:
    1. All "disable" suggestions (they free up slots)
    2. "add" suggestions up to available slots

    Args:
        suggestions: List of parsed suggestions
        slots_available: Number of new strategies that can be added

    Returns:
        Filtered list of suggestions
    """
    if slots_available < 0:
      slots_available = 0

    result = []
    add_count = 0

    # First pass: include all disable suggestions
    for s in suggestions:
      if s.action == "disable":
        result.append(s)

    # Second pass: include add suggestions up to limit
    for s in suggestions:
      if s.action == "add":
        if add_count < slots_available:
          result.append(s)
          add_count += 1
        else:
          logger.info("Skipping add suggestion (no slots available): %s", s.content[:50] if s.content else "")

    # Limit to max suggestions
    return result[:self.MAX_SUGGESTIONS]

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
          # Extract and validate action
          action = item.get("action", "add")
          if not isinstance(action, str):
            action = str(action)
          action = action.lower().strip()
          if action not in Suggestion.VALID_ACTIONS:
            logger.warning("Invalid action skipped: %s", action)
            continue

          # Extract and validate priority
          priority = item.get("priority", 1)
          if isinstance(priority, str):
            priority_map = {"low": 0, "medium": 1, "high": 2}
            priority = priority_map.get(priority.lower(), 1)
          priority = int(priority) if isinstance(priority, (int, float)) else 1
          if priority not in Suggestion.VALID_PRIORITIES:
            priority = 1  # Default to medium

          # Extract and validate expiry_hours
          expiry_hours = item.get("expiry_hours", 0)
          try:
            expiry_hours = int(expiry_hours)
            if expiry_hours < 0:
              expiry_hours = 0
          except (ValueError, TypeError):
            expiry_hours = 0

          # Extract and validate strategy_id
          strategy_id = item.get("strategy_id")
          if strategy_id is not None:
            try:
              strategy_id = int(strategy_id)
              if strategy_id <= 0:
                strategy_id = None
            except (ValueError, TypeError):
              strategy_id = None

          # Extract strings
          content = item.get("content")
          if content is not None:
            content = str(content)[:Suggestion.MAX_CONTENT_LENGTH]
          reason = str(item.get("reason", ""))[:Suggestion.MAX_REASON_LENGTH]

          suggestion = Suggestion(
            action=action,
            content=content,
            priority=priority,
            expiry_hours=expiry_hours,
            strategy_id=strategy_id,
            reason=reason
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
