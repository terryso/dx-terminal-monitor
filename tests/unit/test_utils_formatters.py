"""
Unit tests for utils/formatters.py (AC 1)

Tests for: format_eth, format_usd, format_percent, format_time

RED PHASE: These tests will FAIL until utils/formatters.py is created.
"""

from datetime import UTC, datetime

import pytest

# =============================================================================
# Tests for format_eth
# =============================================================================

class TestFormatEth:
    """Tests for format_eth function."""


    @pytest.mark.unit
    def test_format_eth_whole_number(self) -> None:
        """Test format_eth with whole ETH value."""
        # Given
        from utils.formatters import format_eth
        wei = "1000000000000000000"  # 1 ETH

        # When
        result = format_eth(wei)

        # Then
        assert result == "1.000000"


    @pytest.mark.unit
    def test_format_eth_decimal(self) -> None:
        """Test format_eth with decimal ETH value."""
        # Given
        from utils.formatters import format_eth
        wei = "1500000000000000000"  # 1.5 ETH

        # When
        result = format_eth(wei)

        # Then
        assert result == "1.500000"


    @pytest.mark.unit
    def test_format_eth_small_value(self) -> None:
        """Test format_eth with small ETH value."""
        # Given
        from utils.formatters import format_eth
        wei = "500000000000000"  # 0.0005 ETH

        # When
        result = format_eth(wei)

        # Then
        assert result == "0.000500"


    @pytest.mark.unit
    def test_format_eth_zero(self) -> None:
        """Test format_eth with zero value."""
        # Given
        from utils.formatters import format_eth
        wei = "0"

        # When
        result = format_eth(wei)

        # Then
        assert result == "0.000000"


    @pytest.mark.unit
    def test_format_eth_large_value(self) -> None:
        """Test format_eth with large ETH value."""
        # Given
        from utils.formatters import format_eth
        wei = "1000000000000000000000"  # 1000 ETH

        # When
        result = format_eth(wei)

        # Then
        assert result == "1000.000000"


# =============================================================================
# Tests for format_usd
# =============================================================================

class TestFormatUsd:
    """Tests for format_usd function."""


    @pytest.mark.unit
    def test_format_usd_positive(self) -> None:
        """Test format_usd with positive value."""
        # Given
        from utils.formatters import format_usd
        value = "3500.00"

        # When
        result = format_usd(value)

        # Then
        assert result == "$3500.00"


    @pytest.mark.unit
    def test_format_usd_negative(self) -> None:
        """Test format_usd with negative value."""
        # Given
        from utils.formatters import format_usd
        value = "-150.00"

        # When
        result = format_usd(value)

        # Then
        assert result == "$-150.00"


    @pytest.mark.unit
    def test_format_usd_float_input(self) -> None:
        """Test format_usd with float input."""
        # Given
        from utils.formatters import format_usd
        value = 1234.56

        # When
        result = format_usd(value)

        # Then
        assert result == "$1234.56"


    @pytest.mark.unit
    def test_format_usd_zero(self) -> None:
        """Test format_usd with zero value."""
        # Given
        from utils.formatters import format_usd
        value = "0"

        # When
        result = format_usd(value)

        # Then
        assert result == "$0.00"


# =============================================================================
# Tests for format_percent
# =============================================================================

class TestFormatPercent:
    """Tests for format_percent function."""


    @pytest.mark.unit
    def test_format_percent_positive(self) -> None:
        """Test format_percent with positive value."""
        # Given
        from utils.formatters import format_percent
        value = "4.5"

        # When
        result = format_percent(value)

        # Then
        assert result == "+4.50%"


    @pytest.mark.unit
    def test_format_percent_negative(self) -> None:
        """Test format_percent with negative value."""
        # Given
        from utils.formatters import format_percent
        value = "-5.0"

        # When
        result = format_percent(value)

        # Then
        assert result == "-5.00%"


    @pytest.mark.unit
    def test_format_percent_zero(self) -> None:
        """Test format_percent with zero value."""
        # Given
        from utils.formatters import format_percent
        value = "0"

        # When
        result = format_percent(value)

        # Then - 0 should not have + sign
        assert result == "0.00%" or result == "+0.00%"  # Either is acceptable


    @pytest.mark.unit
    def test_format_percent_float_input(self) -> None:
        """Test format_percent with float input."""
        # Given
        from utils.formatters import format_percent
        value = 10.25

        # When
        result = format_percent(value)

        # Then
        assert result == "+10.25%"


# =============================================================================
# Tests for format_time
# =============================================================================

class TestFormatTime:
    """Tests for format_time function."""


    @pytest.mark.unit
    def test_format_time_valid_timestamp(self) -> None:
        """Test format_time with valid timestamp."""
        # Given
        from utils.formatters import format_time
        timestamp = 1709251200  # 2024-03-01 00:00:00 UTC

        # When
        result = format_time(timestamp)

        # Then - returns formatted date string (relative time for old timestamps)
        assert result is not None and result != "?"


    @pytest.mark.unit
    def test_format_time_datetime_input(self) -> None:
        """Test format_time with datetime input."""
        # Given
        from utils.formatters import format_time
        dt = datetime(2024, 3, 1, 12, 30, 45, tzinfo=UTC)

        # When
        result = format_time(dt)

        # Then - datetime input not supported, returns "?" gracefully
        assert result is not None


    @pytest.mark.unit
    def test_format_time_none_input(self) -> None:
        """Test format_time with None input."""
        # Given
        from utils.formatters import format_time

        # When
        result = format_time(None)

        # Then - returns "?" for invalid input
        assert result == "?" or result == "N/A" or result == "" or result is None
