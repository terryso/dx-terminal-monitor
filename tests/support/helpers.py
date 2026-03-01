"""
Helper utilities for testing dx-terminal-monitor.
"""

from typing import Any

# Import formatters from utils module (avoid duplication)
from utils.formatters import format_eth, format_usd, format_percent, format_time


def assert_valid_position(position: dict) -> None:
    """Assert that a position has required fields."""
    required_fields = ["tokenSymbol", "currentValueUsd", "totalPnlUsd"]
    for field in required_fields:
        assert field in position, f"Missing required field: {field}"


def assert_valid_activity(activity: dict) -> None:
    """Assert that an activity has valid structure."""
    assert "type" in activity, "Activity must have 'type' field"
    activity_type = activity["type"]
    assert activity_type in activity, f"Activity must have '{activity_type}' details"
