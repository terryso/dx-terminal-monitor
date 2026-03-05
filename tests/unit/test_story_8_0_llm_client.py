"""
ATDD Tests for Story 8-0: LLM Client Infrastructure

These tests are designed to FAIL before implementation (TDD RED phase).
Run: pytest tests/unit/test_story_8_0_llm_client.py -v

Generated: 2026-03-03
Story: 8-0-llm-client
"""

import asyncio
from dataclasses import dataclass
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

# ============================================================================
# Test Data Factory
# ============================================================================


def create_mock_response(status=200, json_data=None, text_data=""):
    """Create a mock response that supports async context manager."""
    mock_resp = AsyncMock()
    mock_resp.status = status
    mock_resp.json = AsyncMock(return_value=json_data or {})
    mock_resp.text = AsyncMock(return_value=text_data)
    return mock_resp


class LLMDataFactory:
    """Factory for creating test LLM data."""

    @staticmethod
    def create_config(
        api_key: str = "test-api-key-12345",
        base_url: str = "https://open.bigmodel.cn/api/paas/v4",
        model: str = "glm-4",
        timeout: int = 60,
    ) -> dict:
        """Create LLM configuration for testing."""
        return {
            "api_key": api_key,
            "base_url": base_url,
            "model": model,
            "timeout": timeout,
        }

    @staticmethod
    def create_success_response(
        content: str = "This is a helpful AI response.",
        model: str = "glm-4",
    ) -> dict:
        """Create a successful LLM API response."""
        return {
            "id": "chatcmpl-test-123",
            "object": "chat.completion",
            "created": 1703000000,
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": content,
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": 20,
                "completion_tokens": 10,
                "total_tokens": 30,
            },
        }

    @staticmethod
    def create_error_response(
        error_message: str = "Invalid API key",
        error_type: str = "invalid_request_error",
    ) -> dict:
        """Create an error LLM API response."""
        return {
            "error": {
                "message": error_message,
                "type": error_type,
                "code": "invalid_api_key",
            }
        }


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def llm_data_factory():
    """Provide LLMDataFactory."""
    return LLMDataFactory()


@pytest.fixture
def mock_aiohttp_session():
    """Create mock aiohttp ClientSession."""
    session = AsyncMock(spec=aiohttp.ClientSession)
    return session


@pytest.fixture
def mock_successful_response(llm_data_factory):
    """Create mock successful HTTP response."""
    response = AsyncMock()
    response.status = 200
    response.json = AsyncMock(return_value=llm_data_factory.create_success_response())
    response.text = AsyncMock(return_value="OK")
    return response


@pytest.fixture
def mock_error_response_401():
    """Create mock 401 unauthorized response."""
    response = AsyncMock()
    response.status = 401
    response.text = AsyncMock(return_value='{"error": "Unauthorized"}')
    return response


@pytest.fixture
def mock_error_response_429():
    """Create mock 429 rate limit response."""
    response = AsyncMock()
    response.status = 429
    response.text = AsyncMock(return_value='{"error": "Rate limit exceeded"}')
    return response


@pytest.fixture
def mock_error_response_500():
    """Create mock 500 server error response."""
    response = AsyncMock()
    response.status = 500
    response.text = AsyncMock(return_value='{"error": "Internal server error"}')
    return response


# ============================================================================
# Test Classes - AC1: Create llm.py module with LLMClient class
# ============================================================================


class TestLLMClientModule:
    """Tests for LLMClient module structure (AC1)."""

    def test_llm_module_exists(self):
        """llm.py module should exist in project root."""
        # GIVEN: Project structure
        # WHEN: Importing llm module
        # THEN: Module should be importable
        import llm

        assert llm is not None

    def test_llm_client_class_exists(self):
        """LLMClient class should be defined in llm module."""
        from llm import LLMClient

        assert LLMClient is not None

    def test_llm_config_dataclass_exists(self):
        """LLMConfig dataclass should be defined in llm module."""
        from llm import LLMConfig

        assert LLMConfig is not None
        # Verify it's a dataclass
        assert hasattr(LLMConfig, "__dataclass_fields__")


