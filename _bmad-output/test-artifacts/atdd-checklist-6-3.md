---
stepsCompleted:
  - step-01-preflight-and-context
  - step-02-test-generation
lastStep: step-02-test-generation
lastSaved: '2026-03-03'
story_id: '6-3'
story_file: _bmad-output/implementation-artifacts/6-3-token-detail.md
inputDocuments:
  - _bmad-output/implementation-artifacts/6-3-token-detail.md
  - tests/conftest.py
  - tests/unit/test_story_6_2_tokens_list.py
detected_stack: backend
test_framework: pytest
---

# ATDD Checklist - Story 6-3: Token Detail Query

**Generated**: 2026-03-03
**Story**: 6-3 Token Detail Query
**Status**: Ready for Test Implementation (RED Phase)

---

## Story Summary

**As a** user, I need to **query specific token details via `/token <symbol>` command** so that **I can deeply understand a particular token before trading**.

### Acceptance Criteria

1. Add `get_token(address)` method to `api.py`
2. Call `/token/{tokenAddress}` endpoint
3. Add `cmd_token` command handler to `commands/query.py`
4. Command format: `/token ETH` or `/token 0x...`
5. Format output: name, price, market cap, holder count, 24h volume
6. Add unit tests

---

## Test Strategy

### Test Levels
- **Unit Tests**: API method, command handler, formatters
- **Integration Tests**: End-to-end command flow
- **Test Priority**: P1 (Core feature)

### Test Framework
- **Framework**: pytest with pytest-asyncio
- **Mocking**: unittest.mock (AsyncMock, MagicMock, patch)
- **Pattern**: Given-When-Then structure

---

## Test Cases

### 1. API Method Tests (TestGetToken)

#### TC-1.1: get_token success with symbol
**Given**: API endpoint returns token details
**When**: Call `get_token("ETH")`
**Then**: Returns token dict with expected fields
**Priority**: P1
**Type**: Unit

```python
async def test_get_token_success_with_symbol():
    """Test get_token returns token details for symbol."""
    # Given
    from api import TerminalAPI
    api = TerminalAPI()
    mock_response = {
        "symbol": "ETH",
        "name": "Ethereum",
        "address": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
        "priceUsd": "3000.00",
        "change24h": "2.5",
        "marketCapUsd": "360000000000",
        "holderCount": 1234,
        "volume24hUsd": "15000000000"
    }

    with patch.object(api, "_get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        # When
        result = await api.get_token("ETH")

    # Then
    assert result["symbol"] == "ETH"
    assert result["name"] == "Ethereum"
    mock_get.assert_called_once_with("/token/ETH")
```

#### TC-1.2: get_token success with address
**Given**: API endpoint returns token details
**When**: Call `get_token("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")`
**Then**: Returns token dict with expected fields
**Priority**: P1
**Type**: Unit

#### TC-1.3: get_token API error handling
**Given**: API endpoint returns error
**When**: Call `get_token("INVALID")`
**Then**: Returns error dict
**Priority**: P1
**Type**: Unit

```python
async def test_get_token_api_error():
    """Test get_token handles API errors."""
    # Given
    from api import TerminalAPI
    api = TerminalAPI()

    with patch.object(api, "_get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = {"error": "Token not found"}

        # When
        result = await api.get_token("INVALID")

    # Then
    assert "error" in result
```

---

### 2. Command Handler Tests (TestCmdToken)

#### TC-2.1: cmd_token success with symbol
**Given**: Authorized user provides valid symbol
**When**: Call `/token ETH`
**Then**: Returns formatted token details
**Priority**: P1
**Type**: Unit

```python
async def test_cmd_token_success():
    """Test normal query - cmd_token returns formatted token details."""
    # Given
    mock_api = AsyncMock()
    mock_api.get_token = AsyncMock(return_value={
        "symbol": "ETH",
        "name": "Ethereum",
        "address": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
        "priceUsd": "3000.00",
        "change24h": "2.5",
        "marketCapUsd": "360000000000",
        "holderCount": 1234,
        "volume24hUsd": "15000000000"
    })

    with patch("commands.query.authorized", return_value=True), \
         patch("commands.query._get_api") as mock_get_api:
        mock_get_api.return_value = mock_api
        from commands.query import cmd_token

        # When
        await cmd_token(mock_update, mock_context)

    # Then
    call_args = mock_update.message.reply_text.call_args[0][0]
    assert "Token Details: ETH" in call_args
    assert "Ethereum" in call_args
    assert "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2" in call_args
    assert "$3,000.00" in call_args
    assert "+2.5%" in call_args
    assert "1,234" in call_args
```

#### TC-2.2: cmd_token success with address
**Given**: Authorized user provides valid address
**When**: Call `/token 0xC02...`
**Then**: Returns formatted token details
**Priority**: P1
**Type**: Unit

#### TC-2.3: cmd_token unauthorized user
**Given**: Unauthorized user
**When**: Call `/token ETH`
**Then**: No response sent
**Priority**: P1
**Type**: Unit

#### TC-2.4: cmd_token missing argument
**Given**: Authorized user provides no argument
**When**: Call `/token` (no args)
**Then**: Returns usage hint
**Priority**: P1
**Type**: Unit

```python
async def test_cmd_token_missing_argument():
    """Test missing argument displays usage hint."""
    # Given
    mock_context.args = []  # No arguments

    with patch("commands.query.authorized", return_value=True):
        from commands.query import cmd_token

        # When
        await cmd_token(mock_update, mock_context)

    # Then
    call_args = mock_update.message.reply_text.call_args[0][0]
    assert "Usage" in call_args or "usage" in call_args.lower()
```

