# Story 6.1: ETH Price Query

## Story

**As a** **user**, I need to **query ETH real-time price via `/price` command** so that **I can understand the current market situation**.

## Acceptance Criteria

1. Add `get_eth_price()` method to `api.py`
2. Call `/eth-price` endpoint
3. Add `cmd_price` command handler to `commands/query.py`
4. Format output: current price, 24h change
5. Add unit tests

## Tasks / Subtasks

- [x] **Task 1: Implement get_eth_price() API method** (AC: #1, #2)
  - [x] Add `get_eth_price()` async method to `api.py`
  - [x] Call `/eth-price` endpoint (no parameters needed)
  - [x] Return standard dict response
  - [x] Follow existing `_get()` helper pattern

- [x] **Task 2: Implement cmd_price command handler** (AC: #3, #4)
  - [x] Add `cmd_price` async function to `commands/query.py`
  - [x] Check permission using `authorized()`
  - [x] Call `api.get_eth_price()` method
  - [x] Handle API error response
  - [x] Format output message with current price and 24h change
  - [x] Use English for all user-facing messages (project convention)

- [x] **Task 3: Update command registration and menu** (AC: #3)
  - [x] Export `cmd_price` in `commands/__init__.py` `__all__` list
  - [x] Add `CommandHandler("price", cmd_price)` in `register_handlers()`
  - [x] Add `BotCommand("price", "ETH price")` in `main.py` `post_init()`
  - [x] Add `/price` help text in `cmd_start` in `commands/query.py`

- [x] **Task 4: Add unit tests** (AC: #5)
  - [x] Create `tests/unit/test_story_6_1_eth_price.py`
  - [x] Test `get_eth_price()` method success
  - [x] Test `get_eth_price()` API error handling
  - [x] Test `cmd_price` normal flow with formatted output
  - [x] Test unauthorized user rejection
  - [x] Test API error message display
  - [x] Test command export in `__all__`
  - [x] Test command registration in bot commands
  - [x] Test `/start` includes `/price` in help text

## File List
- `api.py` - Added `get_eth_price()` method
- `commands/query.py` - Added `cmd_price` command handler
- `commands/__init__.py` - Added `cmd_price` export and `CommandHandler`
- `main.py` - Added `BotCommand("price", "ETH price")` to bot commands menu
- `tests/unit/test_story_6_1_eth_price.py` - Created (8 tests passing)
- `tests/unit/test_story_1_3_menu_help.py` - Updated expected commands count

## Change Log
- 2026-03-03: Story 6-1 implementation complete

  - Added `/price` command for ETH price query
  - Added `get_eth_price()` API method to `api.py`
  - Added `cmd_price` command handler to `commands/query.py`
  - Updated command registration in `commands/__init__.py`
  - Added bot command menu entry in `main.py`
  - Added unit tests with full coverage (8 tests)

## Dev Agent Record

### Agent Model Used
GLM-5

### Completion Notes List
- Implemented `get_eth_price()` API method
- Implemented `cmd_price` command handler with formatted output
- Registered `/price` command in bot menu
- Added unit tests covering success, error, and edge cases
- All 8 tests passing

### File List
- api.py
- commands/query.py
- commands/__init__.py
- main.py
- tests/unit/test_story_6_1_eth_price.py
- tests/unit/test_story_1_3_menu_help.py

## Dev Notes

### API Endpoint Details

Based on the Terminal Markets API pattern (from `api.py`), the `/eth-price` endpoint follows the existing `_get()` helper pattern:

```python
# api.py
async def get_eth_price(self) -> dict:
    """Get ETH real-time price"""
    return await self._get("/eth-price")
```

### Expected API Response Format

Based on similar API patterns in the project, the expected response structure:

```json
{
  "price": "3000.00",
  "change24h": "2.5"
}
```

### Message Format Reference

Based on the epics specification:

```
ETH Price

Current: $3,000.00
24h Change: +2.5%
```

Use existing formatter `format_usd()` from `utils/formatters.py` for price display.
Use `format_percent()` for percentage display with +/- sign.

### Implementation Pattern

Follow the existing command handler pattern from `commands/query.py`:

```python
async def cmd_price(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Query ETH price."""
    if not authorized(update):
        return
    api = _get_api()
    data = await api.get_eth_price()
    if "error" in data:
        await update.message.reply_text(f"Error: {data['error']}")
        return

    price = format_usd(data.get("price", "0"))
    change = format_percent(data.get("change24h", "0"))

    msg = f"""
ETH Price

Current: {price}
24h Change: {change}
"""
    await update.message.reply_text(msg)
```

### Project Structure Notes

- API methods go in: `api.py`
- Query commands go in: `commands/query.py`
- Command registration in: `commands/__init__.py`
- Bot command menu in: `main.py` `post_init()`
- Unit tests in: `tests/unit/test_story_6_1_eth_price.py`

### Previous Story Intelligence (Story 5-3)

From Story 5-3 (deposit-eth) implementation:

1. **No ConversationHandler needed**: Simple commands use single-step pattern
2. **UI Language**: All user-facing messages must be in English
3. **Test Structure**: Use Given-When-Then pattern with Mock fixtures
4. **Test File Naming**: `test_story_{epic}_{story}_{feature}.py`
5. **Code Quality**: Tests check command export and bot registration

### Git Intelligence

Recent commits show consistent patterns:
- `feat: Add /deposit command for depositing ETH to Vault (Story 5-3)`
- `feat: Add /pnl_history command for PnL trend query (Story 5-2)`
- `feat: Add /deposits command for deposit/withdrawal history query (Story 5-1)`

Follow this commit message pattern: `feat: Add /price command for ETH price query (Story 6-1)`

### Architecture Compliance

- Use async functions for all I/O operations (python-telegram-bot 21.x requirement)
- Use f-string for string formatting
- Use type annotations for better IDE support
- Follow existing error handling pattern with `{"error": ...}` dict check

### Testing Standards

From project context:
- Use `pytest` framework with `AsyncMock` and `MagicMock`
- Test file location: `tests/unit/test_story_6_1_eth_price.py`
- Follow Given-When-Then structure
- Mock the API using `monkeypatch.setattr("main.api", mock)`
- Test both success and error scenarios

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story 6.1]
- [Source: _bmad-output/project-context.md#Command Pattern]
- [Source: api.py - TerminalAPI class structure]
- [Source: commands/query.py - Existing command handlers]
- [Source: tests/unit/test_story_5_3_deposit_eth.py - Test pattern reference]
