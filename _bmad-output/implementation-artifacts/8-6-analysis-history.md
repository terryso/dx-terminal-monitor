# Story 8.6: 分析历史记录与网页查看

---
title: Story 8.6 - 分析历史记录与网页查看
epic: Epic 8 - AI 策略顾问
created: 2026-03-04
status: done
priority: P2
---

## 概述

实现 AI 分析历史记录的存储和查看功能，帮助用户调试提示词和理解 AI 的决策过程。

---

## 验收标准

### AC1: 配置项

- [ ] `config.py` 添加配置项：
  - `ADVISOR_HISTORY_ENABLED` (默认 `false`)
  - `ADVISOR_HISTORY_MAX` (默认 `30`)
  - `ADVISOR_SURGE_DOMAIN` (默认 `dx-advisor.surge.sh`)
- [ ] 配置可通过环境变量覆盖

### AC2: 分析数据存储

- [ ] 每次分析完成自动保存到 `data/advisor_history.json`
- [ ] 存储内容包含：
  ```json
  {
    "id": "a3f2b1",
    "timestamp": "2026-03-04T16:20:04",
    "request": "发送给 LLM 的完整提示词（system + user message）",
    "response": "LLM 原始 JSON 响应",
    "suggestions": [...],
    "executed": false,
    "executed_at": null
  }
  ```
- [ ] 最多保留 `ADVISOR_HISTORY_MAX` 条记录，超出自动删除最旧记录
- [ ] 执行建议后更新 `executed` 和 `executed_at` 字段

### AC3: 静态网页

- [ ] 创建 `data/advisor-web/` 目录存放静态文件
- [ ] `index.html` - 单页应用
- [ ] 页面通过 JavaScript 加载 `advisor_history.json`
- [ ] 功能要求：
  - [ ] 时间线展示历史记录列表
  - [ ] 点击记录查看详情
  - [ ] 完整提示词展示（带格式化）
  - [ ] LLM 响应展示
  - [ ] 解析后的建议列表
  - [ ] 响应式设计，支持移动端

### AC4: 条件同步和推送

- [ ] **未启用时** (`ADVISOR_HISTORY_ENABLED=false`)：
  - [ ] 仍然保存历史记录到本地
  - [ ] 不同步到 surge
  - [ ] 不附加 web 链接
- [ ] **启用时** (`ADVISOR_HISTORY_ENABLED=true`)：
  - [ ] 分析完成后自动同步 JSON 到 surge.sh
  - [ ] 推送建议时附加查看链接
  - [ ] 同步失败时记录日志，不影响主流程

---

## 文件清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `advisor_history.py` | 新建 | 分析历史存储模块 |
| `advisor.py` | 修改 | 在 analyze() 中添加保存逻辑 |
| `advisor_monitor.py` | 修改 | 添加同步和链接 |
| `data/advisor-web/index.html` | 新建 | 静态网页 |

---

## 技术实现

### 1. advisor_history.py（新建）