#### TC-2.5: cmd_token API error
**Given**: API returns error
**When**: Call `/token ETH`
**Then**: Returns error message
**Priority**: P1
**Type**: Unit

---

### 3. Command Registration Tests (TestCommandRegistration)

#### TC-3.1: cmd_token exported from query
**Given**: Commands module
**When**: Import cmd_token from commands.query
**Then**: Function exists
**Priority**: P1
**Type**: Unit

#### TC-3.2: cmd_token in __all__ exports
**Given**: Commands module __all__ list
**When**: Check __all__
**Then**: "cmd_token" is in list
**Priority**: P1
**Type**: Unit

#### TC-3.3: token command in bot commands
**Given**: Bot command menu
**When**: Call post_init
**Then**: "token" command is registered
**Priority**: P1
**Type**: Unit

#### TC-3.4: /start includes /token help
**Given**: Start command help text
**When**: Call cmd_start
**Then**: Help text includes "/token"
**Priority**: P1
**Type**: Unit

---

## Test Files to Create

### Primary Test File
**Path**: `tests/unit/test_story_6_3_token_detail.py`
**Size**: ~250-300 lines
**Structure**:
- Test fixtures (mock_update, mock_context, mock_token_response)
- TestGetToken class (3 tests)
- TestCmdToken class (5 tests)
- TestCommandRegistration class (4 tests)

### Test Fixtures
All fixtures defined inline (following project pattern from test_story_6_2_tokens_list.py)

---

## Test Data Factories

### TokenDetailFactory
```python
class TokenDetailFactory:
    """Factory for creating test token detail data."""

    @staticmethod
    def create(
        symbol: str = "ETH",
        name: str = "Ethereum",
        address: str = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
        price_usd: str = "3000.00",
        change_24h: str = "2.5",
        market_cap_usd: str = "360000000000",
        holder_count: int = 1234,
        volume_24h_usd: str = "15000000000",
    ) -> dict:
        """Create token detail with default values."""
        return {
            "symbol": symbol,
            "name": name,
            "address": address,
            "priceUsd": price_usd,
            "change24h": change_24h,
            "marketCapUsd": market_cap_usd,
            "holderCount": holder_count,
            "volume24hUsd": volume_24h_usd,
        }
```

---

## Formatter Tests (Optional)

### TC-F.1: format_large_number billions
**Given**: Value is 360,000,000,000
**When**: Call format_large_number(value)
**Then**: Returns "$360.0B"

### TC-F.2: format_large_number millions
**Given**: Value is 15,000,000,000
**When**: Call format_large_number(value)
**Then**: Returns "$15000.0M"

### TC-F.3: format_large_number thousands
**Given**: Value is 5,000
**When**: Call format_large_number(value)
**Then**: Returns "$5.0K"

---

## Expected Test Output

### Test Execution
```bash
pytest tests/unit/test_story_6_3_token_detail.py -v
```

### Expected Results
- **Total Tests**: 12
- **API Tests**: 3
- **Command Handler Tests**: 5
- **Registration Tests**: 4
- **Expected Failures**: All (RED phase - implementation not done)

---

## Implementation Checklist

### Before Tests Can Pass (GREEN Phase)

- [ ] **API Layer**
  - [ ] Add `get_token(address)` method to `api.py`
  - [ ] Method calls `/token/{address}` endpoint
  - [ ] Returns dict response
  - [ ] Handles both symbol and address inputs

- [ ] **Command Handler**
  - [ ] Add `cmd_token` to `commands/query.py`
  - [ ] Check authorization
  - [ ] Parse required argument
  - [ ] Call API method
  - [ ] Handle API errors
  - [ ] Format output message
  - [ ] Handle missing argument

- [ ] **Registration**
  - [ ] Export cmd_token in `commands/__all__`
  - [ ] Add CommandHandler in `register_handlers()`
  - [ ] Add BotCommand in `post_init()`
  - [ ] Add help text to cmd_start

- [ ] **Formatters** (if not exists)
  - [ ] Add `format_large_number()` to `utils/formatters.py`
  - [ ] Format billions with "B" suffix
  - [ ] Format millions with "M" suffix
  - [ ] Format thousands with "K" suffix

---

## Risk Assessment

### P1 Tests (Critical - Must Pass)
- All 12 tests are P1 priority
- Feature is core user functionality
- No P2 or P3 tests defined

### Edge Cases Covered
- Missing argument (usage hint)
- Unauthorized user (rejection)
- API error (error message)
- Both symbol and address inputs

---

## Notes

### Test Pattern Reference
- Follows `test_story_6_2_tokens_list.py` structure
- Uses Given-When-Then pattern
- Mocks API with AsyncMock
- Tests command registration and help text

### Language Requirements
- All user-facing messages in English (project convention)
- Test descriptions in English

### Test Isolation
- Each test is independent
- No shared state between tests
- Mocks reset for each test

---

## Next Steps

1. **RED Phase**: Run tests (all should fail)
   ```bash
   pytest tests/unit/test_story_6_3_token_detail.py -v
   ```

2. **GREEN Phase**: Implement features to pass tests
   - Implement API method
   - Implement command handler
   - Add registrations
   - Add formatters

3. **REFACTOR Phase**: Optimize code while tests pass

---

## Success Criteria

- All 12 tests pass
- Code coverage >= 90% for new code
- No linting errors
- Follows project conventions
- All acceptance criteria met
