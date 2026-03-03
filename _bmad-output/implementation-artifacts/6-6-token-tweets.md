# Story 6.6: Token Tweets Query

Status: done

## Story

As a user, I want to check token-related tweets via the `/tweets <symbol>` command, so that I can understand market sentiment and latest updates for specific tokens.

## Acceptance Criteria

1. [x] Add `get_token_tweets(symbol, limit)` method to `api.py` that calls `/tweets/{tokenSymbol}` endpoint
2. [x] Add `cmd_tweets` command handler in `commands/query.py`
3. [x] Command format: `/tweets <symbol> [limit]` - symbol required, optional limit parameter (default 5)
4. [x] Format output: tweet content, author, time, link
5. [x] Handle missing symbol with usage hint
6. [x] Handle empty results with appropriate message
7. [x] Register `/tweets` command in Bot command menu
8. [x] Add unit tests for the new command

## Tasks / Subtasks

- [x] Task 1: Add API method (AC: #1)
  - [x] Add `get_token_tweets(symbol: str, limit: int = 5)` method to `api.py` TerminalAPI class
  - [x] Call `/tweets/{symbol}` endpoint with `limit` query parameter
  - [x] Return list of tweet items
- [x] Task 2: Add command handler (AC: #2, #3, #4, #5, #6)
  - [x] Add `cmd_tweets` async function in `commands/query.py`
  - [x] Use standard permission check pattern (`authorized(update)`)
  - [x] Parse required symbol argument
  - [x] Parse optional limit argument (default 5)
  - [x] Handle missing symbol with usage hint: "Usage: /tweets <symbol> [limit]"
  - [x] Call `api.get_token_tweets(symbol, limit)`
  - [x] Handle error responses
  - [x] Handle empty results with "No tweets found for {symbol}" message
  - [x] Format output with tweet content, author, time, link
- [x] Task 3: Register command (AC: #7)
  - [x] Add `/tweets` to Bot command menu in `main.py` `post_init()`
  - [x] Add command handler registration in `commands/__init__.py`
  - [x] Update `/start` help text in `commands/query.py`
  - [x] Update `test_post_init_sets_commands` test
- [x] Task 4: Add unit tests (AC: #8)
  - [x] Create `tests/unit/test_story_6_6_token_tweets.py`
  - [x] Test success case with mock API response
  - [x] Test error handling case
  - [x] Test empty results case
  - [x] Test missing symbol case
  - [x] Test optional limit parameter

## Dev Notes

### Architecture Patterns

This story follows the established patterns from Story 6.1-6.5:
- API methods go in `api.py` TerminalAPI class
- Command handlers go in `commands/query.py`
- Use lazy import pattern: `from main import api` inside function
- Use standard permission check: `if not authorized(update): return`

### Source Tree Components to Touch

1. `/Users/nick/projects/dx-terminal-monitor/api.py` - Add `get_token_tweets(symbol, limit)` method
2. `/Users/nick/projects/dx-terminal-monitor/commands/query.py` - Add `cmd_tweets` handler
3. `/Users/nick/projects/dx-terminal-monitor/main.py` - Register command in bot menu
4. `/Users/nick/projects/dx-terminal-monitor/commands/__init__.py` - Export and register handler
5. `/Users/nick/projects/dx-terminal-monitor/tests/unit/test_story_6_6_token_tweets.py` - New test file
6. `/Users/nick/projects/dx-terminal-monitor/tests/unit/test_story_1_3_menu_help.py` - Update expected commands

### API Endpoint Details

Based on epics.md specification:
- Endpoint: `/tweets/{tokenSymbol}`
- Method: GET
- Path parameter: `tokenSymbol` (required) - e.g., "ETH"
- Query parameter: `limit` (optional, default 5)
- Expected response: List of tweet items with content, author, timestamp, link

### Message Format (from epics.md)

```
ETH Related Tweets

1. @VitalikButerin (2026-03-01)
   "Excited about the new ETH upgrade..."
   https://x.com/...

2. @ethereum (2026-03-01)
   "The merge is complete!"
   https://x.com/...

3. @ethenterprise (2026-02-28)
   "Enterprise adoption continues to grow..."
   https://x.com/...
```

### Project Structure Notes

- Follows standard command pattern in `commands/query.py`
- API client pattern in `api.py` using `_get()` helper
- Test file naming: `test_story_6_6_token_tweets.py`

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-6.6]
- [Source: _bmad-output/project-context.md#Telegram-Bot-命令结构]
- [Source: docs/architecture.md#REST-API-方法（只读）]
- [Source: _bmad-output/implementation-artifacts/6-5-leaderboard.md] - Previous story for patterns

### Previous Story Intelligence (Story 6-5: Leaderboard)

Key patterns established:
1. API method pattern:
   ```python
   async def get_leaderboard(self, limit: int = 10) -> list:
       """Get vault leaderboard."""
       return await self._get("/leaderboard", {"limit": limit})
   ```

2. Command handler pattern:
   ```python
   async def cmd_leaderboard(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
       if not authorized(update):
           return
       api = _get_api()
       data = await api.get_leaderboard(limit)
       if isinstance(data, dict) and "error" in data:
           await update.message.reply_text(f"Error: {data['error']}")
           return
       if not data:
           await update.message.reply_text("No leaderboard data available")
           return
       # Format output...
   ```

3. Lazy import pattern for avoiding circular imports:
   ```python
   def _get_api():
       from main import api
       return api
   ```

4. Test file pattern in `tests/unit/test_story_6_5_leaderboard.py`

5. Register command in two places:
   - `main.py` `post_init()` - Bot command menu
   - `commands/__init__.py` - Handler registration and __all__ export

### Git Intelligence (Recent Commits)

- `ad82cb9` - feat: Add /leaderboard command for vault leaderboard (Story 6-5)
- `c310b5a` - feat: Add /launches command for token launch schedule (Story 6-4)
- `73a478c` - fix: Use correct API fields for token detail display
- `514fb62` - perf: Optimize token query with cache and restore proxy support

Key learnings:
- Always verify actual API field names before formatting output
- Follow existing command patterns exactly
- Update both menu registration and help text
- Test file naming follows `test_story_X_Y_description.py` pattern
- Handle both list and dict responses from API

### Implementation Checklist

1. Add `get_token_tweets(symbol: str, limit: int = 5)` to `api.py`:
   ```python
   async def get_token_tweets(self, symbol: str, limit: int = 5) -> list:
       """Get token-related tweets."""
       return await self._get(f"/tweets/{symbol}", {"limit": limit})
   ```

2. Add `cmd_tweets` to `commands/query.py`:
   ```python
   async def cmd_tweets(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
       """Query token-related tweets."""
       if not authorized(update):
           return

       # Check for required symbol argument
       if not ctx.args:
           await update.message.reply_text("Usage: /tweets <symbol> [limit]")
           return

       symbol = ctx.args[0].upper()

       # Parse optional limit argument
       limit = 5
       if len(ctx.args) > 1 and ctx.args[1].isdigit():
           limit = int(ctx.args[1])

       # Call API
       api = _get_api()
       data = await api.get_token_tweets(symbol, limit)

       # Handle API error
       if isinstance(data, dict) and "error" in data:
           await update.message.reply_text(f"Error: {data['error']}")
           return

       # Handle empty results
       if not data:
           await update.message.reply_text(f"No tweets found for {symbol}")
           return

       # Format output
       lines = [f"{symbol} Related Tweets\n"]
       for i, tweet in enumerate(data, 1):
           author = tweet.get("author", "?")
           content = tweet.get("content", "")
           timestamp = tweet.get("timestamp", "?")
           link = tweet.get("link", "")
           lines.append(f"{i}. @{author} ({timestamp})")
           lines.append(f'   "{content[:100]}..."' if len(content) > 100 else f'   "{content}"')
           if link:
               lines.append(f"   {link}")
           lines.append("")

       await update.message.reply_text("\n".join(lines).strip())
   ```

3. Update `commands/__init__.py`:
   - Add import: `cmd_tweets`
   - Add handler: `CommandHandler("tweets", cmd_tweets)`
   - Add to `__all__`: `'cmd_tweets'`

4. Update `main.py` `post_init()`:
   - Add `BotCommand("tweets", "Token-related tweets")`

5. Update `commands/query.py` `cmd_start` help text:
   - Add `/tweets <symbol> [limit] - Token-related tweets`

## Dev Agent Record

### Agent Model Used

Claude (GLM-5 via Claude Code)

### Debug Log References

None - implementation completed without issues.

### Completion Notes List

- 2026-03-03: Story 6-6 implementation completed.
  - Added `get_token_tweets(symbol, limit)` API method to `api.py`
  - Added `cmd_tweets` command handler in `commands/query.py`
  - Registered `/tweets` command in bot menu (`main.py`)
  - Added handler registration in `commands/__init__.py`
  - Updated `/start` help text to include `/tweets` command
  - Created comprehensive unit tests (18 tests, all passing)
  - Updated test expectations in `test_story_1_3_menu_help.py` and `test_code_quality.py`
  - All 441 unit tests pass

### File List

- `api.py` - Added `get_token_tweets(symbol, limit)` method
- `commands/query.py` - Added `cmd_tweets` handler and updated help text
- `commands/__init__.py` - Registered handler and added to exports
- `main.py` - Added `BotCommand("tweets", "Token-related tweets")`
- `tests/unit/test_story_6_6_token_tweets.py` - New test file (18 tests)
- `tests/unit/test_story_1_3_menu_help.py` - Updated expected commands list
- `tests/unit/test_code_quality.py` - Updated line limit assertion