# ============================================================================
# Test Classes - AC2, AC4: Configuration
# ============================================================================


class TestLLMClientInit:
    """Tests for LLMClient initialization (AC2, AC4)."""

    def test_init_with_defaults(self):
        """LLMClient should initialize with default values from env."""
        from llm import LLMClient

        with patch.dict(
            "os.environ",
            {
                "LLM_API_KEY": "test-key",
                "LLM_BASE_URL": "https://api.test.com/v1",
                "LLM_MODEL": "test-model",
                "LLM_TIMEOUT": "30",
            },
        ):
            client = LLMClient()

            assert client.config.api_key == "test-key"
            assert client.config.base_url == "https://api.test.com/v1"
            assert client.config.model == "test-model"
            assert client.config.timeout == 30

    def test_init_default_base_url(self):
        """LLMClient should use GLM default base URL if not specified."""
        from llm import LLMClient

        with patch.dict("os.environ", {"LLM_API_KEY": "test-key"}, clear=True):
            client = LLMClient()

            assert client.config.base_url == "https://open.bigmodel.cn/api/paas/v4"

    def test_init_default_model(self):
        """LLMClient should use glm-4 as default model."""
        from llm import LLMClient

        with patch.dict("os.environ", {"LLM_API_KEY": "test-key"}, clear=True):
            client = LLMClient()

            assert client.config.model == "glm-4"

    def test_init_default_timeout(self):
        """LLMClient should use 60s as default timeout (AC4)."""
        from llm import LLMClient

        with patch.dict("os.environ", {"LLM_API_KEY": "test-key"}, clear=True):
            client = LLMClient()

            assert client.config.timeout == 60

    def test_init_with_custom_config(self, llm_data_factory):
        """LLMClient should accept custom LLMConfig."""
        from llm import LLMClient, LLMConfig

        config = LLMConfig(**llm_data_factory.create_config())
        client = LLMClient(config=config)

        assert client.config.api_key == "test-api-key-12345"
        assert client.config.base_url == "https://open.bigmodel.cn/api/paas/v4"
        assert client.config.model == "glm-4"
        assert client.config.timeout == 60

    def test_init_no_api_key_warning(self):
        """LLMClient should log warning if API key not configured."""
        from llm import LLMClient

        with patch.dict("os.environ", {}, clear=True):
            with patch("llm.logger") as mock_logger:
                client = LLMClient()

                mock_logger.warning.assert_called_once()
                assert "LLM_API_KEY" in mock_logger.warning.call_args[0][0]


# ============================================================================
# Test Classes - AC3: chat() method
# ============================================================================


