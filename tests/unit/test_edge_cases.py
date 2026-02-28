"""
Unit tests for edge cases and error handling (P2 priority).

Tests for: format functions error branches, post_init, main retry logic
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from telegram.error import TimedOut, NetworkError, TelegramError


# =============================================================================
# Tests for format function error branches
# =============================================================================

class TestFormatEthEdgeCases:
    """Tests for format_eth error handling."""

    def test_format_eth_float_input(self) -> None:
        """Test format_eth with float input."""
        from main import format_eth
        # Float should work (converted to float again)
        result = format_eth(1000000000000000000.0)
        assert "1.000000" == result

    def test_format_eth_negative_value(self) -> None:
        """Test format_eth with negative value."""
        from main import format_eth
        result = format_eth("-1000000000000000000")
        assert result == "-1.000000"


class TestFormatUsdEdgeCases:
    """Tests for format_usd error handling."""

    def test_format_usd_float_input(self) -> None:
        """Test format_usd with float input."""
        from main import format_usd
        result = format_usd(1234.5678)
        assert result == "$1234.57"

    def test_format_usd_very_large_value(self) -> None:
        """Test format_usd with very large value."""
        from main import format_usd
        result = format_usd("9999999999.99")
        assert result == "$9999999999.99"


class TestFormatPercentEdgeCases:
    """Tests for format_percent error handling."""

    def test_format_percent_float_input(self) -> None:
        """Test format_percent with float input."""
        from main import format_percent
        result = format_percent(15.5)
        assert result == "+15.50%"

    def test_format_percent_zero_boundary(self) -> None:
        """Test format_percent at zero boundary."""
        from main import format_percent
        result = format_percent("0.0")
        assert result == "0.00%"

    def test_format_percent_very_small_positive(self) -> None:
        """Test format_percent with very small positive value."""
        from main import format_percent
        result = format_percent("0.001")
        assert result == "+0.00%"


# =============================================================================
# Tests for post_init
# =============================================================================

class TestPostInit:
    """Tests for post_init function."""

    @pytest.mark.asyncio
    async def test_post_init_sets_commands(self) -> None:
        """Test post_init sets bot commands."""
        # Given
        mock_app = MagicMock()
        mock_app.bot = AsyncMock()

        from main import post_init

        # When
        await post_init(mock_app)

        # Then
        mock_app.bot.set_my_commands.assert_called_once()
        call_args = mock_app.bot.set_my_commands.call_args[0][0]
        command_names = [cmd.command for cmd in call_args]
        assert "start" in command_names
        assert "balance" in command_names
        assert "pnl" in command_names
        assert "positions" in command_names
        assert "activity" in command_names
        assert "swaps" in command_names
        assert "strategies" in command_names
        assert "vault" in command_names


# =============================================================================
# Tests for main function retry logic
# =============================================================================

class TestMainFunction:
    """Tests for main() function and retry logic."""

    def test_main_exits_without_token(self) -> None:
        """Test main exits when TELEGRAM_BOT_TOKEN not set."""
        with patch("main.TELEGRAM_BOT_TOKEN", None), \
             patch("builtins.print") as mock_print:
            from main import main
            main()

            mock_print.assert_called_with("Error: TELEGRAM_BOT_TOKEN not set")

    @pytest.mark.asyncio
    async def test_main_retries_on_network_error(self) -> None:
        """Test main retries on NetworkError."""
        # This tests the retry logic structure
        # We can't easily test the full loop, but we can verify the error handling

        with patch("main.TELEGRAM_BOT_TOKEN", "test_token"), \
             patch("main.Application.builder") as mock_builder:

            # Set up mock application
            mock_app = MagicMock()
            mock_app.run_polling.side_effect = NetworkError("Connection failed")
            mock_builder.return_value.token.return_value.post_init.return_value.build.return_value = mock_app

            from main import main

            # Run main - it should retry and eventually exit
            # We limit retries by patching time.sleep
            with patch("main.time.sleep"), \
                 patch("main.logger"):
                main()

            # Should have attempted run_polling multiple times (max_retries = 10)
            assert mock_app.run_polling.call_count == 10

    @pytest.mark.asyncio
    async def test_main_retries_on_timeout(self) -> None:
        """Test main retries on TimedOut error."""
        with patch("main.TELEGRAM_BOT_TOKEN", "test_token"), \
             patch("main.Application.builder") as mock_builder:

            mock_app = MagicMock()
            mock_app.run_polling.side_effect = TimedOut("Timeout")
            mock_builder.return_value.token.return_value.post_init.return_value.build.return_value = mock_app

            from main import main

            with patch("main.time.sleep"), \
                 patch("main.logger"):
                main()

            assert mock_app.run_polling.call_count == 10

    @pytest.mark.asyncio
    async def test_main_retries_on_telegram_error(self) -> None:
        """Test main retries on generic TelegramError."""
        with patch("main.TELEGRAM_BOT_TOKEN", "test_token"), \
             patch("main.Application.builder") as mock_builder:

            mock_app = MagicMock()
            mock_app.run_polling.side_effect = TelegramError("Generic error")
            mock_builder.return_value.token.return_value.post_init.return_value.build.return_value = mock_app

            from main import main

            with patch("main.time.sleep"), \
                 patch("main.logger"):
                main()

            assert mock_app.run_polling.call_count == 10

    @pytest.mark.asyncio
    async def test_main_retries_on_unexpected_error(self) -> None:
        """Test main retries on unexpected exceptions."""
        with patch("main.TELEGRAM_BOT_TOKEN", "test_token"), \
             patch("main.Application.builder") as mock_builder:

            mock_app = MagicMock()
            mock_app.run_polling.side_effect = RuntimeError("Unexpected!")
            mock_builder.return_value.token.return_value.post_init.return_value.build.return_value = mock_app

            from main import main

            with patch("main.time.sleep"), \
                 patch("main.logger"):
                main()

            assert mock_app.run_polling.call_count == 10

    def test_main_exits_on_keyboard_interrupt(self) -> None:
        """Test main exits gracefully on KeyboardInterrupt."""
        with patch("main.TELEGRAM_BOT_TOKEN", "test_token"), \
             patch("main.Application.builder") as mock_builder:

            mock_app = MagicMock()
            mock_app.run_polling.side_effect = KeyboardInterrupt()
            mock_builder.return_value.token.return_value.post_init.return_value.build.return_value = mock_app

            from main import main

            with patch("main.logger"):
                main()  # Should exit without error

            # Should only have attempted once
            assert mock_app.run_polling.call_count == 1

    def test_main_clears_proxy_env(self) -> None:
        """Test main clears proxy environment variables."""
        import os

        # Set proxy vars
        os.environ['HTTP_PROXY'] = 'http://proxy:8080'
        os.environ['HTTPS_PROXY'] = 'https://proxy:8080'

        with patch("main.TELEGRAM_BOT_TOKEN", None), \
             patch("builtins.print"):
            from main import main
            main()  # This clears proxy vars and exits

        # Proxy vars should be cleared after main() runs
        assert os.environ.get('HTTP_PROXY') is None
        assert os.environ.get('HTTPS_PROXY') is None