```python
"""
Analysis History Storage Module for Story 8.6

Stores AI analysis history with full request/response for debugging.
"""

import json
import logging
import shutil
import subprocess
import uuid
from datetime import datetime
from pathlib import Path

from config import ADVISOR_HISTORY_MAX, ADVISOR_SURGE_DOMAIN

logger = logging.getLogger(__name__)

# File paths
HISTORY_FILE = Path("data/advisor_history.json")
WEB_DIR = Path("data/advisor-web")


def save_analysis(request: str, response: str, suggestions: list) -> str:
    """Save analysis record and return record ID.

    Args:
        request: Full prompt sent to LLM (system + user message)
        response: Raw LLM response
        suggestions: Parsed suggestions list

    Returns:
        8-character record ID
    """
    history = load_history()

    record_id = uuid.uuid4().hex[:8]
    record = {
        "id": record_id,
        "timestamp": datetime.now().isoformat(),
        "request": request,
        "response": response,
        "suggestions": suggestions,
        "executed": False,
        "executed_at": None
    }

    history.insert(0, record)

    # Limit records
    if len(history) > ADVISOR_HISTORY_MAX:
        history = history[:ADVISOR_HISTORY_MAX]

    _save_history(history)
    logger.info(f"Saved analysis record: {record_id}")
    return record_id


def load_history() -> list:
    """Load analysis history from file."""
    if not HISTORY_FILE.exists():
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Failed to load history: {e}")
        return []


def _save_history(history: list):
    """Save history to file."""
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def mark_executed(record_id: str):
    """Mark a record as executed.

    Args:
        record_id: The record ID to mark
    """
    history = load_history()
    for record in history:
        if record["id"] == record_id:
            record["executed"] = True
            record["executed_at"] = datetime.now().isoformat()
            break
    _save_history(history)
    logger.info(f"Marked record as executed: {record_id}")


def sync_to_surge():
    """Sync JSON file to surge.sh.

    Logs failure but does not raise exception.
    """
    try:
        WEB_DIR.mkdir(parents=True, exist_ok=True)

        if HISTORY_FILE.exists():
            shutil.copy(HISTORY_FILE, WEB_DIR / "advisor_history.json")

        result = subprocess.run(
            ["surge", str(WEB_DIR), ADVISOR_SURGE_DOMAIN],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            logger.info(f"Synced to surge.sh: https://{ADVISOR_SURGE_DOMAIN}")
        else:
            logger.warning(f"Surge sync failed: {result.stderr}")

    except FileNotFoundError:
        logger.warning("Surge CLI not installed, skip sync")
    except subprocess.TimeoutExpired:
        logger.warning("Surge sync timeout")
    except Exception as e:
        logger.error(f"Surge sync error: {e}")


def get_view_url() -> str:
    """Get the URL to view analysis history."""
    return f"https://{ADVISOR_SURGE_DOMAIN}"
```

### 2. advisor.py 修改

在 `analyze()` 方法中添加保存逻辑：

```python
# advisor.py - 在 analyze() 方法末尾添加

async def analyze(self) -> list[Suggestion]:
    try:
        data = await self.collector.collect()
        formatted_data = self.collector.format_for_llm(data)

        # Get full system prompt
        system_prompt = _load_system_prompt()

        # Build full request content (for saving)
        full_request = f"{system_prompt}\n\n{formatted_data}"

        # Call LLM
        response = await self.llm.chat(system_prompt, formatted_data)

        if response.startswith("Error:"):
            logger.error("LLM analysis failed: %s", response)
            return []

        suggestions = self._parse_suggestions(response)

        # ========== 新增：保存分析记录 ==========
        from advisor_history import save_analysis
        record_id = save_analysis(
            request=full_request,
            response=response,
            suggestions=[s.__dict__ for s in suggestions]
        )
        self._last_record_id = record_id
        # ========================================

        return suggestions[:self.MAX_SUGGESTIONS]

    except Exception as e:
        logger.error("Analysis failed: %s", e)
        return []
```

添加 `last_record_id` 属性：

```python
class StrategyAdvisor:
    def __init__(self, llm: LLMClient, api: TerminalAPI):
        self.llm = llm
        self.api = api
        self.collector = StrategyDataCollector(api)
        self._last_record_id: str | None = None

    @property
    def last_record_id(self) -> str | None:
        return self._last_record_id
```

### 3. advisor_monitor.py 修改

添加导入和条件逻辑：

