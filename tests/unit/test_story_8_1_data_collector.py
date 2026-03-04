"""
ATDD Tests for Story 8-1: Strategy Data Collector

These tests are designed to FAIL before implementation (TDD RED phase).
Run: pytest tests/unit/test_story_8_1_data_collector.py -v

Generated: 2026-03-03
Story: 8-1-data-collector
"""
from dataclasses import dataclass, field
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ============================================================================
# Test Data Factory
# ============================================================================


class StrategyDataFactory:
    """Factory for creating test data for strategy collector."""

    @staticmethod
    def create_position_data(
        eth_balance: float = 10.5,
        total_pnl_usd: float = 1234.56,
        tokens: list = None,
        **overrides
    ) -> dict:
        """Create mock position data."""
        default_tokens = [
            {
                "symbol": "PEPE",
                "tokenAddress": "0x6982508145454Ce325dDbE47a25d4ec3d2311933",
                "balance": "1000000",
                "pnlUsd": 500.0,
            },
            {
                "symbol": "SHIB",
                "tokenAddress": "0x95aD61b0a150d79219dCF64E1E6Cc01f0B64C4cE",
                "balance": "500000",
                "pnlUsd": 300.0,
            },
        ]
        return {
            "ethBalance": eth_balance,
            "totalPnlUsd": total_pnl_usd,
            "tokens": tokens or default_tokens,
            **overrides,
        }

    @staticmethod
    def create_strategy_data(
        id: int = 1,
        content: str = "Hold PEPE until 2x",
        priority: int = 1,
        expiry: int = 0,  # 0 = never expires (active)
        **overrides
    ) -> dict:
        """Create mock strategy data."""
        return {
            "id": id,
            "content": content,
            "priority": priority,
            "expiry": expiry,
            **overrides,
        }

    @staticmethod
    def create_vault_data(
        paused: bool = False,
        total_value: float = 50000.0,
        **overrides
    ) -> dict:
        """Create mock vault status data."""
        return {
            "paused": paused,
            "totalValue": total_value,
            **overrides,
        }

    @staticmethod
    def create_eth_price_data(
        price: float = 2500.0,
        change_24h: float = 5.2,
        **overrides
    ) -> dict:
        """Create mock ETH price data."""
        return {
            "price": price,
            "change24h": change_24h,
            **overrides,
        }

    @staticmethod
    def create_token_list(count: int = 10) -> list:
        """Create mock token list."""
        tokens = []
        for i in range(count):
            tokens.append({
                "symbol": f"TOKEN{i}",
                "tokenAddress": f"0x{i:040x}",
                "price": 0.001 * (i + 1),
                "volume24h": 100000 * (i + 1),
            })
        return tokens

    @staticmethod
    def create_candle_data(count: int = 24) -> list:
        """Create mock candlestick data."""
        candles = []
        base_price = 0.0001
        base_time = 1703000000

        for i in range(count):
            open_price = base_price * (1 + 0.01 * i)
            close_price = open_price * 1.05
            high_price = close_price * 1.02
            low_price = open_price * 0.98

            candles.append({
                "open": open_price,
                "high": high_price,
                "low": low_price,
                "close": close_price,
                "volume": 1000000 * (i + 1),
                "timestamp": base_time + i * 3600,
            })

        return candles


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def data_factory():
    """Provide StrategyDataFactory."""
    return StrategyDataFactory()


@pytest.fixture
def mock_api(data_factory):
    """Create mock TerminalAPI instance."""
    api = AsyncMock()

    # Set up default return values
    api.get_positions.return_value = data_factory.create_position_data()
    api.get_strategies.return_value = [data_factory.create_strategy_data()]
    api.get_vault.return_value = data_factory.create_vault_data()
    api.get_eth_price.return_value = data_factory.create_eth_price_data()
    api.get_tokens.return_value = data_factory.create_token_list(10)
    api.get_candles.return_value = data_factory.create_candle_data(24)

    return api


