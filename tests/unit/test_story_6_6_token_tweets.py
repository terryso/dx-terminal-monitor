"""
Unit tests for Story 6.6: Token Tweets Query

Tests for: api.get_token_tweets(), cmd_tweets command handler

ATDD Checklist:
- [ ] AC1: Add get_token_tweets(symbol, limit) method to api.py TerminalAPI class
- [ ] AC2: Add cmd_tweets command handler in commands/query.py
- [ ] AC3: Command format: /tweets <symbol> [limit] - symbol required, optional limit (default 5)
- [ ] AC4: Format output: tweet content, author, time, link
- [ ] AC5: Handle missing symbol with usage hint
- [ ] AC6: Handle empty results with appropriate message
- [ ] AC7: Register /tweets command in Bot command menu
- [ ] AC8: Add unit tests for the new command
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def mock_update():
    """Create mock Telegram Update object."""
    update = MagicMock()
    update.effective_user = MagicMock()
    update.effective_user.id = 123456789
    update.message = AsyncMock()
    return update


@pytest.fixture
def mock_context():
    """Create mock Telegram Context object."""
    context = MagicMock()
    context.args = []
    context.bot = AsyncMock()
    return context


@pytest.fixture
def mock_tweets_response():
    """Create mock tweets API response.

    Based on expected API response structure from /tweets/{tokenSymbol} endpoint.
    """
    return {
        "totalCount": 3,
        "hasMoreItems": False,
        "items": [
            {
                "userName": "VitalikButerin",
                "text": "Excited about the new ETH upgrade roadmap and the progress we've made on scalability!",
                "createdAt": "2026-03-01",
                "linkToTweet": "https://x.com/VitalikButerin/status/123456789",
            },
            {
                "userName": "ethereum",
                "text": "The merge is complete! Thank you to all contributors who made this possible.",
                "createdAt": "2026-03-01",
                "linkToTweet": "https://x.com/ethereum/status/987654321",
            },
            {
                "userName": "ethenterprise",
                "text": "Enterprise adoption continues to grow with major partnerships announced this quarter.",
                "createdAt": "2026-02-28",
                "linkToTweet": "https://x.com/ethenterprise/status/456789123",
            },
        ],
    }


@pytest.fixture
def mock_empty_tweets_response():
    """Create mock empty tweets API response."""
    return {"totalCount": 0, "hasMoreItems": False, "items": []}


@pytest.fixture
def mock_api_error_response():
    """Create mock API error response."""
    return {"error": "HTTP 500 - Internal Server Error"}


# =============================================================================
# Helper Functions (Data Factories)
# =============================================================================


def create_tweet_entry(overrides=None):
    """Create a single tweet entry with optional overrides.

    Args:
        overrides: Dict of fields to override defaults

    Returns:
        Dict with tweet entry data
    """
    defaults = {
        "userName": "TestUser",
        "text": "This is a test tweet about crypto.",
        "createdAt": "2026-03-03",
        "linkToTweet": "https://x.com/TestUser/status/111222333",
    }
    if overrides:
        defaults.update(overrides)
    return defaults


def create_tweet_entries(count):
    """Create multiple tweet entries.

    Args:
        count: Number of entries to create

    Returns:
        List of tweet entry dicts
    """
    entries = []
    for i in range(count):
        entries.append(
            create_tweet_entry(
                {
                    "author": f"User{i + 1}",
                    "content": f"Tweet content {i + 1} about crypto and blockchain.",
                    "timestamp": f"2026-03-0{3 - i}" if i < 3 else "2026-02-28",
                    "link": f"https://x.com/User{i + 1}/status/{100000 + i}",
                }
            )
        )
    return entries


# =============================================================================
# Test Class: TestGetTokenTweets (API Method Tests) - AC1
# =============================================================================


class TestGetTokenTweets:
    """Tests for get_token_tweets API method - AC1."""

    @pytest.mark.asyncio
    async def test_get_token_tweets_success(self, mock_tweets_response):
        """Test get_token_tweets returns tweet data.

        AC1: Add get_token_tweets(symbol, limit) method to api.py that calls /tweets/{symbol} endpoint
        """
        # Given
        from api import TerminalAPI

        api = TerminalAPI()

        with patch.object(api, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_tweets_response

            # When
            result = await api.get_token_tweets("ETH")

        # Then
        assert result is not None
        assert isinstance(result, dict)
        assert "items" in result
        assert len(result["items"]) == 3
        assert result["items"][0]["userName"] == "VitalikButerin"
        assert result["items"][1]["userName"] == "ethereum"
        assert result["items"][2]["userName"] == "ethenterprise"
        mock_get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_token_tweets_with_custom_limit(self, mock_tweets_response):
        """Test get_token_tweets accepts custom limit parameter.

        AC1, AC3: Method should accept optional limit parameter
        """
        # Given
        from api import TerminalAPI

        api = TerminalAPI()

        with patch.object(api, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_tweets_response

            # When
            result = await api.get_token_tweets("ETH", limit=2)

        # Then
        assert result is not None
        # Verify endpoint path includes symbol and limit/order params were passed
        call_args = mock_get.call_args
        assert "/tweets/ETH" in call_args[0][0]
        assert call_args[0][1] == {"limit": 2, "order": "desc"}

    @pytest.mark.asyncio
    async def test_get_token_tweets_empty(self, mock_empty_tweets_response):
        """Test get_token_tweets returns empty items when no data."""
        # Given
        from api import TerminalAPI

        api = TerminalAPI()

        with patch.object(api, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_empty_tweets_response

            # When
            result = await api.get_token_tweets("UNKNOWN")

        # Then
        assert result is not None
        assert isinstance(result, dict)
        assert "items" in result
        assert len(result["items"]) == 0
        mock_get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_token_tweets_api_error(self, mock_api_error_response):
        """Test get_token_tweets handles API errors."""
        # Given
        from api import TerminalAPI

        api = TerminalAPI()

        with patch.object(api, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_api_error_response

            # When
            result = await api.get_token_tweets("ETH")

        # Then
        assert "error" in result
        mock_get.assert_called_once()


# =============================================================================
# Test Class: TestCmdTweets (Command Handler Tests) - AC2, AC3, AC4, AC5, AC6
# =============================================================================


class TestCmdTweets:
    """Tests for cmd_tweets command handler - AC2, AC3, AC4, AC5, AC6."""

    @pytest.mark.asyncio
    async def test_cmd_tweets_success(
        self, mock_update, mock_context, mock_tweets_response
    ):
        """Test normal query - cmd_tweets returns formatted tweets.

        AC2: Add cmd_tweets command handler in commands/query.py
        AC4: Format output: tweet content, author, time, link
        """
        # Given
        mock_context.args = ["ETH"]
        mock_api = AsyncMock()
        mock_api.get_token_tweets = AsyncMock(return_value=mock_tweets_response)

        with patch("commands.query.authorized", return_value=True), patch(
            "commands.query._get_api"
        ) as mock_get_api:
            mock_get_api.return_value = mock_api
            from commands.query import cmd_tweets

            # When
            await cmd_tweets(mock_update, mock_context)

        # Then
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "ETH" in call_args
        assert "Tweets" in call_args or "tweets" in call_args.lower()
        assert "VitalikButerin" in call_args
        assert "ethereum" in call_args
        assert "ethenterprise" in call_args
        # AC4: Check for timestamp and link
        assert "2026-03-01" in call_args
        assert "https://x.com" in call_args

    @pytest.mark.asyncio
    async def test_cmd_tweets_unauthorized(self, mock_update, mock_context):
        """Test unauthorized user is rejected."""
        # Given
        mock_context.args = ["ETH"]
        mock_update.effective_user.id = 99999  # Non-authorized user

        with patch("commands.query.authorized", return_value=False):
            from commands.query import cmd_tweets

            # When
            await cmd_tweets(mock_update, mock_context)

        # Then
        # Should not call reply_text since user is not authorized
        mock_update.message.reply_text.assert_not_called()

    @pytest.mark.asyncio
    async def test_cmd_tweets_missing_symbol(self, mock_update, mock_context):
        """Test missing symbol displays usage hint.

        AC5: Handle missing symbol with usage hint
        """
        # Given
        mock_context.args = []  # No symbol provided

        with patch("commands.query.authorized", return_value=True):
            from commands.query import cmd_tweets

            # When
            await cmd_tweets(mock_update, mock_context)

        # Then
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "Usage" in call_args or "usage" in call_args.lower()
        assert "/tweets" in call_args
        assert "symbol" in call_args.lower()

    @pytest.mark.asyncio
    async def test_cmd_tweets_empty_results(
        self, mock_update, mock_context, mock_empty_tweets_response
    ):
        """Test empty results displays appropriate message.

        AC6: Handle empty results with appropriate message
        """
        # Given
        mock_context.args = ["UNKNOWN"]
        mock_api = AsyncMock()
        mock_api.get_token_tweets = AsyncMock(return_value=mock_empty_tweets_response)

        with patch("commands.query.authorized", return_value=True), patch(
            "commands.query._get_api"
        ) as mock_get_api:
            mock_get_api.return_value = mock_api
            from commands.query import cmd_tweets

            # When
            await cmd_tweets(mock_update, mock_context)

        # Then
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "No tweets" in call_args or "no tweets" in call_args.lower()
        assert "UNKNOWN" in call_args

    @pytest.mark.asyncio
    async def test_cmd_tweets_api_error(
        self, mock_update, mock_context, mock_api_error_response
    ):
        """Test API error message display."""
        # Given
        mock_context.args = ["ETH"]
        mock_api = AsyncMock()
        mock_api.get_token_tweets = AsyncMock(return_value=mock_api_error_response)

        with patch("commands.query.authorized", return_value=True), patch(
            "commands.query._get_api"
        ) as mock_get_api:
            mock_get_api.return_value = mock_api
            from commands.query import cmd_tweets

            # When
            await cmd_tweets(mock_update, mock_context)

        # Then
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "Error" in call_args or "error" in call_args.lower()

    @pytest.mark.asyncio
    async def test_cmd_tweets_with_limit_arg(
        self, mock_update, mock_context, mock_tweets_response
    ):
        """Test command with custom limit argument.

        AC3: Command format: /tweets <symbol> [limit] - optional limit parameter
        """
        # Given
        mock_context.args = ["ETH", "2"]  # User passed limit argument
        mock_api = AsyncMock()
        # Create a response with 2 items
        two_tweets = {
            "totalCount": 2,
            "hasMoreItems": False,
            "items": mock_tweets_response["items"][:2],
        }
        mock_api.get_token_tweets = AsyncMock(return_value=two_tweets)

        with patch("commands.query.authorized", return_value=True), patch(
            "commands.query._get_api"
        ) as mock_get_api:
            mock_get_api.return_value = mock_api
            from commands.query import cmd_tweets

            # When
            await cmd_tweets(mock_update, mock_context)

        # Then
        # Verify API was called with symbol and limit from args
        mock_api.get_token_tweets.assert_called_once_with("ETH", 2)

    @pytest.mark.asyncio
    async def test_cmd_tweets_invalid_limit_arg(
        self, mock_update, mock_context, mock_tweets_response
    ):
        """Test command with invalid limit argument uses default.

        AC3: Invalid/non-integer limit should use default (5)
        """
        # Given
        mock_context.args = ["ETH", "invalid"]  # Invalid limit argument
        mock_api = AsyncMock()
        mock_api.get_token_tweets = AsyncMock(return_value=mock_tweets_response)

        with patch("commands.query.authorized", return_value=True), patch(
            "commands.query._get_api"
        ) as mock_get_api:
            mock_get_api.return_value = mock_api
            from commands.query import cmd_tweets

            # When
            await cmd_tweets(mock_update, mock_context)

        # Then
        # Verify API was called with default limit (5)
        mock_api.get_token_tweets.assert_called_once_with("ETH", 5)

    @pytest.mark.asyncio
    async def test_cmd_tweets_symbol_case_insensitive(
        self, mock_update, mock_context, mock_tweets_response
    ):
        """Test that symbol is converted to uppercase.

        AC3: Symbol argument should be case-insensitive (converted to uppercase)
        """
        # Given
        mock_context.args = ["eth"]  # lowercase symbol
        mock_api = AsyncMock()
        mock_api.get_token_tweets = AsyncMock(return_value=mock_tweets_response)

        with patch("commands.query.authorized", return_value=True), patch(
            "commands.query._get_api"
        ) as mock_get_api:
            mock_get_api.return_value = mock_api
            from commands.query import cmd_tweets

            # When
            await cmd_tweets(mock_update, mock_context)

        # Then
        # Verify API was called with uppercase symbol
        mock_api.get_token_tweets.assert_called_once()
        call_args = mock_api.get_token_tweets.call_args
        assert call_args[0][0] == "ETH"  # Symbol should be uppercase


# =============================================================================
# Test Class: TestCommandRegistration - AC7
# =============================================================================


class TestCommandRegistration:
    """Tests for tweets command registration - AC7."""

    def test_cmd_tweets_exported_from_query(self):
        """Test that cmd_tweets is exported from commands.query module."""
        try:
            from commands.query import cmd_tweets

            assert cmd_tweets is not None
        except ImportError:
            pytest.fail("cmd_tweets not exported from commands.query")

    def test_cmd_tweets_in_all_exports(self):
        """Test that cmd_tweets is in __all__ list."""
        import commands

        if hasattr(commands, "__all__"):
            assert "cmd_tweets" in commands.__all__
        else:
            # Verify the function exists
            assert hasattr(commands, "cmd_tweets")

    @pytest.mark.asyncio
    async def test_tweets_command_in_bot_commands(self):
        """Test that tweets command is in bot commands.

        AC7: Register /tweets command in Bot command menu
        """
        from main import post_init

        # Create a mock application
        mock_app = MagicMock()
        mock_app.bot = AsyncMock()
        mock_app.bot.set_my_commands = AsyncMock()

        # Call post_init
        await post_init(mock_app)

        # Verify set_my_commands was called
        mock_app.bot.set_my_commands.assert_called_once()
        commands = mock_app.bot.set_my_commands.call_args[0][0]
        command_names = [cmd.command for cmd in commands]
        assert "tweets" in command_names

    @pytest.mark.asyncio
    async def test_cmd_start_includes_tweets_help(self):
        """Test that /start help text includes /tweets command."""
        mock_update = MagicMock()
        mock_update.effective_user = MagicMock()
        mock_update.effective_user.id = 123456789
        mock_update.message = AsyncMock()

        mock_context = MagicMock()
        mock_context.args = []

        with patch("commands.query.authorized", return_value=True):
            from commands.query import cmd_start

            await cmd_start(mock_update, mock_context)

        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "/tweets" in call_args


# =============================================================================
# Test Class: TestOutputFormatting - AC4
# =============================================================================


class TestOutputFormatting:
    """Tests for output formatting - AC4."""

    @pytest.mark.asyncio
    async def test_output_format_includes_author_and_timestamp(
        self, mock_update, mock_context, mock_tweets_response
    ):
        """Test output includes author and timestamp - AC4."""
        # Given
        mock_context.args = ["ETH"]
        mock_api = AsyncMock()
        mock_api.get_token_tweets = AsyncMock(return_value=mock_tweets_response)

        with patch("commands.query.authorized", return_value=True), patch(
            "commands.query._get_api"
        ) as mock_get_api:
            mock_get_api.return_value = mock_api
            from commands.query import cmd_tweets

            # When
            await cmd_tweets(mock_update, mock_context)

        # Then
        call_args = mock_update.message.reply_text.call_args[0][0]
        # Should include @ prefix for authors
        assert "@" in call_args or "VitalikButerin" in call_args
        assert "ethereum" in call_args
        # Should include timestamps
        assert "2026-03-01" in call_args or "2026-02-28" in call_args

    @pytest.mark.asyncio
    async def test_output_format_includes_content_and_link(
        self, mock_update, mock_context, mock_tweets_response
    ):
        """Test output includes tweet content and link - AC4."""
        # Given
        mock_context.args = ["ETH"]
        mock_api = AsyncMock()
        mock_api.get_token_tweets = AsyncMock(return_value=mock_tweets_response)

        with patch("commands.query.authorized", return_value=True), patch(
            "commands.query._get_api"
        ) as mock_get_api:
            mock_get_api.return_value = mock_api
            from commands.query import cmd_tweets

            # When
            await cmd_tweets(mock_update, mock_context)

        # Then
        call_args = mock_update.message.reply_text.call_args[0][0]
        # Should include tweet content (truncated or full)
        assert "ETH upgrade" in call_args or "merge" in call_args or "Enterprise" in call_args
        # Should include links
        assert "https://x.com" in call_args
