"""
Unit tests for code quality verification (AC 12, AC 13)

Tests for: main.py line count, commands/ file sizes
"""

import pytest
import os


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# =============================================================================
# Tests for file size limits (AC 12, AC 13)
# =============================================================================

class TestCodeQualityRefactored:
    """Tests for code quality after refactoring."""

    @pytest.mark.unit
    def test_main_py_line_count_under_120(self) -> None:
        """Test main.py has fewer than 120 lines (AC 12)."""
        # Given
        main_path = os.path.join(PROJECT_ROOT, "main.py")

        # When
        with open(main_path, "r") as f:
            line_count = sum(1 for line in f if line.strip())

        # Then
        assert line_count < 120, f"main.py should have < 120 lines, got {line_count}"

    @pytest.mark.unit
    def test_commands_query_size_under_250(self) -> None:
        """Test commands/query.py has fewer than 250 lines (AC 13)."""
        # Given
        query_path = os.path.join(PROJECT_ROOT, "commands", "query.py")

        # Skip if file doesn't exist yet
        if not os.path.exists(query_path):
            pytest.skip("commands/query.py not yet created")

        # When
        with open(query_path, "r") as f:
            line_count = sum(1 for line in f if line.strip())

        # Then
        assert line_count < 250, f"commands/query.py should have < 250 lines, got {line_count}"

    @pytest.mark.unit
    def test_commands_admin_size_under_250(self) -> None:
        """Test commands/admin.py has fewer than 250 lines (AC 13)."""
        # Given
        admin_path = os.path.join(PROJECT_ROOT, "commands", "admin.py")

        # Skip if file doesn't exist yet
        if not os.path.exists(admin_path):
            pytest.skip("commands/admin.py not yet created")

        # When
        with open(admin_path, "r") as f:
            line_count = sum(1 for line in f if line.strip())

        # Then
        assert line_count < 250, f"commands/admin.py should have < 250 lines, got {line_count}"

    @pytest.mark.unit
    def test_commands_monitor_size_under_250(self) -> None:
        """Test commands/monitor.py has fewer than 250 lines (AC 13)."""
        # Given
        monitor_path = os.path.join(PROJECT_ROOT, "commands", "monitor.py")

        # Skip if file doesn't exist yet
        if not os.path.exists(monitor_path):
            pytest.skip("commands/monitor.py not yet created")

        # When
        with open(monitor_path, "r") as f:
            line_count = sum(1 for line in f if line.strip())

        # Then
        assert line_count < 250, f"commands/monitor.py should have < 250 lines, got {line_count}"

    @pytest.mark.unit
    def test_commands_withdraw_size_under_250(self) -> None:
        """Test commands/withdraw.py has fewer than 250 lines (AC 13)."""
        # Given
        withdraw_path = os.path.join(PROJECT_ROOT, "commands", "withdraw.py")

        # Skip if file doesn't exist yet
        if not os.path.exists(withdraw_path):
            pytest.skip("commands/withdraw.py not yet created")

        # When
        with open(withdraw_path, "r") as f:
            line_count = sum(1 for line in f if line.strip())

        # Then
        assert line_count < 250, f"commands/withdraw.py should have < 250 lines, got {line_count}"