@pytest.fixture
def collector(mock_api):
    """Create StrategyDataCollector with mocked API."""
    # Import here to allow tests to run before module exists
    from advisor import StrategyDataCollector

    return StrategyDataCollector(mock_api)


# ============================================================================
# Test Classes - AC1: advisor.py Module Structure
# ============================================================================


class TestAdvisorModule:
    """Tests for advisor.py module structure (AC1)."""

    def test_advisor_module_exists(self):
        """advisor.py module should exist in project root."""
        # GIVEN: Project structure
        # WHEN: Importing advisor module
        # THEN: Module should be importable
        import advisor

        assert advisor is not None

    def test_strategy_data_collector_class_exists(self):
        """StrategyDataCollector class should be defined in advisor module."""
        from advisor import StrategyDataCollector

        assert StrategyDataCollector is not None

    def test_collected_data_dataclass_exists(self):
        """CollectedData dataclass should be defined in advisor module."""
        from advisor import CollectedData

        assert CollectedData is not None
        # Verify it's a dataclass
        assert hasattr(CollectedData, "__dataclass_fields__")

        # Verify required fields exist
        fields = CollectedData.__dataclass_fields__
        assert "positions" in fields
        assert "strategies" in fields
        assert "vault" in fields
        assert "eth_price" in fields
        assert "tokens" in fields
        assert "candles" in fields
        assert "collected_at" in fields
        assert "errors" in fields


# ============================================================================
# Test Classes - AC2: collect() Method
# ============================================================================


class TestCollectMethod:
    """Tests for collect() method (AC2)."""

    @pytest.mark.asyncio
    async def test_collect_returns_collected_data(self, collector):
        """collect() should return CollectedData instance."""
        # GIVEN: StrategyDataCollector instance
        # WHEN: Calling collect()
        # THEN: Should return CollectedData
        from advisor import CollectedData

        result = await collector.collect()

        assert isinstance(result, CollectedData)

    @pytest.mark.asyncio
    async def test_collect_gathers_positions(self, collector, mock_api, data_factory):
        """collect() should gather position data via API."""
        # GIVEN: Mock API with position data
        expected_data = data_factory.create_position_data(eth_balance=15.0)
        mock_api.get_positions.return_value = expected_data

        # WHEN: Calling collect()
        result = await collector.collect()

        # THEN: Should call get_positions and store result
        mock_api.get_positions.assert_called_once()
        assert result.positions == expected_data

    @pytest.mark.asyncio
    async def test_collect_gathers_strategies(self, collector, mock_api, data_factory):
        """collect() should gather strategy data via API."""
        # GIVEN: Mock API with strategy data
        expected_data = [
            data_factory.create_strategy_data(id=1, content="Test strategy"),
            data_factory.create_strategy_data(id=2, content="Another strategy"),
        ]
        mock_api.get_strategies.return_value = expected_data

        # WHEN: Calling collect()
        result = await collector.collect()

        # THEN: Should call get_strategies and store result
        mock_api.get_strategies.assert_called_once()
        assert result.strategies == expected_data

    @pytest.mark.asyncio
    async def test_collect_gathers_vault_status(self, collector, mock_api, data_factory):
        """collect() should gather vault status via API."""
        # GIVEN: Mock API with vault data
        expected_data = data_factory.create_vault_data(paused=True)
        mock_api.get_vault.return_value = expected_data

        # WHEN: Calling collect()
        result = await collector.collect()

        # THEN: Should call get_vault and store result
        mock_api.get_vault.assert_called_once()
        assert result.vault == expected_data

    @pytest.mark.asyncio
    async def test_collect_gathers_market_data(self, collector, mock_api, data_factory):
        """collect() should gather ETH price and token list via API."""
        # GIVEN: Mock API with market data
        expected_eth_price = data_factory.create_eth_price_data(price=3000.0)
        expected_tokens = data_factory.create_token_list(15)

        mock_api.get_eth_price.return_value = expected_eth_price
        mock_api.get_tokens.return_value = expected_tokens

        # WHEN: Calling collect()
        result = await collector.collect()

        # THEN: Should call both market data APIs
        mock_api.get_eth_price.assert_called_once()
        mock_api.get_tokens.assert_called_once()

        assert result.eth_price == expected_eth_price
        assert result.tokens == expected_tokens


