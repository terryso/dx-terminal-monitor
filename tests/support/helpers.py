"""
Helper utilities for testing dx-terminal-monitor.
"""

from typing import Any


def format_eth(wei: str) -> str:
    """Convert wei to ETH string."""
    try:
        return f"{float(wei) / 1e18:.6f}"
    except (ValueError, TypeError):
        return wei


def format_usd(value: Any) -> str:
    """Format value as USD string."""
    try:
        return f"${float(value):.2f}"
    except (ValueError, TypeError):
        return str(value)


def format_percent(value: Any) -> str:
    """Format value as percentage string."""
    try:
        sign = "+" if float(value) > 0 else ""
        return f"{sign}{float(value):.2f}%"
    except (ValueError, TypeError):
        return str(value)


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
