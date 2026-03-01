"""
Unit tests for circular import detection (AC 14)

Tests for: No circular import errors when importing main

RED PHASE: These tests will FAIL until refactoring is complete.
"""

import pytest
import sys
import importlib


# =============================================================================
# Tests for circular import detection
# =============================================================================

class TestImportCycles:
    """Tests for circular import detection."""

    
    @pytest.mark.unit
    def test_import_main_no_error(self) -> None:
        """Test that importing main does not raise circular import error."""
        # Given - Clear any cached imports
        modules_to_clear = [
            "main",
            "commands",
            "commands.query",
            "commands.admin",
            "commands.monitor",
            "commands.withdraw",
            "utils",
            "utils.formatters",
            "utils.permissions",
        ]
        for mod in modules_to_clear:
            if mod in sys.modules:
                del sys.modules[mod]

        # When/Then - Should not raise ImportError
        try:
            import main
            assert True
        except ImportError as e:
            if "circular" in str(e).lower() or "cannot import" in str(e).lower():
                pytest.fail(f"Circular import detected: {e}")
            raise

    
    @pytest.mark.unit
    def test_import_commands_query_no_error(self) -> None:
        """Test that importing commands.query does not raise circular import error."""
        # Given - Clear any cached imports
        modules_to_clear = ["commands", "commands.query", "utils", "utils.formatters"]
        for mod in modules_to_clear:
            if mod in sys.modules:
                del sys.modules[mod]

        # When/Then - Should not raise ImportError
        try:
            from commands import query
            assert True
        except ImportError as e:
            if "circular" in str(e).lower() or "cannot import" in str(e).lower():
                pytest.fail(f"Circular import detected: {e}")
            raise

    
    @pytest.mark.unit
    def test_import_commands_admin_no_error(self) -> None:
        """Test that importing commands.admin does not raise circular import error."""
        # Given - Clear any cached imports
        modules_to_clear = ["commands", "commands.admin", "utils", "utils.formatters"]
        for mod in modules_to_clear:
            if mod in sys.modules:
                del sys.modules[mod]

        # When/Then - Should not raise ImportError
        try:
            from commands import admin
            assert True
        except ImportError as e:
            if "circular" in str(e).lower() or "cannot import" in str(e).lower():
                pytest.fail(f"Circular import detected: {e}")
            raise

    
    @pytest.mark.unit
    def test_import_commands_monitor_no_error(self) -> None:
        """Test that importing commands.monitor does not raise circular import error."""
        # Given - Clear any cached imports
        modules_to_clear = ["commands", "commands.monitor"]
        for mod in modules_to_clear:
            if mod in sys.modules:
                del sys.modules[mod]

        # When/Then - Should not raise ImportError
        try:
            from commands import monitor
            assert True
        except ImportError as e:
            if "circular" in str(e).lower() or "cannot import" in str(e).lower():
                pytest.fail(f"Circular import detected: {e}")
            raise

    
    @pytest.mark.unit
    def test_import_commands_withdraw_no_error(self) -> None:
        """Test that importing commands.withdraw does not raise circular import error."""
        # Given - Clear any cached imports
        modules_to_clear = ["commands", "commands.withdraw"]
        for mod in modules_to_clear:
            if mod in sys.modules:
                del sys.modules[mod]

        # When/Then - Should not raise ImportError
        try:
            from commands import withdraw
            assert True
        except ImportError as e:
            if "circular" in str(e).lower() or "cannot import" in str(e).lower():
                pytest.fail(f"Circular import detected: {e}")
            raise

    
    @pytest.mark.unit
    def test_import_utils_no_error(self) -> None:
        """Test that importing utils does not raise circular import error."""
        # Given - Clear any cached imports
        modules_to_clear = ["utils", "utils.formatters", "utils.permissions"]
        for mod in modules_to_clear:
            if mod in sys.modules:
                del sys.modules[mod]

        # When/Then - Should not raise ImportError
        try:
            import utils
            assert True
        except ImportError as e:
            if "circular" in str(e).lower() or "cannot import" in str(e).lower():
                pytest.fail(f"Circular import detected: {e}")
            raise

    
    @pytest.mark.unit
    def test_register_handlers_available(self) -> None:
        """Test that register_handlers function is available from commands."""
        # Given - Clear any cached imports
        modules_to_clear = ["commands", "main"]
        for mod in modules_to_clear:
            if mod in sys.modules:
                del sys.modules[mod]

        # When
        from commands import register_handlers

        # Then
        assert callable(register_handlers)

    
    @pytest.mark.unit
    def test_set_monitor_instance_available(self) -> None:
        """Test that set_monitor_instance function is available from commands."""
        # Given - Clear any cached imports
        modules_to_clear = ["commands", "commands.monitor"]
        for mod in modules_to_clear:
            if mod in sys.modules:
                del sys.modules[mod]

        # When
        from commands import set_monitor_instance

        # Then
        assert callable(set_monitor_instance)
