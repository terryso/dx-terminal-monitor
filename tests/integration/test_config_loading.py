"""
Integration tests for dx-terminal-monitor.

These tests verify the integration between components.
"""

import os
from unittest.mock import patch

import pytest


class TestConfigDefaults:
    """Tests for default configuration values in config.py."""

    def test_default_values_defined(self) -> None:
        """Test that config.py has the expected default values in code."""
        # Read config.py source to verify defaults exist
        import config
        source = open("config.py").read()

        # Verify default values are defined in the source
        assert "TELEGRAM_BOT_TOKEN" in source
        assert "VAULT_ADDRESS" in source
        assert "API_BASE_URL" in source
        # Check the default vault address
        assert "0x933aafc9C5B1e0000E1dd77ac52D67b0E4e4997C" in source
        # Check the default API URL
        assert "https://api.terminal.markets/api/v1" in source

    def test_config_module_has_required_attributes(self) -> None:
        """Test that config module exports required attributes."""
        import config

        assert hasattr(config, "TELEGRAM_BOT_TOKEN")
        assert hasattr(config, "ALLOWED_USERS")
        assert hasattr(config, "VAULT_ADDRESS")
        assert hasattr(config, "API_BASE_URL")


class TestAPIIntegration:
    """Integration tests for API module."""

    def test_api_module_structure(self) -> None:
        """Test that API module has expected structure."""
        from api import TerminalAPI

        api = TerminalAPI()

        # Check expected methods exist
        assert hasattr(api, "get_positions")
        assert hasattr(api, "get_activity")
        assert hasattr(api, "get_vault")
        assert hasattr(api, "get_swaps")
        assert hasattr(api, "get_strategies")