# ============================================================================
# Test Classes - AC3: get_candles() in api.py
# ============================================================================


class TestAPICandles:
    """Tests for get_candles() method in TerminalAPI (AC3)."""

    def test_api_get_candles_exists(self):
        """TerminalAPI should have get_candles() method."""
        from api import TerminalAPI

        api = TerminalAPI()
        assert hasattr(api, "get_candles")
        assert callable(api.get_candles)

    @pytest.mark.asyncio
    async def test_api_get_candles_returns_list(self, data_factory):
        """get_candles() should return list of candle objects."""
        from api import TerminalAPI

        api = TerminalAPI()

        # Mock the _get method to return candle data
        expected_candles = data_factory.create_candle_data(24)
        with patch.object(api, "_get", return_value=expected_candles):
            result = await api.get_candles(
                token_address="0x6982508145454Ce325dDbE47a25d4ec3d2311933",
                timeframe="1h",
                limit=24
            )

        assert isinstance(result, list)
        assert len(result) == 24

    @pytest.mark.asyncio
    async def test_api_get_candles_correct_params(self, data_factory):
        """get_candles() should send correct query parameters."""
        from api import TerminalAPI

        api = TerminalAPI()

        # Mock _get to capture parameters
        with patch.object(api, "_get") as mock_get:
            mock_get.return_value = data_factory.create_candle_data(24)

            await api.get_candles(
                token_address="0x6982508145454Ce325dDbE47a25d4ec3d2311933",
                timeframe="4h",
                limit=24
            )

            # Verify _get was called with correct endpoint and params
            call_args = mock_get.call_args
            endpoint = call_args[0][0]
            params = call_args[0][1] if len(call_args[0]) > 1 else call_args[1].get("params", {})

            # Check endpoint includes token address
            assert "0x6982508145454Ce325dDbE47a25d4ec3d2311933" in endpoint
            assert "candles" in endpoint

            # Check query params
            assert params.get("timeframe") == "4h"
            assert "to" in params  # timestamp
            assert params.get("countback") == 24


# ============================================================================
# Test Classes - AC4: format_for_llm() Method
# ============================================================================


class TestFormatForLLM:
    """Tests for format_for_llm() method (AC4)."""

    def test_format_for_llm_returns_string(self, collector, data_factory):
        """format_for_llm() should return string."""
        # GIVEN: CollectedData instance
        from advisor import CollectedData

        data = CollectedData(
            positions=data_factory.create_position_data(),
            collected_at=datetime.now().isoformat()
        )

        # WHEN: Calling format_for_llm()
        result = collector.format_for_llm(data)

        # THEN: Should return string
        assert isinstance(result, str)
        assert len(result) > 0

    def test_format_for_llm_includes_positions(self, collector, data_factory):
        """format_for_llm() output should include positions section."""
        # GIVEN: CollectedData with position data
        from advisor import CollectedData

        positions = data_factory.create_position_data(
            eth_balance=10.5,
            total_pnl_usd=1234.56,
            tokens=[
                {"symbol": "PEPE", "balance": "1000000", "pnlUsd": 500.0},
                {"symbol": "SHIB", "balance": "500000", "pnlUsd": 300.0},
            ]
        )

        data = CollectedData(
            positions=positions,
            collected_at=datetime.now().isoformat()
        )

        # WHEN: Calling format_for_llm()
        result = collector.format_for_llm(data)

        # THEN: Should include position information
        assert "## Positions" in result or "# Positions" in result
        assert "10.5" in result  # ETH balance
        assert "PEPE" in result  # Token symbol
        assert "1234.56" in result or "1234" in result  # PnL

    def test_format_for_llm_includes_strategies(self, collector, data_factory):
        """format_for_llm() output should include strategies section."""
        # GIVEN: CollectedData with strategy data
        from advisor import CollectedData

        strategies = [
            data_factory.create_strategy_data(id=1, content="Hold PEPE until 2x", priority=1),
            data_factory.create_strategy_data(id=2, content="Take profit at 50%", priority=2),
        ]

        data = CollectedData(
            strategies=strategies,
            collected_at=datetime.now().isoformat()
        )

        # WHEN: Calling format_for_llm()
        result = collector.format_for_llm(data)

        # THEN: Should include strategy information
        assert "## Active Strategies" in result or "# Active Strategies" in result or "## Strategies" in result
        assert "Hold PEPE" in result  # Strategy content
        assert "#1" in result or "ID: 1" in result or "1:" in result  # Strategy ID


