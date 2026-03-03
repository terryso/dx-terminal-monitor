# Story 6.4: New Coin Launch Schedule

Status: done

## Story

As a user, I want to check the upcoming token launch schedule via the `/launches` command, so that I can stay informed about new tokens that will be available for trading.

## Acceptance Criteria

1. [x] Add `get_launch_schedule()` method to `api.py` that calls `/launch-schedule` endpoint
2. [x] Add `cmd_launches` command handler in `commands/query.py`
3. [x] Command format: `/launches` - no parameters required
4. [x] Format output: token name, launch time, status
5. [x] Handle empty results with appropriate message
6. [x] Register `/launches` command in Bot command menu
7. [x] Add unit tests for the new command

## Tasks / Subtasks

- [x] Task 1: Add API method (AC: #1)
  - [x] Add `get_launch_schedule()` method to `api.py` TerminalAPI class
  - [x] Call `/launch-schedule` endpoint with no parameters
  - [x] Return list of launch items
- [x] Task 2: Add command handler (AC: #2, #3, #4, #5)
  - [x] Add `cmd_launches` async function in `commands/query.py`
  - [x] Use standard permission check pattern (`authorized(update)`)
  - [x] Call `api.get_launch_schedule()`
  - [x] Handle error responses
  - [x] Handle empty results with "No upcoming launches" message
  - [x] Format output with token name, launch time, status
- [x] Task 3: Register command (AC: #6)
  - [x] Add `/launches` to Bot command menu in `main.py` `post_init()`
  - [x] Add command handler registration in `main.py`
  - [x] Update `/start` help text in `commands/query.py`
  - [x] Update `test_post_init_sets_commands` test
- [x] Task 4: Add unit tests (AC: #7)
  - [x] Create `tests/unit/test_story_6_4_launch_schedule.py`
  - [x] Test success case with mock API response
  - [x] Test error handling case
  - [x] Test empty results case

## Dev Notes

### Architecture Patterns

This story follows the established patterns from Story 6.1-6.3:
- API methods go in `api.py` TerminalAPI class
- Command handlers go in `commands/query.py`
- Use lazy import pattern: `from main import api` inside function
- Use standard permission check: `if not authorized(update): return`

### Source Tree Components to Touch

1. `/Users/nick/projects/dx-terminal-monitor/api.py` - Add `get_launch_schedule()` method
2. `/Users/nick/projects/dx-terminal-monitor/commands/query.py` - Add `cmd_launches` handler
3. `/Users/nick/projects/dx-terminal-monitor/main.py` - Register command and update menu
4. `/Users/nick/projects/dx-terminal-monitor/tests/unit/test_story_6_4_launch_schedule.py` - New test file
5. `/Users/nick/projects/dx-terminal-monitor/tests/unit/test_story_1_3_menu_help.py` - Update expected commands

### API Endpoint Details

Based on epics.md specification:
- Endpoint: `/launch-schedule`
- Method: GET
- Parameters: None required
- Expected response: List of launch items with token info

### Message Format (from epics.md)

```
New Coin Launch Schedule

1. NEWTOKEN
   Launch Time: 2026-03-05 12:00 UTC
   Status: Coming Soon

2. ANOTHER
   Launch Time: 2026-03-10 08:00 UTC
   Status: Planned
```

### Project Structure Notes

- Follows standard command pattern in `commands/query.py`
- API client pattern in `api.py` using `_get()` helper
- Test file naming: `test_story_6_4_launch_schedule.py`

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-6.4]
- [Source: _bmad-output/project-context.md#Telegram-Bot-命令结构]
- [Source: docs/architecture.md#REST-API-方法（只读）]
- [Source: _bmad-output/implementation-artifacts/6-3-token-detail.md] - Previous story for patterns

### Previous Story Intelligence (Story 6-3: Token Detail)

Key patterns established:
1. API method pattern:
   ```python
   async def get_token(self, address_or_symbol: str) -> dict:
       return await self._get(f"/token/{address_or_symbol}")
   ```

2. Command handler pattern:
   ```python
   async def cmd_token(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
       if not authorized(update):
           return
       if not ctx.args:
           await update.message.reply_text("Usage: /token <symbol>")
           return
       api = _get_api()
       data = await api.get_token(ctx.args[0])
       if "error" in data:
           await update.message.reply_text(f"Error: {data['error']}")
           return
       # Format output...
   ```

3. Lazy import pattern for avoiding circular imports:
   ```python
   def _get_api():
       from main import api
       return api
   ```

4. Test file pattern in `tests/unit/test_story_6_3_token_detail.py`

5. Updated test in `test_story_1_3_menu_help.py` to include new command

### Git Intelligence (Recent Commits)

- `73a478c` - fix: Use correct API fields for token detail display
- `3c63d30` - feat: Add /token command for token detail query (Story 6-3)
- `cfd7d30` - feat: Add /tokens command for tradeable tokens list (Story 6-2)

Key learnings:
- Always verify actual API field names before formatting output
- Follow existing command patterns exactly
- Update both menu registration and help text
- Test file naming follows `test_story_X_Y_description.py` pattern

## Dev Agent Record

### Agent Model Used

GLM-5 (via Claude Code)

### Debug Log References

N/A

### Completion Notes List

- Story 6-4 implementation was already complete - verified all code in place
- `get_launch_schedule()` method exists in `api.py` (lines 119-121)
- `cmd_launches` handler exists in `commands/query.py` (lines 504-536)
- `/launches` command registered in `main.py` post_init() (line 54)
- Command handler registered in `commands/__init__.py` (line 50)
- All 14 unit tests pass for story 6-4
- All 407 unit tests pass - no regressions
- Command is included in help text and bot menu

### File List

- `api.py` - Added `get_launch_schedule()` method
- `commands/query.py` - Added `cmd_launches` command handler
- `commands/__init__.py` - Exported and registered `cmd_launches`
- `main.py` - Registered `/launches` command in bot menu
- `tests/unit/test_story_6_4_launch_schedule.py` - New test file (14 tests)
- `tests/unit/test_story_1_3_menu_help.py` - Updated to include `launches` in expected commands