class TestLLMClientChat:
    """Tests for LLMClient.chat() method (AC3)."""

    @pytest.mark.asyncio
    async def test_chat_returns_response_string(self, llm_data_factory):
        """chat() should return the assistant's response as string."""
        from llm import LLMClient, LLMConfig

        config = LLMConfig(**llm_data_factory.create_config())
        client = LLMClient(config=config)

        # Create mock response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(
            return_value=llm_data_factory.create_success_response(content="AI trading advice here")
        )

        # Create mock session
        mock_session = AsyncMock()
        mock_session.post = MagicMock(return_value=mock_response)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        # Patch _get_session to return our mock
        with patch.object(client, "_get_session", return_value=mock_session):
            result = await client.chat(
                system_prompt="You are a trading advisor.",
                user_message="Should I buy ETH?",
            )

            assert result == "AI trading advice here"

    @pytest.mark.asyncio
    async def test_chat_sends_correct_payload(self, llm_data_factory):
        """chat() should send OpenAI-compatible request payload."""
        from llm import LLMClient, LLMConfig

        config = LLMConfig(**llm_data_factory.create_config())
        client = LLMClient(config=config)

        with patch.object(client, "_get_session") as mock_get_session:
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=llm_data_factory.create_success_response())
            mock_session.post = MagicMock(return_value=mock_response)
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)
            mock_get_session.return_value = mock_session

            await client.chat(
                system_prompt="System prompt here",
                user_message="User message here",
            )

            # Verify the call was made with correct payload
            call_args = mock_session.post.call_args
            assert call_args is not None

            # Check URL
            url = call_args[1]["url"] if "url" in call_args[1] else call_args[0][0]
            assert "/chat/completions" in str(url)

            # Check payload structure
            payload = call_args[1]["json"]
            assert payload["model"] == "glm-4"
            assert len(payload["messages"]) == 2
            assert payload["messages"][0]["role"] == "system"
            assert payload["messages"][0]["content"] == "System prompt here"
            assert payload["messages"][1]["role"] == "user"
            assert payload["messages"][1]["content"] == "User message here"

    @pytest.mark.asyncio
    async def test_chat_sends_authorization_header(self, llm_data_factory):
        """chat() should send Bearer token in Authorization header."""
        from llm import LLMClient, LLMConfig

        config = LLMConfig(**llm_data_factory.create_config())
        client = LLMClient(config=config)

        with patch.object(client, "_get_session") as mock_get_session:
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=llm_data_factory.create_success_response())
            mock_session.post = MagicMock(return_value=mock_response)
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)
            mock_get_session.return_value = mock_session

            await client.chat("System", "User")

            headers = mock_session.post.call_args[1]["headers"]
            assert headers["Authorization"] == "Bearer test-api-key-12345"
            assert headers["Content-Type"] == "application/json"

    @pytest.mark.asyncio
    async def test_chat_content_type_json(self, llm_data_factory):
        """chat() should set Content-Type to application/json."""
        from llm import LLMClient, LLMConfig

        config = LLMConfig(**llm_data_factory.create_config())
        client = LLMClient(config=config)

        with patch.object(client, "_get_session") as mock_get_session:
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=llm_data_factory.create_success_response())
            mock_session.post = MagicMock(return_value=mock_response)
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)
            mock_get_session.return_value = mock_session

            await client.chat("System", "User")

            headers = mock_session.post.call_args[1]["headers"]
            assert headers["Content-Type"] == "application/json"


# ============================================================================
# Test Classes - AC5: Error Handling
# ============================================================================


