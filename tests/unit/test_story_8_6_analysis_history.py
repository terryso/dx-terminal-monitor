"""
Failing acceptance tests for Story 8-6: Analysis History and Web Viewer

This module contains RED phase tests that will FAIL until the feature is implemented.
Tests cover:
- AC1: Config items (ADVISOR_HISTORY_ENABLED, ADVISOR_HISTORY_MAX, ADVISOR_SURGE_DOMAIN)
- AC2: Analysis data storage (save_analysis, load_history, mark_executed)
- AC3: Static web page (data/index.html)
- AC4: Conditional sync and push (sync_to_surge, get_view_url, web link attachment)

RED Phase - All tests should fail until implementation is complete.
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture(autouse=True)
def mock_sync_to_surge():
    """Mock sync_to_surge to avoid actual surge CLI calls during tests."""
    with patch("advisor_monitor.sync_to_surge"):
        yield


# =============================================================================
# AC1: Config Tests - Tests for config.py additions
# =============================================================================

class TestAdvisorHistoryConfig:
    """Tests for ADVISOR_HISTORY_* config values in config.py."""

    def test_advisor_history_enabled_config_exists(self):
        """ADVISOR_HISTORY_ENABLED should be defined in config.py."""
        from config import ADVISOR_HISTORY_ENABLED
        assert ADVISOR_HISTORY_ENABLED is not None

    @pytest.mark.skip(reason="Default value depends on .env, not testable in isolation")
    def test_advisor_history_enabled_default_is_false(self):
        """ADVISOR_HISTORY_ENABLED should default to False."""
        from config import ADVISOR_HISTORY_ENABLED
        assert ADVISOR_HISTORY_ENABLED is False

    def test_advisor_history_enabled_can_be_overridden_by_env(self, monkeypatch):
        """ADVISOR_HISTORY_ENABLED can be overridden via environment variable."""
        monkeypatch.setenv("ADVISOR_HISTORY_ENABLED", "true")
        # Re-import to pick up new env var
        import importlib

        import config
        importlib.reload(config)
        from config import ADVISOR_HISTORY_ENABLED
        assert ADVISOR_HISTORY_ENABLED is True

    def test_advisor_history_max_config_exists(self):
        """ADVISOR_HISTORY_MAX should be defined in config.py."""
        from config import ADVISOR_HISTORY_MAX
        assert ADVISOR_HISTORY_MAX is not None

    def test_advisor_history_max_default_is_30(self):
        """ADVISOR_HISTORY_MAX should default to 30."""
        from config import ADVISOR_HISTORY_MAX
        assert ADVISOR_HISTORY_MAX == 30

    def test_advisor_history_max_can_be_overridden_by_env(self, monkeypatch):
        """ADVISOR_HISTORY_MAX can be overridden via environment variable."""
        monkeypatch.setenv("ADVISOR_HISTORY_MAX", "50")
        import importlib

        import config
        importlib.reload(config)
        from config import ADVISOR_HISTORY_MAX
        assert ADVISOR_HISTORY_MAX == 50

    def test_advisor_surge_domain_config_exists(self):
        """ADVISOR_SURGE_DOMAIN should be defined in config.py."""
        from config import ADVISOR_SURGE_DOMAIN
        assert ADVISOR_SURGE_DOMAIN is not None

    def test_advisor_surge_domain_default_is_dx_advisor_surge_sh(self):
        """ADVISOR_SURGE_DOMAIN should default to dx-advisor.surge.sh."""
        from config import ADVISOR_SURGE_DOMAIN
        assert ADVISOR_SURGE_DOMAIN == "dx-advisor.surge.sh"

    def test_advisor_surge_domain_can_be_overridden_by_env(self, monkeypatch):
        """ADVISOR_SURGE_DOMAIN can be overridden via environment variable."""
        monkeypatch.setenv("ADVISOR_SURGE_DOMAIN", "custom-domain.surge.sh")
        import importlib

        import config
        importlib.reload(config)
        from config import ADVISOR_SURGE_DOMAIN
        assert ADVISOR_SURGE_DOMAIN == "custom-domain.surge.sh"


# =============================================================================
# AC2: Analysis Data Storage Tests - Tests for advisor_history.py module
# =============================================================================

class TestAdvisorHistoryStorage:
    """Tests for advisor_history.py module functions."""

    def test_advisor_history_module_exists(self):
        """advisor_history module should exist and be importable."""
        from advisor_history import (
            get_view_url,
            load_history,
            mark_executed,
            save_analysis,
            sync_to_surge,
        )
        assert callable(save_analysis)
        assert callable(load_history)
        assert callable(mark_executed)
        assert callable(sync_to_surge)
        assert callable(get_view_url)

    def test_save_analysis_creates_record_with_correct_structure(self, tmp_path, monkeypatch):
        """save_analysis should create a record with all required fields."""
        history_file = tmp_path / "advisor_history.json"
        monkeypatch.setattr("advisor_history.HISTORY_FILE", history_file)

        from advisor_history import load_history, save_analysis

        suggestions = [{"action": "add", "content": "test strategy", "priority": 1}]
        record_id = save_analysis(
            request="Full system prompt\n\nUser data here",
            response='{"suggestions": [...]}',
            suggestions=suggestions
        )

        assert record_id is not None
        assert len(record_id) == 8  # 8-character hex ID

        history = load_history()
        assert len(history) == 1
        record = history[0]
        assert record["id"] == record_id
        assert "timestamp" in record
        assert record["request"] == "Full system prompt\n\nUser data here"
        assert record["response"] == '{"suggestions": [...]}'
        assert record["suggestions"] == suggestions
        assert record["executed"] is False
        assert record["executed_at"] is None

    def test_save_analysis_inserts_newest_first(self, tmp_path, monkeypatch):
        """New records should be inserted at the beginning of the history list."""
        history_file = tmp_path / "advisor_history.json"
        monkeypatch.setattr("advisor_history.HISTORY_FILE", history_file)

        from advisor_history import load_history, save_analysis

        id1 = save_analysis("prompt 1", "response 1", [])
        id2 = save_analysis("prompt 2", "response 2", [])

        history = load_history()
        assert len(history) == 2
        assert history[0]["id"] == id2  # Newest first
        assert history[1]["id"] == id1

    def test_save_analysis_respects_max_records_limit(self, tmp_path, monkeypatch):
        """History should be trimmed to ADVISOR_HISTORY_MAX records."""
        history_file = tmp_path / "advisor_history.json"
        monkeypatch.setattr("advisor_history.HISTORY_FILE", history_file)
        monkeypatch.setattr("advisor_history.ADVISOR_HISTORY_MAX", 5)

        from advisor_history import load_history, save_analysis

        # Save 8 records (more than max of 5)
        for i in range(8):
            save_analysis(f"prompt {i}", f"response {i}", [])

        history = load_history()
        assert len(history) == 5  # Should be trimmed to max
        # Most recent should be present (prompt 7)
        assert "prompt 7" in history[0]["request"]
        # Oldest should be removed (prompt 0, 1, 2 should be gone)
        assert "prompt 0" not in [r["request"] for r in history]

    def test_load_history_returns_empty_list_when_file_not_exists(self, tmp_path, monkeypatch):
        """load_history should return empty list if file doesn't exist."""
        history_file = tmp_path / "nonexistent.json"
        monkeypatch.setattr("advisor_history.HISTORY_FILE", history_file)

        from advisor_history import load_history

        history = load_history()
        assert history == []

    def test_load_history_handles_corrupt_json_gracefully(self, tmp_path, monkeypatch):
        """load_history should return empty list on corrupt JSON."""
        history_file = tmp_path / "advisor_history.json"
        history_file.write_text("not valid json {{{")
        monkeypatch.setattr("advisor_history.HISTORY_FILE", history_file)

        from advisor_history import load_history

        history = load_history()
        assert history == []

    def test_mark_executed_updates_record_status(self, tmp_path, monkeypatch):
        """mark_executed should set executed=True and executed_at timestamp."""
        history_file = tmp_path / "advisor_history.json"
        monkeypatch.setattr("advisor_history.HISTORY_FILE", history_file)

        from advisor_history import load_history, mark_executed, save_analysis

        record_id = save_analysis("test prompt", "test response", [])

        # Mark as executed
        mark_executed(record_id)

        history = load_history()
        record = next((r for r in history if r["id"] == record_id), None)
        assert record is not None
        assert record["executed"] is True
        assert record["executed_at"] is not None

    def test_mark_executed_does_nothing_for_nonexistent_id(self, tmp_path, monkeypatch):
        """mark_executed should handle non-existent record ID gracefully."""
        history_file = tmp_path / "advisor_history.json"
        monkeypatch.setattr("advisor_history.HISTORY_FILE", history_file)

        from advisor_history import load_history, mark_executed, save_analysis

        save_analysis("test", "test", [])

        # Try to mark non-existent ID
        mark_executed("nonexistent")

        # Should not raise exception, history should still contain 1 record
        history = load_history()
        assert len(history) == 1