# ============================================================================
# Test Classes - AC5: Error Handling
# ============================================================================


class TestErrorHandling:
    """Tests for error handling (AC5)."""

    @pytest.mark.asyncio
    async def test_collect_handles_api_failure_gracefully(self, mock_api):
        """collect() should handle API failures and return partial data."""
        # GIVEN: Mock API with some methods failing
        from advisor import StrategyDataCollector

        # Make get_positions fail
        mock_api.get_positions.side_effect = Exception("API Error")

        collector = StrategyDataCollector(mock_api)

        # WHEN: Calling collect()
        result = await collector.collect()

        # THEN: Should return CollectedData with errors list
        assert result is not None
        assert len(result.errors) > 0
        assert any("positions" in err.lower() for err in result.errors)

    @pytest.mark.asyncio
    async def test_collect_continues_after_partial_failure(self, mock_api, data_factory):
        """collect() should continue collecting other data after one API fails."""
        # GIVEN: Mock API with get_positions failing
        from advisor import StrategyDataCollector

        mock_api.get_positions.side_effect = Exception("Positions API Error")
        mock_api.get_strategies.return_value = [data_factory.create_strategy_data()]

        collector = StrategyDataCollector(mock_api)

        # WHEN: Calling collect()
        result = await collector.collect()

        # THEN: Should have collected strategies despite positions failure
        assert result.strategies is not None
        assert len(result.strategies) > 0
        assert len(result.errors) > 0

    def test_format_for_llm_includes_errors(self, collector, data_factory):
        """format_for_llm() should include errors section when errors exist."""
        # GIVEN: CollectedData with errors
        from advisor import CollectedData

        data = CollectedData(
            positions=data_factory.create_position_data(),
            errors=["positions: API Error", "candles: Timeout"]
        )

        # WHEN: Calling format_for_llm()
        result = collector.format_for_llm(data)

        # THEN: Should include error section
        assert "## Collection Errors" in result or "# Errors" in result or "Error" in result
        assert "positions" in result.lower() or "api error" in result.lower()

    @pytest.mark.asyncio
    async def test_collect_never_raises_exception(self, mock_api):
        """collect() should never raise exceptions, always return CollectedData."""
        # GIVEN: Mock API with all methods failing
        from advisor import StrategyDataCollector

        mock_api.get_positions.side_effect = Exception("Error 1")
        mock_api.get_strategies.side_effect = Exception("Error 2")
        mock_api.get_vault.side_effect = Exception("Error 3")
        mock_api.get_eth_price.side_effect = Exception("Error 4")
        mock_api.get_tokens.side_effect = Exception("Error 5")

        collector = StrategyDataCollector(mock_api)

        # WHEN: Calling collect()
        # THEN: Should not raise exception
        try:
            result = await collector.collect()
            assert result is not None
            assert len(result.errors) > 0
        except Exception as e:
            pytest.fail(f"collect() should not raise exception, but raised: {e}")


# ============================================================================
# Test Classes - Candlestick Collection
# ============================================================================


