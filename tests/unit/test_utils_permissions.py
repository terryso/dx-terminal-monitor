"""
Unit tests for utils/permissions.py (AC 2)

Tests for: authorized function

RED PHASE: These tests will FAIL until utils/permissions.py is created.
"""

from unittest.mock import MagicMock, patch

import pytest

# =============================================================================
# Tests for authorized function
# =============================================================================


class TestAuthorized:
    """Tests for authorized function."""

    @pytest.mark.unit
    def test_authorized_user_in_allowed_list(self) -> None:
        """Test authorized returns True when user is in ALLOWED_USERS."""
        # Given
        from utils.permissions import authorized

        update = MagicMock()
        update.effective_user.id = 123456789

        with patch("utils.permissions.ALLOWED_USERS", [123456789, 987654321]):
            # When
            result = authorized(update)

        # Then
        assert result is True

    @pytest.mark.unit
    def test_authorized_user_not_in_allowed_list(self) -> None:
        """Test authorized returns False when user is not in ALLOWED_USERS."""
        # Given
        from utils.permissions import authorized

        update = MagicMock()
        update.effective_user.id = 111111111

        with patch("utils.permissions.ALLOWED_USERS", [123456789, 987654321]):
            # When
            result = authorized(update)

        # Then
        assert result is False

    @pytest.mark.unit
    def test_authorized_empty_allowed_users(self) -> None:
        """Test authorized returns True when ALLOWED_USERS is empty."""
        # Given
        from utils.permissions import authorized

        update = MagicMock()
        update.effective_user.id = 123456789

        with patch("utils.permissions.ALLOWED_USERS", []):
            # When
            result = authorized(update)

        # Then
        assert result is True

    @pytest.mark.unit
    def test_authorized_none_allowed_users(self) -> None:
        """Test authorized returns True when ALLOWED_USERS is None."""
        # Given
        from utils.permissions import authorized

        update = MagicMock()
        update.effective_user.id = 123456789

        with patch("utils.permissions.ALLOWED_USERS", None):
            # When
            result = authorized(update)

        # Then
        assert result is True

    @pytest.mark.unit
    def test_authorized_single_user_list(self) -> None:
        """Test authorized with single user in ALLOWED_USERS."""
        # Given
        from utils.permissions import authorized

        update = MagicMock()
        update.effective_user.id = 123456789

        with patch("utils.permissions.ALLOWED_USERS", [123456789]):
            # When
            result = authorized(update)

        # Then
        assert result is True
