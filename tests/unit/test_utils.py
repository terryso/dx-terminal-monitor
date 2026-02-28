"""
Unit tests for utility functions in main.py.
"""

import pytest

from tests.support.helpers import (
    format_eth,
    format_percent,
    format_usd,
)


class TestFormatEth:
    """Tests for format_eth function."""

    def test_format_eth_zero(self) -> None:
        """Test formatting zero wei."""
        assert format_eth("0") == "0.000000"

    def test_format_eth_one_eth(self) -> None:
        """Test formatting 1 ETH in wei."""
        assert format_eth("1000000000000000000") == "1.000000"

    def test_format_eth_fractional(self) -> None:
        """Test formatting fractional ETH."""
        assert format_eth("500000000000000000") == "0.500000"

    def test_format_eth_large_value(self) -> None:
        """Test formatting large ETH value."""
        assert format_eth("10000000000000000000") == "10.000000"

    def test_format_eth_invalid_string(self) -> None:
        """Test handling invalid input."""
        assert format_eth("invalid") == "invalid"

    def test_format_eth_empty_string(self) -> None:
        """Test handling empty input."""
        assert format_eth("") == ""


class TestFormatUsd:
    """Tests for format_usd function."""

    def test_format_usd_zero(self) -> None:
        """Test formatting zero USD."""
        assert format_usd("0") == "$0.00"

    def test_format_usd_positive(self) -> None:
        """Test formatting positive USD."""
        assert format_usd("1234.56") == "$1234.56"

    def test_format_usd_negative(self) -> None:
        """Test formatting negative USD."""
        assert format_usd("-100.50") == "$-100.50"

    def test_format_usd_integer(self) -> None:
        """Test formatting integer value."""
        assert format_usd(1000) == "$1000.00"

    def test_format_usd_invalid(self) -> None:
        """Test handling invalid input."""
        assert format_usd("invalid") == "invalid"


class TestFormatPercent:
    """Tests for format_percent function."""

    def test_format_percent_zero(self) -> None:
        """Test formatting zero percent."""
        assert format_percent("0") == "0.00%"

    def test_format_percent_positive(self) -> None:
        """Test formatting positive percent with sign."""
        assert format_percent("10.5") == "+10.50%"

    def test_format_percent_negative(self) -> None:
        """Test formatting negative percent."""
        assert format_percent("-5.25") == "-5.25%"

    def test_format_percent_integer(self) -> None:
        """Test formatting integer value."""
        assert format_percent(100) == "+100.00%"

    def test_format_percent_invalid(self) -> None:
        """Test handling invalid input."""
        assert format_percent("invalid") == "invalid"