# =============================================================================
# AC3: Static Web Page Tests
# =============================================================================

class TestAdvisorWebPage:
    """Tests for data/index.html static web page."""

    def test_web_directory_exists(self):
        """data directory should exist."""
        web_dir = Path("data")
        assert web_dir.exists()
        assert web_dir.is_dir()

    def test_index_html_exists(self):
        """data/index.html should exist."""
        index_file = Path("data/index.html")
        assert index_file.exists()
        assert index_file.is_file()

    def test_index_html_contains_title(self):
        """index.html should contain proper title."""
        index_file = Path("data/index.html")
        content = index_file.read_text()
        assert "<title>" in content
        assert "AI Advisor" in content or "Analysis History" in content

    def test_index_html_loads_advisor_history_json(self):
        """index.html should load advisor_history.json via JavaScript."""
        index_file = Path("data/index.html")
        content = index_file.read_text()
        assert "advisor_history.json" in content
        assert "fetch" in content.lower()

    def test_index_html_has_responsive_meta(self):
        """index.html should have responsive viewport meta tag."""
        index_file = Path("data/index.html")
        content = index_file.read_text()
        assert "viewport" in content.lower()
        assert "width=device-width" in content.lower()


# =============================================================================
# AC4: Sync and Push Tests - Tests for sync_to_surge and web link
# =============================================================================