```python
# advisor_monitor.py - 添加导入
from config import ADVISOR_HISTORY_ENABLED
from advisor_history import sync_to_surge, get_view_url

# 修改 push_suggestions 函数
async def push_suggestions(
    chat_id: int,
    suggestions: list[Suggestion] | list[dict],
    context: dict,
    bot: Bot
) -> str:
    # ... 现有逻辑 ...

    # 构建消息
    message = format_suggestions_message(suggestions, context)

    # ========== 新增：只有启用时才同步和附加链接 ==========
    if ADVISOR_HISTORY_ENABLED:
        sync_to_surge()
        message += f"\n\n📎 <a href='{get_view_url()}'>查看详细分析历史</a>"
    # ====================================================

    # 发送消息
    await bot.send_message(
        chat_id,
        text=message,
        reply_markup=keyboard,
        parse_mode="HTML",
        disable_web_page_preview=True
    )

    logger.info(f"Pushed {len(suggestions)} suggestions (request_id={request_id})")
    return request_id
```

### 4. data/advisor-web/index.html（新建）

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Advisor Analysis History</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #1a1a2e;
            color: #eee;
            padding: 20px;
            line-height: 1.6;
        }
        .container { max-width: 900px; margin: 0 auto; }
        h1 { margin-bottom: 10px; color: #00d9ff; }
        .subtitle { color: #888; margin-bottom: 20px; }

        .record {
            background: #16213e;
            border-radius: 8px;
            margin-bottom: 15px;
            overflow: hidden;
        }
        .record-header {
            padding: 15px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .record-header:hover { background: #1f2b47; }
        .record-meta { display: flex; gap: 15px; align-items: center; }
        .record-time { color: #888; font-size: 14px; }
        .record-status {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
        }
        .status-pending { background: #f39c12; color: #000; }
        .status-executed { background: #27ae60; color: #fff; }

        .detail {
            display: none;
            padding: 20px;
            background: #0f0f23;
            border-top: 1px solid #2a3a5a;
        }
        .detail.active { display: block; }

        .section { margin-top: 20px; }
        .section:first-child { margin-top: 0; }
        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .section-title {
            color: #00d9ff;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .toggle-btn {
            background: #2a3a5a;
            color: #00d9ff;
            border: none;
            padding: 6px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
        }
        .toggle-btn:hover { background: #3a4a6a; }

        .content-box {
            background: #0f0f23;
            border-radius: 6px;
            padding: 15px;
            white-space: pre-wrap;
            font-family: 'SF Mono', 'Fira Code', monospace;
            font-size: 12px;
            max-height: 400px;
            overflow-y: auto;
            word-break: break-word;
        }
        .content-box::-webkit-scrollbar { width: 8px; }
        .content-box::-webkit-scrollbar-track { background: #1a1a2e; }
        .content-box::-webkit-scrollbar-thumb { background: #3a4a6a; border-radius: 4px; }

        .suggestions { list-style: none; }
        .suggestion-item {
            padding: 12px 15px;
            background: #16213e;
            margin-bottom: 8px;
            border-radius: 6px;
            border-left: 3px solid #00d9ff;
        }
        .suggestion-item.add { border-left-color: #27ae60; }
        .suggestion-item.disable { border-left-color: #e74c3c; }
        .suggestion-action {
            font-weight: 600;
            margin-bottom: 5px;
            display: block;
        }
        .suggestion-action.add { color: #27ae60; }
        .suggestion-action.disable { color: #e74c3c; }
        .suggestion-detail { color: #aaa; font-size: 13px; margin: 3px 0; }
        .suggestion-reason {
            margin-top: 8px;
            padding-top: 8px;
            border-top: 1px dashed #2a3a5a;
            font-style: italic;
            color: #888;
        }

        .error { color: #e74c3c; text-align: center; padding: 40px; }
        .loading { color: #888; text-align: center; padding: 40px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 AI Advisor Analysis History</h1>
        <p class="subtitle">查看历史 AI 分析的完整提示词和响应</p>
        <div id="records" class="loading">Loading...</div>
    </div>

    <script>
        async function loadHistory() {
            const container = document.getElementById('records');
            try {
                const response = await fetch('advisor_history.json');
                if (!response.ok) throw new Error('Failed to load');
                const data = await response.json();
                renderRecords(data);
            } catch (e) {
                container.innerHTML = '<div class="error">Failed to load history data</div>';
            }
        }

        function renderRecords(records) {
            const container = document.getElementById('records');
            if (!records || records.length === 0) {
                container.innerHTML = '<div class="error">No analysis history found</div>';
                return;
            }

            container.innerHTML = records.map(record => `
                <div class="record" id="record-${record.id}">
                    <div class="record-header" onclick="toggleDetail('${record.id}')">
                        <div class="record-meta">
                            <span class="record-time">${formatTime(record.timestamp)}</span>
                            <span>${record.suggestions.length} suggestion(s)</span>
                        </div>
                        <span class="record-status ${record.executed ? 'status-executed' : 'status-pending'}">
                            ${record.executed ? 'Executed' : 'Pending'}
                        </span>
                    </div>
                    <div class="detail" id="detail-${record.id}">
                        <div class="section">
                            <div class="section-header">
                                <span class="section-title">📥 Request (Full Prompt)</span>
                                <button class="toggle-btn" onclick="event.stopPropagation(); toggleSection('request-${record.id}')">Show/Hide</button>
                            </div>
                            <div class="content-box" id="request-${record.id}" style="display: none;">${escapeHtml(record.request)}</div>
                        </div>
                        <div class="section">
                            <div class="section-header">
                                <span class="section-title">📤 LLM Response</span>
                                <button class="toggle-btn" onclick="event.stopPropagation(); toggleSection('response-${record.id}')">Show/Hide</button>
                            </div>
                            <div class="content-box" id="response-${record.id}" style="display: none;">${escapeHtml(record.response)}</div>
                        </div>
                        <div class="section">
                            <div class="section-header">
                                <span class="section-title">💡 Parsed Suggestions</span>
                            </div>
                            <ul class="suggestions">
                                ${record.suggestions.map(s => `
                                    <li class="suggestion-item ${s.action}">
                                        <span class="suggestion-action ${s.action}">[${s.action.toUpperCase()}]</span>
                                        ${s.content ? `<div class="suggestion-detail">Prompt: "${escapeHtml(s.content)}"</div>` : ''}
                                        ${s.strategy_id !== null ? `<div class="suggestion-detail">Strategy #${s.strategy_id}</div>` : ''}
                                        <div class="suggestion-detail">Priority: ${['LOW', 'MEDIUM', 'HIGH'][s.priority] || 'MEDIUM'} | Validity: ${s.expiry_hours ? s.expiry_hours + 'h' : 'Permanent'}</div>
                                        <div class="suggestion-reason">${escapeHtml(s.reason)}</div>
                                    </li>
                                `).join('')}
                            </ul>
                        </div>
                    </div>
                </div>
            `).join('');
        }

        function formatTime(iso) {
            const date = new Date(iso);
            return date.toLocaleString('zh-CN', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
            });
        }

        function escapeHtml(text) {
            if (!text) return '';
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        function toggleDetail(id) {
            document.getElementById(`detail-${id}`).classList.toggle('active');
        }

        function toggleSection(id) {
            const el = document.getElementById(id);
            el.style.display = el.style.display === 'none' ? 'block' : 'none';
        }

        loadHistory();
    </script>
</body>
</html>
```

---

## 配置项

| 配置项 | 环境变量 | 默认值 | 说明 |
|--------|----------|--------|------|
| 启用分析历史 | `ADVISOR_HISTORY_ENABLED` | `false` | 是否启用分析历史记录功能 |
| 历史记录最大数 | `ADVISOR_HISTORY_MAX` | `30` | 保存的最大记录数 |
| Surge 域名 | `ADVISOR_SURGE_DOMAIN` | `dx-advisor.surge.sh` | 静态网页域名 |

### config.py 添加

```python
# AI Advisor History
ADVISOR_HISTORY_ENABLED = os.getenv("ADVISOR_HISTORY_ENABLED", "false").lower() == "true"
ADVISOR_HISTORY_MAX = int(os.getenv("ADVISOR_HISTORY_MAX", "30"))
ADVISOR_SURGE_DOMAIN = os.getenv("ADVISOR_SURGE_DOMAIN", "dx-advisor.surge.sh")
```

### .env 示例

```env
# AI Advisor History (可选)
ADVISOR_HISTORY_ENABLED=true
ADVISOR_HISTORY_MAX=30
ADVISOR_SURGE_DOMAIN=your-domain.surge.sh
```

---

## 条件逻辑

### 保存历史记录

无论是否启用 web 查看，**都保存历史记录**（方便本地查看）：

```python
# advisor.py - analyze()
# 始终保存历史记录
from advisor_history import save_analysis
record_id = save_analysis(...)
```

### 同步和推送链接

只有启用时才同步和推送链接：

```python
# advisor_monitor.py - push_suggestions()

from config import ADVISOR_HISTORY_ENABLED
from advisor_history import sync_to_surge, get_view_url

# 只有启用时才同步和添加链接
if ADVISOR_HISTORY_ENABLED:
    sync_to_surge()
    message += f"\n\n📎 <a href='{get_view_url()}'>查看详细分析历史</a>"
```

---

## 首次部署

```bash
# 1. 安装 surge CLI（需要 Node.js）
npm install -g surge

# 2. 创建目录和初始文件
mkdir -p data/advisor-web
echo '[]' > data/advisor_history.json
cp data/advisor_history.json data/advisor-web/

# 3. 首次部署到 surge.sh
cd data/advisor-web
surge . dx-advisor.surge.sh
```

---

## 测试用例

### 单元测试

```python
# tests/unit/test_advisor_history.py

import pytest
import tempfile
from pathlib import Path


class TestAdvisorHistory:

    def test_save_analysis(self, tmp_path, monkeypatch):
        """测试保存分析记录"""
        monkeypatch.setattr("advisor_history.HISTORY_FILE", tmp_path / "history.json")
        from advisor_history import save_analysis, load_history

        record_id = save_analysis(
            request="test prompt",
            response='{"suggestions": []}',
            suggestions=[]
        )
        assert len(record_id) == 8

        history = load_history()
        assert len(history) == 1
        assert history[0]["id"] == record_id
        assert history[0]["request"] == "test prompt"
        assert history[0]["executed"] == False

    def test_max_records_limit(self, tmp_path, monkeypatch):
        """测试记录数量限制"""
        monkeypatch.setattr("advisor_history.HISTORY_FILE", tmp_path / "history.json")
        monkeypatch.setattr("advisor_history.MAX_RECORDS", 5)
        from advisor_history import save_analysis, load_history

        for i in range(8):
            save_analysis(f"prompt {i}", "{}", [])

        history = load_history()
        assert len(history) == 5
        # 最新记录在前
        assert "prompt 7" in history[0]["request"]

    def test_mark_executed(self, tmp_path, monkeypatch):
        """测试标记已执行"""
        monkeypatch.setattr("advisor_history.HISTORY_FILE", tmp_path / "history.json")
        from advisor_history import save_analysis, load_history, mark_executed

        record_id = save_analysis("test", "{}", [])
        mark_executed(record_id)

        history = load_history()
        record = next(r for r in history if r["id"] == record_id)
        assert record["executed"] == True
        assert record["executed_at"] is not None

    def test_load_empty_history(self, tmp_path, monkeypatch):
        """测试加载空历史"""
        monkeypatch.setattr("advisor_history.HISTORY_FILE", tmp_path / "history.json")
        from advisor_history import load_history

        history = load_history()
        assert history == []
```

---

## 风险与缓解

| 风险 | 缓解措施 |
|------|----------|
| surge CLI 未安装 | 检测并跳过同步，记录日志 |
| surge 同步失败 | 失败不影响主流程，仅记录日志 |
| JSON 文件过大 | 限制记录数量（30条） |
| 网页无法加载 | 错误处理和友好提示 |

---

## 预估复杂度

**中等**