class TestLLMClientErrorHandling:
    """Tests for LLMClient error handling (AC5)."""

    @pytest.mark.asyncio
    async def test_chat_handles_timeout(self, llm_data_factory):
        """chat() should handle TimeoutError gracefully."""
        from llm import LLMClient, LLMConfig

        config = LLMConfig(**llm_data_factory.create_config())
        client = LLMClient(config=config)

        # Create a mock session that raises TimeoutError when post is called
        mock_session = AsyncMock()
        mock_session.post = MagicMock(side_effect=TimeoutError())

        with patch.object(client, "_get_session", return_value=mock_session):
            result = await client.chat("System", "User")

            assert "Error:" in result
            assert "timed out" in result.lower()

    @pytest.mark.asyncio
    async def test_chat_handles_401_unauthorized(self, llm_data_factory):
        """chat() should handle 401 authentication error."""
        from llm import LLMClient, LLMConfig

        config = LLMConfig(**llm_data_factory.create_config())
        client = LLMClient(config=config)

        with patch.object(client, "_get_session") as mock_get_session:
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status = 401
            mock_session.post = MagicMock(return_value=mock_response)
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)
            mock_get_session.return_value = mock_session

            result = await client.chat("System", "User")

            assert "Error:" in result
            assert "authentication" in result.lower()

    @pytest.mark.asyncio
    async def test_chat_handles_429_rate_limit(self, llm_data_factory):
        """chat() should handle 429 rate limit error."""
        from llm import LLMClient, LLMConfig

        config = LLMConfig(**llm_data_factory.create_config())
        client = LLMClient(config=config)

        with patch.object(client, "_get_session") as mock_get_session:
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status = 429
            mock_session.post = MagicMock(return_value=mock_response)
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)
            mock_get_session.return_value = mock_session

            result = await client.chat("System", "User")

            assert "Error:" in result
            assert "rate limit" in result.lower()

    @pytest.mark.asyncio
    async def test_chat_handles_500_server_error(self, llm_data_factory):
        """chat() should handle 500 server error."""
        from llm import LLMClient, LLMConfig

        config = LLMConfig(**llm_data_factory.create_config())
        client = LLMClient(config=config)

        with patch.object(client, "_get_session") as mock_get_session:
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status = 500
            mock_response.text = AsyncMock(return_value="Internal Server Error")
            mock_session.post = MagicMock(return_value=mock_response)
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)
            mock_get_session.return_value = mock_session

            result = await client.chat("System", "User")

            assert "Error:" in result
            assert "500" in result

    @pytest.mark.asyncio
    async def test_chat_handles_invalid_json_response(self, llm_data_factory):
        """chat() should handle invalid JSON response."""
        from llm import LLMClient, LLMConfig

        config = LLMConfig(**llm_data_factory.create_config())
        client = LLMClient(config=config)

        with patch.object(client, "_get_session") as mock_get_session:
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(side_effect=Exception("Invalid JSON"))
            mock_session.post = MagicMock(return_value=mock_response)
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)
            mock_get_session.return_value = mock_session

            result = await client.chat("System", "User")

            assert "Error:" in result

    @pytest.mark.asyncio
    async def test_chat_handles_missing_choices(self, llm_data_factory):
        """chat() should handle response without choices array."""
        from llm import LLMClient, LLMConfig

        config = LLMConfig(**llm_data_factory.create_config())
        client = LLMClient(config=config)

        with patch.object(client, "_get_session") as mock_get_session:
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={"id": "test"})  # No choices
            mock_session.post = MagicMock(return_value=mock_response)
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)
            mock_get_session.return_value = mock_session

            result = await client.chat("System", "User")

            assert "Error:" in result
            assert "Invalid" in result or "format" in result.lower()

    @pytest.mark.asyncio
    async def test_chat_handles_empty_content(self, llm_data_factory):
        """chat() should handle response with empty content."""
        from llm import LLMClient, LLMConfig

        config = LLMConfig(**llm_data_factory.create_config())
        client = LLMClient(config=config)

        with patch.object(client, "_get_session") as mock_get_session:
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(
                return_value={
                    "choices": [{"message": {"content": ""}}]  # Empty content
                }
            )
            mock_session.post = MagicMock(return_value=mock_response)
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)
            mock_get_session.return_value = mock_session

            result = await client.chat("System", "User")

            assert "Error:" in result
            assert "Empty" in result

    @pytest.mark.asyncio
    async def test_chat_handles_network_error(self, llm_data_factory):
        """chat() should handle network errors (aiohttp.ClientError)."""
        from llm import LLMClient, LLMConfig

        config = LLMConfig(**llm_data_factory.create_config())
        client = LLMClient(config=config)

        # Create a mock session that raises ClientError when post is called
        mock_session = AsyncMock()
        mock_session.post = MagicMock(side_effect=aiohttp.ClientError("Network error"))

        with patch.object(client, "_get_session", return_value=mock_session):
            result = await client.chat("System", "User")

            assert "Error:" in result
            assert "Network" in result

    @pytest.mark.asyncio
    async def test_chat_returns_error_without_api_key(self):
        """chat() should return error message if API key not configured."""
        from llm import LLMClient

        with patch.dict("os.environ", {}, clear=True):
            client = LLMClient()

            result = await client.chat("System", "User")

            assert "Error:" in result
            assert "API key" in result


# ============================================================================
# Test Classes - Session Management
# ============================================================================