class TestSyncToSurge:
    """Tests for sync_to_surge function."""

    def test_sync_to_surge_handles_missing_surge_cli(self, tmp_path, monkeypatch):
        """sync_to_surge should handle FileNotFoundError gracefully."""
        web_dir = tmp_path / "data"
        web_dir.mkdir()
        history_file = web_dir / "advisor_history.json"
        history_file.write_text("[]")

        monkeypatch.setattr("advisor_history.WEB_DIR", web_dir)
        monkeypatch.setattr("advisor_history.HISTORY_FILE", history_file)

        from advisor_history import sync_to_surge

        # Should not raise exception when surge CLI not found
        with patch("subprocess.run", side_effect=FileNotFoundError("surge not found")):
            sync_to_surge()  # Should complete without error

    def test_sync_to_surge_handles_timeout(self, tmp_path, monkeypatch):
        """sync_to_surge should handle subprocess timeout gracefully."""
        web_dir = tmp_path / "data"
        web_dir.mkdir()
        history_file = web_dir / "advisor_history.json"
        history_file.write_text("[]")

        monkeypatch.setattr("advisor_history.WEB_DIR", web_dir)
        monkeypatch.setattr("advisor_history.HISTORY_FILE", history_file)

        from advisor_history import sync_to_surge

        # Should not raise exception on timeout
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="surge", timeout=60)):
            sync_to_surge()  # Should complete without error


class TestGetViewUrl:
    """Tests for get_view_url function."""

    def test_get_view_url_returns_correct_format(self, monkeypatch):
        """get_view_url should return URL with ADVISOR_SURGE_DOMAIN."""
        monkeypatch.setattr("advisor_history.ADVISOR_SURGE_DOMAIN", "test-domain.surge.sh")

        from advisor_history import get_view_url

        url = get_view_url()
        assert url == "https://test-domain.surge.sh"

    def test_get_view_url_uses_config_domain(self, monkeypatch):
        """get_view_url should use ADVISOR_SURGE_DOMAIN from config."""
        monkeypatch.setattr("advisor_history.ADVISOR_SURGE_DOMAIN", "custom.surge.sh")

        from advisor_history import get_view_url

        assert get_view_url() == "https://custom.surge.sh"


