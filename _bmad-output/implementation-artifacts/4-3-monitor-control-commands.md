# Story 4.3: 监控控制命令

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

作为**用户**,我需要**通过命令控制监控服务的开启/关闭**,以便**灵活管理推送**。

## Acceptance Criteria

1. 实现 `/monitor_start` 命令启动监控
2. 实现 `/monitor_stop` 命令停止监控
3. 实现 `/monitor_status` 命令查看状态
4. 管理员权限检查
5. Bot 启动时自动开始监控 (可配置)
6. 添加单元测试

## Tasks / Subtasks

- [x] **Task 1: 实现 /monitor_status 命令** (AC: #3, #4)
  - [x] 在 `main.py` 中添加 `cmd_monitor_status` 异步函数
  - [x] 使用 `is_admin()` 检查管理员权限
  - [x] 读取 `_monitor_instance.running` 状态
  - [x] 返回格式化状态消息 (运行中/已停止, 轮询间隔, 已处理活动数)
  - [x] 处理监控器未初始化的情况

- [x] **Task 2: 实现 /monitor_start 命令** (AC: #1, #4)
  - [x] 在 `main.py` 中添加 `cmd_monitor_start` 异步函数
  - [x] 使用 `is_admin()` 检查管理员权限
  - [x] 检查监控器是否已在运行
  - [x] 如果未运行,调用 `_monitor_instance.start_background()`
  - [x] 返回启动确认消息

- [x] **Task 3: 实现 /monitor_stop 命令** (AC: #2, #4)
  - [x] 在 `main.py` 中添加 `cmd_monitor_stop` 异步函数
  - [x] 使用 `is_admin()` 检查管理员权限
  - [x] 检查监控器是否已停止
  - [x] 如果运行中,调用 `_monitor_instance.stop()`
  - [x] 返回停止确认消息

- [x] **Task 4: 更新命令菜单** (AC: #1, #2, #3)
  - [x] 在 `post_init()` 中添加新命令到 BotCommand 列表
  - [x] 在 `/start` 帮助文本中添加新命令说明
  - [x] 注册新命令处理器到 `create_app()`

- [x] **Task 5: 添加环境变量配置** (AC: #5)
  - [x] 在 `.env.example` 中添加 `AUTO_START_MONITOR` 说明
  - [x] 更新 `config.py` 读取 `AUTO_START_MONITOR` (默认 true)
  - [x] 修改 `post_init()` 根据配置决定是否自动启动

- [x] **Task 6: 添加单元测试** (AC: #6)
  - [x] 创建 `tests/unit/test_story_4_3_monitor_commands.py`
  - [x] 测试 `/monitor_status` 运行中状态
  - [x] 测试 `/monitor_status` 已停止状态
  - [x] 测试 `/monitor_start` 启动成功
  - [x] 测试 `/monitor_start` 已运行情况
  - [x] 测试 `/monitor_stop` 停止成功
  - [x] 测试 `/monitor_stop` 已停止情况
  - [x] 测试非管理员权限拒绝

## Dev Notes

### 技术栈要求

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | >=3.12 | 主要开发语言 |
| python-telegram-bot | >=21.0 | Telegram Bot API |
| pytest | >=8.0 | 测试框架 |
| pytest-asyncio | >=0.23 | 异步测试支持 |

### 现有代码依赖

**monitor.py - ActivityMonitor 类 (已实现):**
```python
# monitor.py:17-136
class ActivityMonitor:
    def __init__(self, api: TerminalAPI, callback: Callable[[Dict[str, Any]], Any]):
        self.api = api
        self.callback = callback
        self.seen_ids: set[str] = set()
        self.poll_interval = self._get_poll_interval()
        self.running: bool = False
        self._task: asyncio.Task | None = None

    async def start(self):
        """启动监控循环 (阻塞)"""
        self.running = True
        # ...

    def stop(self):
        """停止监控循环"""
        self.running = False

    async def start_background(self) -> asyncio.Task:
        """在后台任务中启动监控"""
        self._task = asyncio.create_task(self.start())
        return self._task
```

**main.py - 全局监控器实例 (已实现):**
```python
# main.py:51-53
_monitor_instance = None
_notifier_instance = None

# main.py:295-300
async def post_init(app: Application):
    # ...
    global _notifier_instance, _monitor_instance
    _notifier_instance = TelegramNotifier(app.bot)
    _monitor_instance = ActivityMonitor(api, _on_new_activity)
    await _monitor_instance.start_background()
    logger.info("Activity monitor started with Telegram notifications")
```

**config.py - 权限检查 (已实现):**
```python
# config.py:40-48
def is_admin(user_id: int) -> bool:
    """检查用户是否为管理员（用于高风险操作）"""
    if not ADMIN_USERS:
        logger.warning("ADMIN_USERS not configured - admin check denied")
        return False
    return user_id in ADMIN_USERS
```

### 新增代码实现指南

**main.py - 监控控制命令:**
```python
async def cmd_monitor_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """查看监控服务状态。"""
    # Admin permission check
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("未授权: 仅管理员可查看监控状态")
        return

    # Check if monitor is initialized
    if _monitor_instance is None:
        await update.message.reply_text("监控服务未初始化")
        return

    # Get status
    status = "运行中" if _monitor_instance.running else "已停止"
    interval = _monitor_instance.poll_interval
    seen_count = len(_monitor_instance.seen_ids)

    await update.message.reply_text(
        f"📊 监控服务状态\n\n"
        f"状态: {status}\n"
        f"轮询间隔: {interval} 秒\n"
        f"已处理活动: {seen_count} 个"
    )


async def cmd_monitor_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """启动监控服务。"""
    # Admin permission check
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("未授权: 仅管理员可启动监控")
        return

    # Check if monitor is initialized
    if _monitor_instance is None:
        await update.message.reply_text("监控服务未初始化，请重启 Bot")
        return

    # Check if already running
    if _monitor_instance.running:
        await update.message.reply_text("监控服务已在运行中")
        return

    # Start monitor
    await _monitor_instance.start_background()
    logger.info(f"Admin {update.effective_user.id} started activity monitor")

    await update.message.reply_text(
        "✅ 监控服务已启动\n"
        f"轮询间隔: {_monitor_instance.poll_interval} 秒"
    )


async def cmd_monitor_stop(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """停止监控服务。"""
    # Admin permission check
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("未授权: 仅管理员可停止监控")
        return

    # Check if monitor is initialized
    if _monitor_instance is None:
        await update.message.reply_text("监控服务未初始化")
        return

    # Check if already stopped
    if not _monitor_instance.running:
        await update.message.reply_text("监控服务已处于停止状态")
        return

    # Stop monitor
    _monitor_instance.stop()
    logger.info(f"Admin {update.effective_user.id} stopped activity monitor")

    await update.message.reply_text("⏹️ 监控服务已停止")
```

**config.py - 添加 AUTO_START_MONITOR:**
```python
# 在现有环境变量读取部分添加 (约第38行)
AUTO_START_MONITOR = os.getenv('AUTO_START_MONITOR', 'true').lower() == 'true'
```

**.env.example - 添加配置说明:**
```bash
# 监控控制配置
# Bot 启动时是否自动开始监控 (true/false, 默认 true)
AUTO_START_MONITOR=true
```

**main.py - 修改 post_init 支持配置:**
```python
async def post_init(app: Application):
    commands = [
        # ... existing commands ...
        BotCommand("monitor_status", "Check monitor status"),
        BotCommand("monitor_start", "Start activity monitor"),
        BotCommand("monitor_stop", "Stop activity monitor"),
    ]
    await app.bot.set_my_commands(commands)
    logger.info("Commands menu set")

    # Initialize notifier and monitor
    global _notifier_instance, _monitor_instance
    _notifier_instance = TelegramNotifier(app.bot)
    _monitor_instance = ActivityMonitor(api, _on_new_activity)

    # Auto-start monitor based on config
    if config.AUTO_START_MONITOR:
        await _monitor_instance.start_background()
        logger.info("Activity monitor auto-started with Telegram notifications")
    else:
        logger.info("Activity monitor initialized but not started (AUTO_START_MONITOR=false)")
```

**main.py - 更新 /start 帮助文本:**
```python
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not authorized(update):
        await update.message.reply_text("Unauthorized")
        return
    help_text = """
Terminal Markets Monitor

Commands:
/balance - View balance
/pnl - View PnL
/positions - View positions
/activity - Recent activity
/swaps - Recent swaps
/strategies - Active strategies
/vault - Vault info
/add_strategy <text> - Add new strategy
/disable_strategy <id> - Disable a specific strategy
/disable_all - Disable all active strategies
/pause - Pause Agent trading
/resume - Resume Agent trading
/update_settings - Update vault settings
/withdraw <amount> - Withdraw ETH to wallet
/monitor_status - Check monitor status
/monitor_start - Start activity monitor
/monitor_stop - Stop activity monitor
"""
    await update.message.reply_text(help_text)
```

**main.py - 注册命令处理器:**
```python
def create_app():
    """Create and configure the Telegram application."""
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).post_init(post_init).build()
    # ... existing handlers ...
    app.add_handler(CommandHandler("monitor_status", cmd_monitor_status))
    app.add_handler(CommandHandler("monitor_start", cmd_monitor_start))
    app.add_handler(CommandHandler("monitor_stop", cmd_monitor_stop))
    return app
```

### Project Structure Notes

**修改文件:**
```
dx-terminal-monitor/
├── main.py              # 修改 - 添加监控控制命令
├── config.py            # 修改 - 添加 AUTO_START_MONITOR
└── .env.example         # 修改 - 添加 AUTO_START_MONITOR 说明
```

**新增测试文件:**
```
tests/
└── unit/
    └── test_story_4_3_monitor_commands.py  # 新增 - 监控命令测试
```

### 与其他 Story 的关系

**前置依赖:**
- **Story 4-1** - 提供了 `ActivityMonitor` 类和 `start()`, `stop()`, `start_background()` 方法
- **Story 4-2** - 提供了 `TelegramNotifier` 类和消息推送功能
- 本 Story 将使用 `_monitor_instance` 全局变量提供控制命令

**功能关系:**
```
Story 4-1: ActivityMonitor (监控基础设施)
    ↓
Story 4-2: TelegramNotifier (消息推送)
    ↓
Story 4-3: 监控控制命令 (本 Story)
    - /monitor_status - 查看状态
    - /monitor_start - 启动监控
    - /monitor_stop - 停止监控
```

### 测试策略

**单元测试覆盖:**
```python
# tests/unit/test_story_4_3_monitor_commands.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from main import cmd_monitor_status, cmd_monitor_start, cmd_monitor_stop


@pytest.fixture
def mock_update():
    update = MagicMock()
    update.effective_user.id = 123456
    update.message.reply_text = AsyncMock()
    return update


@pytest.fixture
def mock_context():
    return MagicMock()


@pytest.mark.asyncio
async def test_cmd_monitor_status_running(mock_update, mock_context):
    """测试查看运行中状态"""
    with patch('main._monitor_instance') as mock_monitor:
        with patch('main.is_admin', return_value=True):
            mock_monitor.running = True
            mock_monitor.poll_interval = 30
            mock_monitor.seen_ids = {'id1', 'id2', 'id3'}

            await cmd_monitor_status(mock_update, mock_context)

            call_args = mock_update.message.reply_text.call_args[0][0]
            assert "运行中" in call_args
            assert "30 秒" in call_args
            assert "3 个" in call_args


@pytest.mark.asyncio
async def test_cmd_monitor_status_stopped(mock_update, mock_context):
    """测试查看已停止状态"""
    with patch('main._monitor_instance') as mock_monitor:
        with patch('main.is_admin', return_value=True):
            mock_monitor.running = False
            mock_monitor.poll_interval = 30
            mock_monitor.seen_ids = set()

            await cmd_monitor_status(mock_update, mock_context)

            call_args = mock_update.message.reply_text.call_args[0][0]
            assert "已停止" in call_args


@pytest.mark.asyncio
async def test_cmd_monitor_start_success(mock_update, mock_context):
    """测试启动监控成功"""
    with patch('main._monitor_instance') as mock_monitor:
        with patch('main.is_admin', return_value=True):
            mock_monitor.running = False
            mock_monitor.start_background = AsyncMock()
            mock_monitor.poll_interval = 30

            await cmd_monitor_start(mock_update, mock_context)

            mock_monitor.start_background.assert_called_once()
            assert "已启动" in mock_update.message.reply_text.call_args[0][0]


@pytest.mark.asyncio
async def test_cmd_monitor_start_already_running(mock_update, mock_context):
    """测试启动监控 - 已运行"""
    with patch('main._monitor_instance') as mock_monitor:
        with patch('main.is_admin', return_value=True):
            mock_monitor.running = True

            await cmd_monitor_start(mock_update, mock_context)

            call_args = mock_update.message.reply_text.call_args[0][0]
            assert "已在运行中" in call_args


@pytest.mark.asyncio
async def test_cmd_monitor_stop_success(mock_update, mock_context):
    """测试停止监控成功"""
    with patch('main._monitor_instance') as mock_monitor:
        with patch('main.is_admin', return_value=True):
            mock_monitor.running = True

            await cmd_monitor_stop(mock_update, mock_context)

            mock_monitor.stop.assert_called_once()
            assert "已停止" in mock_update.message.reply_text.call_args[0][0]


@pytest.mark.asyncio
async def test_cmd_monitor_stop_already_stopped(mock_update, mock_context):
    """测试停止监控 - 已停止"""
    with patch('main._monitor_instance') as mock_monitor:
        with patch('main.is_admin', return_value=True):
            mock_monitor.running = False

            await cmd_monitor_stop(mock_update, mock_context)

            call_args = mock_update.message.reply_text.call_args[0][0]
            assert "已处于停止状态" in call_args


@pytest.mark.asyncio
async def test_cmd_monitor_unauthorized(mock_update, mock_context):
    """测试非管理员权限拒绝"""
    with patch('main.is_admin', return_value=False):
        await cmd_monitor_status(mock_update, mock_context)
        assert "未授权" in mock_update.message.reply_text.call_args[0][0]

        mock_update.message.reply_text.reset_mock()
        await cmd_monitor_start(mock_update, mock_context)
        assert "未授权" in mock_update.message.reply_text.call_args[0][0]

        mock_update.message.reply_text.reset_mock()
        await cmd_monitor_stop(mock_update, mock_context)
        assert "未授权" in mock_update.message.reply_text.call_args[0][0]
```

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story4.3]
- [Source: monitor.py:17-136 - ActivityMonitor 类实现]
- [Source: main.py:51-53 - _monitor_instance 全局变量]
- [Source: main.py:295-306 - post_init 监控初始化]
- [Source: config.py:40-48 - is_admin 权限检查函数]
- [Source: _bmad-output/implementation-artifacts/4-1-activity-monitor-service.md]
- [Source: _bmad-output/implementation-artifacts/4-2-tg-message-push.md]

## Dev Agent Record

### Agent Model Used

GLM-5 (Code Review by Claude Code)

### Debug Log References

### Completion Notes List

Story created with comprehensive developer context including:
- Complete command handler implementations for /monitor_start, /monitor_stop, /monitor_status
- AUTO_START_MONITOR configuration for flexible deployment
- Unit test templates with full coverage
- Integration patterns with existing ActivityMonitor and TelegramNotifier

### File List

Created:
- `/Users/nick/projects/dx-terminal-monitor/_bmad-output/implementation-artifacts/4-3-monitor-control-commands.md`
- `/Users/nick/projects/dx-terminal-monitor/tests/unit/test_story_4_3_monitor_commands.py` - 27 unit tests

Modified:
- `main.py` - Added monitor control commands (cmd_monitor_status, cmd_monitor_start, cmd_monitor_stop)
- `config.py` - Added AUTO_START_MONITOR configuration
- `.env.example` - Added AUTO_START_MONITOR documentation
