---
stepsCompleted:
  - step-01-preflight-and-context
  - step-02-generation-mode
  - step-03-test-strategy
  - step-04-generate-tests

  - step-05-verify-red-phase

lastStep: step-06-completion

inputDocuments:
  - /Users/nick/projects/dx-terminal-monitor/_bmad-output/implementation-artifacts/8-6-analysis-history.md
  - /Users/nick/projects/dx-terminal-monitor/_bmad-output/test-artifacts/atdd-checklist-8-6.md
---

## Summary

生成 Mode: AI Generation (backend stack)
Primary Test Level: Unit tests
Stack Type: backend (Python with pytest)

## Test Files Created

1. **test_story_8_6_analysis_history.py** - 416 lines
   - 37 test methods covering AC1-AC4
   - All tests expected to FAIL (RED phase)

## Test Execution Results
```
pytest tests/unit/test_story_8_6_analysis_history.py -v --tb=short
```
**Output:**
```
FAILED (errors=37)
- Import errors: advisor_history module not found (expected - RED phase)
- Config ADVISOR_HISTORY_* items not found (expected - RED phase)
- Web directory/files not found (expected - RED phase)
```

All 37 tests failed with clear error messages indicating missing implementation.

## Implementation Checklist

### Test: test_advisor_history_enabled_config_exists
**Tasks to make pass:**
- [ ] Add `ADVISOR_HISTORY_ENABLED` to config.py (default: `false`)
- [ ] Add `ADVISOR_HISTORY_MAX` to config.py (default: `30`)
- [ ] Add `ADVISOR_SURGE_DOMAIN` to config.py (default: `dx-advisor.surge.sh`)

### Test: test_save_analysis_creates_record_with_correct_structure
**Tasks to make pass:**
- [ ] Create `advisor_history.py` module with `save_analysis()` function
- [ ] Create `data/advisor_history.json` on save
- [ ] Generate 8-character record ID
- [ ] Save record with: id, timestamp, request, response, suggestions, executed, executed_at

- [ ] Run test: `pytest tests/unit/test_story_8_6_analysis_history.py -v`

### Test: test_load_empty_history_returns_empty_list
**Tasks to make pass:**
- [ ] Add `load_history()` to `advisor_history.py`
- [ ] Handle missing file gracefully (return [])
- [ ] Handle JSON decode errors gracefully (return [])
- [ ] Run test: `pytest tests/unit/test_story_8_6_analysis_history.py -v`

### Test: test_mark_executed_updates_record
**Tasks to make pass:**
- [ ] Add `mark_executed()` to `advisor_history.py`
- [ ] Set `executed = True`
- [ ] Set `executed_at` to current timestamp
- [ ] Run test: `pytest tests/unit/test_story_8_6_analysis_history.py -v`

### Test: test_max_records_limit_enforcement
**Tasks to make pass:**
- [ ] When `len(history) > ADVISOR_HISTORY_MAX`, remove oldest records
- [ ] Run test: `pytest tests/unit/test_story_8_6_analysis_history.py -v`

### Test: test_sync_to_surge_success
**Tasks to make pass:**
- [ ] Add `sync_to_surge()` to `advisor_history.py`
- [ ] Create `data/advisor-web/` directory
- [ ] Copy `advisor_history.json` to web directory
- [ ] Run surge CLI command
- [ ] Log success on completion
- [ ] Run test: `pytest tests/unit/test_story_8_6_analysis_history.py -v`

### Test: test_sync_to_surge_fails_gracefully
**Tasks to make pass:**
- [ ] Handle FileNotFoundError (surge CLI not installed) - log warning
- [ ] Handle subprocess.TimeoutExpired - log warning
- [ ] Handle general exceptions - log error
- [ ] Run test: `pytest tests/unit/test_story_8_6_analysis_history.py -v`

### Test: test_get_view_url_returns_correct_url
**Tasks to make pass:**
- [ ] Add `get_view_url()` to `advisor_history.py`
- [ ] Return `https://{ADVISOR_SURGE_DOMAIN}`
- [ ] Run test: `pytest tests/unit/test_story_8_6_analysis_history.py -v`

### Test: test_web_page_exists
**Tasks to make pass:**
- [ ] Create `data/advisor-web/index.html`
- [ ] Include responsive design (viewport meta tag)
- [ ] Include JavaScript to load `advisor_history.json`
- [ ] Include timeline view with click-to-expand details
- [ ] Run test: `pytest tests/unit/test_story_8_6_analysis_history.py -v`

### Test: test_push_suggestions_includes_web_link_when_enabled
**Tasks to make pass:**
- [ ] In `advisor_monitor.py`, import `ADVISOR_HISTORY_ENABLED`, `sync_to_surge`, `get_view_url`
- [ ] When `ADVISOR_HISTORY_ENABLED=True`:
  - [ ] Call `sync_to_surge()`
  - [ ] Append web link to message: `\n\n📎 <a href='{url}'>查看详细分析历史</a>`
- [ ] Run test: `pytest tests/unit/test_story_8_6_analysis_history.py -v`

### Test: test_push_suggestions_excludes_web_link_when_disabled
**Tasks to make pass:**
- [ ] When `ADVISOR_HISTORY_ENABLED=False`:
  - [ ] Do NOT call `sync_to_surge()`
  - [ ] Do NOT append web link to message
- [ ] Run test: `pytest tests/unit/test_story_8_6_analysis_history.py -v`

### Test: test_analyze_saves_history_record
**Tasks to make pass:**
- [ ] In `advisor.py`, import `save_analysis` from `advisor_history`
- [ ] Call `save_analysis()` after LLM analysis completes
- [ ] Store `last_record_id` property
- [ ] Run test: `pytest tests/unit/test_story_8_6_analysis_history.py -v`

## Files to Create/Modify
| File | Operation | Description |
|------|----------|-------------|
| `advisor_history.py` | Create | New module for history storage |
| `config.py` | Modify | Add 3 config items |
| `advisor.py` | Modify | Add save_analysis call in `analyze()` |
| `advisor_monitor.py` | Modify | Add sync/link logic in `push_suggestions()` |
| `data/advisor-web/index.html` | Create | Static web page |
| `data/advisor_history.json` | Create (runtime) | History data file |

## Running Tests

```bash
# Run all failing tests for this story
pytest tests/unit/test_story_8_6_analysis_history.py -v --tb=short

```

