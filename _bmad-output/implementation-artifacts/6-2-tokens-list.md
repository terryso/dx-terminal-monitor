# Story 6.2: Tokens List Query

**Status: done**

## Story

**As a** **user**, I need to **query the list of tradeable tokens via `/tokens` command** so that **I can understand which tokens are available for trading**.

## Acceptance Criteria

1. Add `get_tokens()` method to `api.py`
2. Call `/tokens` endpoint
3. Add `cmd_tokens` command handler to `commands/query.py`
4. Format output: token symbol, name, price, 24h change
5. Support pagination: `/tokens 2`
6. Add unit tests

## Tasks / Subtasks

- [x] **Task 1: Implement get_tokens() API method** (AC: #1, #2)
  - [x] Add `get_tokens()` async method to `api.py`
  - [x] Call `/tokens` endpoint (no parameters needed for basic list)
  - [x] Consider optional pagination support (page/limit parameters)
  - [x] Return standard dict response

- [x] **Task 2: Implement cmd_tokens command handler** (AC: #3, #4, #5)
  - [x] Add `cmd_tokens` async function to `commands/query.py`
  - [x] Check permission using `authorized()`
  - [x] Call `api.get_tokens()` method
  - [x] Handle API error response
  - [x] Format output message with token details (symbol, name, price, 24h change)
  - [x] Use English for all user-facing messages (project convention)
  - [x] Implement pagination support via optional page argument

- [x] **Task 3: Update command registration and menu** (AC: #3)
  - [x] Export `cmd_tokens` in `commands/__init__.py` `__all__` list
  - [x] Add `CommandHandler("tokens", cmd_tokens)` in `register_handlers()`
  - [x] Add `BotCommand("tokens", "Tradeable tokens")` in `main.py` `post_init()`
  - [x] Add `/tokens` help text in `cmd_start` in `commands/query.py`

- [x] **Task 4: Add unit tests** (AC: #6)
  - [x] Create `tests/unit/test_story_6_2_tokens_list.py`
  - [x] Test `get_tokens()` method success
  - [x] Test `get_tokens()` API error handling
  - [x] Test `cmd_tokens` normal flow with formatted output
  - [x] Test unauthorized user rejection
  - [x] Test API error message display
  - [x] Test pagination parameter parsing
  - [x] Test command export in `__all__`
  - [x] Test command registration in bot commands
  - [x] Test `/start` includes `/tokens` in help text

## File List
- `api.py` - Added `get_tokens()` method
- `commands/query.py` - Added `cmd_tokens` command handler
- `commands/__init__.py` - Added `cmd_tokens` export and `CommandHandler`
- `main.py` - Added `BotCommand("tokens", "Tradeable tokens")` to bot commands menu
- `tests/unit/test_story_6_2_tokens_list.py` - Created (11 unit tests)
- `_bmad-output/test-artifacts/atdd-checklist-6-2.md` - ATDD checklist

## Change Log
- 2026-03-03: Story 6-2 created (YOLO mode)

## Dev Agent Record

### Agent Model Used
{{agent_model_name_version}}

### Completion Notes List
- Ultimate context analysis completed - comprehensive developer guide created

### File List
- _bmad-output/implementation-artifacts/6-2-tokens-list.md

## Dev Notes

### API Endpoint Details

Based on the Terminal Markets API pattern (from `api.py`), the `/tokens` endpoint follows the existing `_get()` helper pattern:

```python
# api.py
async def get_tokens(self, page: int = 1, limit: int = 10) -> dict:
    """Get tradeable tokens list."""
    return await self._get("/tokens", {"page": page, "limit": limit})
```

### Expected API Response Format

Based on similar API patterns in the project and the epics specification, the expected response structure:

```json
{
  "items": [
    {
      "symbol": "ETH",
      "name": "Ethereum",
      "priceUsd": "3000.00",
      "change24h": "2.5"
    },
    {
      "symbol": "USDC",
      "name": "USD Coin",
      "priceUsd": "1.00",
      "change24h": "0.1"
    }
  ],
  "total": 50,
  "page": 1,
  "limit": 10
}
```

### Message Format Reference

Based on the epics specification:

```
Tradeable Tokens (1-10)

1. ETH - Ethereum
   Price: $3,000 | 24h: +2.5%

2. USDC - USD Coin
   Price: $1.00 | 24h: +0.1%

...
```

Use existing formatter `format_usd()` from `utils/formatters.py` for price display.
Use `format_percent()` for percentage display with +/- sign.

### Implementation Pattern

Follow the existing command handler pattern from `commands/query.py`:

```python
async def cmd_tokens(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Query tradeable tokens list."""
    if not authorized(update):
        return

    # Parse optional page argument (default 1)
    page = 1
    if ctx.args and ctx.args[0].isdigit():
        page = int(ctx.args[0])

    # Call API
    api = _get_api()
    data = await api.get_tokens(page)

    # Handle API error
    if "error" in data:
        await update.message.reply_text(f"Error: {data['error']}")
        return

    # Get items list
    items = data.get("items", [])
    if not items:
        await update.message.reply_text("No tokens available")
        return

    # Calculate display range
    total = data.get("total", 0)
    limit = data.get("limit", 10)
    start_num = (page - 1) * limit + 1
    end_num = min(page * limit, total)

    # Format output
    lines = [f"Tradeable Tokens ({start_num}-{end_num})\n"]
    for i, token in enumerate(items, 1):
        symbol = token.get("symbol", "?")
        name = token.get("name", "?")
        price = format_usd(token.get("priceUsd", "0"))
        change = format_percent(token.get("change24h", "0"))
        lines.append(f"{i}. {symbol} - {name}")
        lines.append(f"   Price: {price} | 24h: {change}\n")

    await update.message.reply_text("\n".join(lines))
```

### Project Structure Notes

- API methods go in: `api.py`
- Query commands go in: `commands/query.py`
- Command registration in: `commands/__init__.py`
- Bot command menu in: `main.py` `post_init()`
- Unit tests in: `tests/unit/test_story_6_2_tokens_list.py`

### Previous Story Intelligence (Story 6-1)

From Story 6-1 (ETH price) implementation:

1. **Simple pattern**: Query commands use straightforward `_get_api()` pattern
2. **UI Language**: All user-facing messages must be in English
3. **Test Structure**: Use Given-When-Then pattern with Mock fixtures
4. **Test File Naming**: `test_story_{epic}_{story}_{feature}.py`
5. **Code Quality**: Tests check command export and bot registration
6. **API Response**: `get_eth_price()` returns dict with `priceUsd` field (actual API field name)

### Git Intelligence

Recent commits show consistent patterns:
- `feat: Add /price command for ETH price query (Story 6-1)`
- `feat: Add /deposit command for depositing ETH to Vault (Story 5-3)`
- `feat: Add /pnl_history command for PnL trend query (Story 5-2)`

Follow this commit message pattern: `feat: Add /tokens command for tradeable tokens list query (Story 6-2)`

### Architecture Compliance

- Use async functions for all I/O operations (python-telegram-bot 21.x requirement)
- Use f-string for string formatting
- Use type annotations for better IDE support
- Follow existing error handling pattern with `{"error": ...}` dict check

### Testing Standards

From project context:
- Use `pytest` framework with `AsyncMock` and `MagicMock`
- Test file location: `tests/unit/test_story_6_2_tokens_list.py`
- Follow Given-When-Then structure
- Mock the API using `monkeypatch.setattr("main.api", mock)`
- Test both success and error scenarios

- Test pagination parameter parsing

### References
- [Source: _bmad-output/planning-artifacts/epics.md#Story 6.2]
- [Source: _bmad-output/project-context.md#Command Pattern]
- [Source: api.py - TerminalAPI class structure]
- [Source: commands/query.py - Existing command handlers]
- [Source: tests/unit/test_story_6_1_eth_price.py - Test pattern reference]