class TestAdvisorMonitorIntegration:
    """Tests for advisor_monitor.py integration with history."""

    def test_push_suggestions_includes_web_link_when_enabled(self, monkeypatch):
        """push_suggestions should include web link when ADVISOR_HISTORY_ENABLED is True."""
        # Mock both config references (same pattern as disabled test)
        monkeypatch.setattr("config.ADVISOR_HISTORY_ENABLED", True)
        monkeypatch.setattr("advisor_monitor.config.ADVISOR_HISTORY_ENABLED", True)

        from advisor_history import get_view_url
        from advisor_monitor import push_suggestions

        # Mock bot
        mock_bot = AsyncMock()

        # Capture the message sent
        sent_messages = []
        async def mock_send(chat_id, text, **kwargs):
            sent_messages.append({"chat_id": chat_id, "text": text})

        mock_bot.send_message = mock_send

        # Mock sync_to_surge
        with patch("advisor_monitor.sync_to_surge"):
            import asyncio
            asyncio.run(push_suggestions(
                chat_id=123456,
                suggestions=[{"action": "add", "content": "test", "reason": "test reason"}],
                context={"balance": "1.0 ETH", "positions": 1, "strategies": 0, "pnl": "$100"},
                bot=mock_bot
            ))

        assert len(sent_messages) == 1
        message_text = sent_messages[0]["text"]
        assert "查看详细分析历史" in message_text or get_view_url() in message_text

    def test_push_suggestions_excludes_web_link_when_disabled(self, monkeypatch):
        """push_suggestions should NOT include web link when ADVISOR_HISTORY_ENABLED is False."""
        # Mock both config references
        monkeypatch.setattr("config.ADVISOR_HISTORY_ENABLED", False)
        monkeypatch.setattr("advisor_monitor.config.ADVISOR_HISTORY_ENABLED", False)

        from advisor_monitor import push_suggestions

        # Mock bot
        mock_bot = AsyncMock()
        sent_messages = []
        async def mock_send(chat_id, text, **kwargs):
            sent_messages.append({"text": text})

        mock_bot.send_message = mock_send

        import asyncio
        asyncio.run(push_suggestions(
            chat_id=123456,
            suggestions=[{"action": "add", "content": "test", "reason": "test"}],
            context={"balance": "1.0 ETH", "positions": 1, "strategies": 0, "pnl": "$100"},
            bot=mock_bot
        ))

        message_text = sent_messages[0]["text"]
        assert "查看详细分析历史" not in message_text
        assert "surge.sh" not in message_text


class TestAdvisorAnalyzeIntegration:
    """Tests for advisor.py integration with save_analysis."""

    def test_analyze_saves_history_record(self, monkeypatch):
        """StrategyAdvisor.analyze should save analysis record via save_analysis."""
        # Mock the LLM and API
        mock_llm = AsyncMock()
        mock_api = AsyncMock()

        # Mock data collection
        mock_api.get_positions = AsyncMock(return_value={"ethBalance": "1000000000000000000"})
        mock_api.get_strategies = AsyncMock(return_value=[])
        mock_api.get_vault = AsyncMock(return_value={})
        mock_api.get_eth_price = AsyncMock(return_value={"price": "3000"})
        mock_api.get_tokens = AsyncMock(return_value=[])
        mock_api.get_candles = AsyncMock(return_value=[])

        # Mock LLM response
        mock_llm.chat = AsyncMock(return_value='{"suggestions": []}')

        # Track save_analysis calls
        save_analysis_calls = []
        def mock_save_analysis(request, response, suggestions):
            save_analysis_calls.append({
                "request": request,
                "response": response,
                "suggestions": suggestions
            })
            return "abc12345"

        monkeypatch.setattr("advisor_history.save_analysis", mock_save_analysis)

        import asyncio

        from advisor import StrategyAdvisor

        advisor = StrategyAdvisor(mock_llm, mock_api)
        result = asyncio.run(advisor.analyze())

        # Verify save_analysis was called
        assert len(save_analysis_calls) == 1
        call = save_analysis_calls[0]
        assert "request" in call
        assert "response" in call
        assert "suggestions" in call

    def test_analyze_stores_last_record_id(self, monkeypatch):
        """StrategyAdvisor should store last_record_id after analysis."""
        mock_llm = AsyncMock()
        mock_api = AsyncMock()

        mock_api.get_positions = AsyncMock(return_value={"ethBalance": "1000000000000000000"})
        mock_api.get_strategies = AsyncMock(return_value=[])
        mock_api.get_vault = AsyncMock(return_value={})
        mock_api.get_eth_price = AsyncMock(return_value={"price": "3000"})
        mock_api.get_tokens = AsyncMock(return_value=[])
        mock_api.get_candles = AsyncMock(return_value=[])

        mock_llm.chat = AsyncMock(return_value='{"suggestions": []}')

        monkeypatch.setattr("advisor_history.save_analysis", lambda *args, **kwargs: "testid12")

        import asyncio

        from advisor import StrategyAdvisor

        advisor = StrategyAdvisor(mock_llm, mock_api)
        asyncio.run(advisor.analyze())

        assert advisor.last_record_id == "testid12"