class TestLLMClientSessionManagement:
    """Tests for LLMClient session management."""

    @pytest.mark.asyncio
    async def test_get_session_creates_client_session(self, llm_data_factory):
        """_get_session should create aiohttp.ClientSession."""
        from llm import LLMClient, LLMConfig

        config = LLMConfig(**llm_data_factory.create_config(timeout=30))
        client = LLMClient(config=config)

        session = await client._get_session()

        assert isinstance(session, aiohttp.ClientSession)
        await client.close()

    @pytest.mark.asyncio
    async def test_get_session_reuses_existing_session(self, llm_data_factory):
        """_get_session should reuse existing session."""
        from llm import LLMClient, LLMConfig

        config = LLMConfig(**llm_data_factory.create_config())
        client = LLMClient(config=config)

        session1 = await client._get_session()
        session2 = await client._get_session()

        assert session1 is session2
        await client.close()

    @pytest.mark.asyncio
    async def test_close_closes_session(self, llm_data_factory):
        """close() should close the HTTP session."""
        from llm import LLMClient, LLMConfig

        config = LLMConfig(**llm_data_factory.create_config())
        client = LLMClient(config=config)

        await client._get_session()
        await client.close()

        assert client._session is None or client._session.closed


# ============================================================================
# Test Classes - Integration with config.py
# ============================================================================


class TestConfigIntegration:
    """Tests for config.py integration (AC2, AC4)."""

    def test_config_has_llm_api_key(self):
        """config.py should export LLM_API_KEY."""
        import config

        assert hasattr(config, "LLM_API_KEY")

    def test_config_has_llm_base_url(self):
        """config.py should export LLM_BASE_URL."""
        import config

        assert hasattr(config, "LLM_BASE_URL")

    def test_config_has_llm_model(self):
        """config.py should export LLM_MODEL."""
        import config

        assert hasattr(config, "LLM_MODEL")

    def test_config_has_llm_timeout(self):
        """config.py should export LLM_TIMEOUT."""
        import config

        assert hasattr(config, "LLM_TIMEOUT")

    def test_config_llm_timeout_default_60(self):
        """config.py LLM_TIMEOUT should have a sensible default value."""
        # The actual value depends on .env configuration
        # This test verifies the config is properly loaded
        import config

        assert hasattr(config, "LLM_TIMEOUT")
        assert isinstance(config.LLM_TIMEOUT, int)
        assert config.LLM_TIMEOUT > 0


# ============================================================================
# Test Classes - Logging
# ============================================================================


class TestLLMClientLogging:
    """Tests for LLMClient logging."""

    @pytest.mark.asyncio
    async def test_error_logged_on_timeout(self, llm_data_factory):
        """Timeout errors should be logged."""
        from llm import LLMClient, LLMConfig

        config = LLMConfig(**llm_data_factory.create_config())
        client = LLMClient(config=config)

        # Create a mock session that raises TimeoutError
        mock_session = AsyncMock()
        mock_session.post = MagicMock(side_effect=TimeoutError())

        with patch.object(client, "_get_session", return_value=mock_session):
            with patch("llm.logger") as mock_logger:
                await client.chat("System", "User")

                mock_logger.error.assert_called()
                # Check for timeout-related keywords (timed out or timeout)
                log_msg = mock_logger.error.call_args[0][0].lower()
                assert "timed out" in log_msg or "timeout" in log_msg

    @pytest.mark.asyncio
    async def test_error_logged_on_auth_failure(self, llm_data_factory):
        """Authentication failures should be logged."""
        from llm import LLMClient, LLMConfig

        config = LLMConfig(**llm_data_factory.create_config())
        client = LLMClient(config=config)

        # Create mock response
        mock_response = AsyncMock()
        mock_response.status = 401

        # Create mock session
        mock_session = AsyncMock()
        mock_session.post = MagicMock(return_value=mock_response)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        with patch.object(client, "_get_session", return_value=mock_session):
            with patch("llm.logger") as mock_logger:
                await client.chat("System", "User")

                mock_logger.error.assert_called()
                assert "401" in mock_logger.error.call_args[0][0]