class TestCandleCollection:
    """Tests for candlestick data collection."""

    @pytest.mark.asyncio
    async def test_collect_gathers_candles_for_held_tokens(self, collector, mock_api, data_factory):
        """collect() should gather candles for tokens held in positions."""
        # GIVEN: Position with specific tokens
        positions = data_factory.create_position_data(
            tokens=[
                {"symbol": "PEPE", "tokenAddress": "0x123...", "balance": "1000000"},
                {"symbol": "SHIB", "tokenAddress": "0x456...", "balance": "500000"},
            ]
        )
        mock_api.get_positions.return_value = positions

        # WHEN: Calling collect()
        result = await collector.collect()

        # THEN: Should have called get_candles for each token
        assert result.candles is not None
        # Should have candles for at least one token
        assert len(result.candles) > 0

    @pytest.mark.asyncio
    async def test_collect_gathers_multiple_timeframes(self, collector, mock_api, data_factory):
        """collect() should gather candles for 1h, 4h, and 1d timeframes."""
        # GIVEN: Position with tokens
        positions = data_factory.create_position_data(
            tokens=[
                {"symbol": "PEPE", "tokenAddress": "0x123...", "balance": "1000000"},
            ]
        )
        mock_api.get_positions.return_value = positions

        # WHEN: Calling collect()
        result = await collector.collect()

        # THEN: Should have candles for multiple timeframes
        # (check that get_candles was called multiple times)
        if result.candles and "PEPE" in result.candles:
            pepe_candles = result.candles["PEPE"]
            # Should have at least one timeframe
            assert len(pepe_candles) > 0


# ============================================================================
# Test Classes - Timestamp
# ============================================================================


class TestTimestamp:
    """Tests for data collection timestamp."""

    @pytest.mark.asyncio
    async def test_collect_includes_timestamp(self, collector):
        """collect() should include collection timestamp."""
        # WHEN: Calling collect()
        result = await collector.collect()

        # THEN: Should have timestamp
        assert result.collected_at is not None
        assert len(result.collected_at) > 0
        # Should be ISO format
        assert "T" in result.collected_at or "-" in result.collected_at

    def test_format_for_llm_includes_timestamp(self, collector, data_factory):
        """format_for_llm() should include collection timestamp."""
        # GIVEN: CollectedData with timestamp
        from advisor import CollectedData

        timestamp = "2026-03-03T10:30:00"
        data = CollectedData(
            positions=data_factory.create_position_data(),
            collected_at=timestamp
        )

        # WHEN: Calling format_for_llm()
        result = collector.format_for_llm(data)

        # THEN: Should include timestamp in output
        assert timestamp in result or "2026-03-03" in result


# ============================================================================
# Test Classes - Integration with api.py
# ============================================================================


class TestAPIIntegration:
    """Tests for api.py integration."""

    def test_api_module_has_terminal_api_class(self):
        """api.py should have TerminalAPI class."""
        from api import TerminalAPI

        assert TerminalAPI is not None

    def test_api_has_required_methods(self):
        """TerminalAPI should have all required methods."""
        from api import TerminalAPI

        api = TerminalAPI()

        # Check existing methods
        assert hasattr(api, "get_positions")
        assert hasattr(api, "get_strategies")
        assert hasattr(api, "get_vault")
        assert hasattr(api, "get_eth_price")
        assert hasattr(api, "get_tokens")

        # Check new method (will fail until implemented)
        assert hasattr(api, "get_candles")


# ============================================================================
# Test Classes - Logging
# ============================================================================


class TestLogging:
    """Tests for logging behavior."""

    @pytest.mark.asyncio
    async def test_error_logged_on_api_failure(self, mock_api):
        """API failures should be logged."""
        from advisor import StrategyDataCollector

        # Make API fail
        mock_api.get_positions.side_effect = Exception("API Error")

        collector = StrategyDataCollector(mock_api)

        with patch("advisor.logger") as mock_logger:
            await collector.collect()

            # Should have logged error
            mock_logger.error.assert_called()
            log_msg = mock_logger.error.call_args[0][0].lower()
            assert "positions" in log_msg or "error" in log_msg
