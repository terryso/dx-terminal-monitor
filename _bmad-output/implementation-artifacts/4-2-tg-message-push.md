# Story 4.2: TG 消息推送

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

作为**用户**,我需要**当 Agent 执行操作时收到 TG 通知**,以便**及时了解交易动态**。

## Acceptance Criteria

1. 实现 `format_activity_message()` 格式化活动消息
2. 支持格式化 Swap/Deposit/Withdrawal 三种类型
3. 推送到 `.env` 配置的 `ADMIN_USERS` 或 `ALLOWED_USERS`
4. 消息包含: 操作类型、时间、金额/数量、交易链接
5. 添加单元测试

## Tasks / Subtasks

- [x] **Task 1: 创建消息格式化模块** (AC: #1, #2, #4)
  - [x] 在项目根目录创建 `notifier.py` 文件
  - [x] 实现 `format_activity_message()` 函数
  - [x] 支持 Swap 类型格式化 (方向、代币、数量、价格)
  - [x] 支持 Deposit 类型格式化 (金额、时间)
  - [x] 支持 Withdrawal 类型格式化 (金额、时间)
  - [x] 添加时间戳格式化
  - [x] 添加 Etherscan 交易链接生成

- [x] **Task 2: 实现 Telegram 推送回调** (AC: #3)
  - [x] 在 `notifier.py` 中实现 `TelegramNotifier` 类
  - [x] 接收 Bot 实例
  - [x] 从配置读取 `ADMIN_USERS` 或 `ALLOWED_USERS`
  - [x] 实现 `send_notification()` 异步方法
  - [x] 支持推送到多个授权用户
  - [x] 添加错误处理和日志记录

- [x] **Task 3: 集成 ActivityMonitor 回调** (AC: #3)
  - [x] 在 `main.py` 中初始化 `TelegramNotifier`
  - [x] 创建 `on_new_activity()` 回调函数
  - [x] 格式化活动消息
  - [x] 调用 `send_notification()` 发送通知
  - [x] 传递回调给 `ActivityMonitor` 构造函数

- [x] **Task 4: 添加环境变量配置** (AC: #3)
  - [x] 在 `.env.example` 中添加 `NOTIFY_USERS` 说明
  - [x] 更新 `config.py` 读取 `NOTIFY_USERS`
  - [x] 支持逗号分隔的用户 ID 列表
  - [x] 默认使用 `ALLOWED_USERS` 作为回退

- [x] **Task 5: 添加单元测试** (AC: #5)
  - [x] 创建 `tests/unit/test_story_4_2_notifier.py`
  - [x] 测试 Swap 消息格式化
  - [x] 测试 Deposit 消息格式化
  - [x] 测试 Withdrawal 消息格式化
  - [x] 测试时间戳格式化
  - [x] 测试 Etherscan 链接生成
  - [x] 测试 `TelegramNotifier` 推送逻辑 (使用 AsyncMock)

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
        # ...

    async def start(self):
        # 监控循环，调用 callback(item) 处理新活动
```

**main.py - 已有格式化函数 (可复用):**
```python
# main.py:50-61
def format_eth(wei: str) -> str:
    try:
        return f"{float(wei) / 1e18:.6f}"
    except (ValueError, TypeError):
        return wei

def format_usd(value) -> str:
    try:
        return f"${float(value):.2f}"
    except (ValueError, TypeError):
        return str(value)
```

**config.py - 配置读取 (已实现):**
```python
# config.py:13-31
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
ALLOWED_USERS = [int(x) for x in os.getenv('ALLOWED_USERS', '').split(',') if x.strip().isdigit()]
ADMIN_USERS = [int(x) for x in os.getenv('ADMIN_USERS', '').split(',') if x.strip().isdigit()]
CHAIN_ID = int(os.getenv('CHAIN_ID', '1'))
```

### Terminal Markets API 响应格式

根据 `api.py` 的 `get_activity()` 方法，活动数据结构如下:

```json
{
  "activities": [
    {
      "id": "0xabc123...",
      "type": "swap",
      "timestamp": "2026-03-01T12:00:00Z",
      "swap": {
        "side": "BUY",
        "tokenSymbol": "USDC",
        "ethAmount": "500000000000000000",
        "tokenAmount": "1500000000",
        "effectivePriceUsd": "3000.00"
      }
    }
  ]
}
```

活动类型包括:
1. **swap** - 交易操作
   - `side`: BUY/SELL
   - `tokenSymbol`: 代币符号
   - `ethAmount`: ETH 数量 (Wei)
   - `tokenAmount`: 代币数量
   - `effectivePriceUsd`: 有效价格

2. **deposit** - 存款操作
   - `amountWei`: 金额 (Wei)

3. **withdrawal** - 提款操作
   - `amountWei`: 金额 (Wei)

### 新增代码实现指南

**notifier.py - 消息格式化和推送:**
```python
"""Telegram 通知模块 for Story 4-2"""

import logging
from datetime import datetime
from typing import Dict, Any, List
from telegram import Bot
from config import ADMIN_USERS, ALLOWED_USERS, CHAIN_ID

logger = logging.getLogger(__name__)

# Etherscan 基础 URL (根据链 ID)
ETHERSCAN_BASE_URLS = {
    1: "https://etherscan.io/tx",
    11155111: "https://sepolia.etherscan.io/tx",
}


def format_eth(wei: str) -> str:
    """将 Wei 格式化为 ETH"""
    try:
        return f"{float(wei) / 1e18:.6f}"
    except (ValueError, TypeError):
        return wei


def format_usd(value) -> str:
    """将数值格式化为 USD"""
    try:
        return f"${float(value):,.2f}"
    except (ValueError, TypeError):
        return str(value)


def format_timestamp(ts: str) -> str:
    """格式化时间戳"""
    try:
        dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        return ts


def get_tx_url(tx_hash: str) -> str:
    """生成交易浏览器链接"""
    base_url = ETHERSCAN_BASE_URLS.get(CHAIN_ID, ETHERSCAN_BASE_URLS[1])
    return f"{base_url}/{tx_hash}"


def format_activity_message(activity: Dict[str, Any]) -> str:
    """格式化活动为 Telegram 消息。

    Args:
        activity: 活动字典，包含 type, timestamp, id 等字段

    Returns:
        格式化的 Telegram 消息字符串
    """
    activity_type = activity.get('type', 'unknown')
    timestamp = format_timestamp(activity.get('timestamp', ''))
    activity_id = activity.get('id', '')

    lines = [
        "🔔 Agent 操作通知\n",
        f"类型: {activity_type.upper()}",
        f"时间: {timestamp}",
    ]

    if activity_type == 'swap':
        swap = activity.get('swap', {})
        side = swap.get('side', '?').upper()
        token = swap.get('tokenSymbol', '?')
        eth_amt = format_eth(swap.get('ethAmount', '0'))
        price = format_usd(swap.get('effectivePriceUsd', '0'))

        lines.extend([
            f"方向: {side}",
            f"代币: {token}",
            f"数量: {eth_amt} ETH",
            f"价格: {price}",
        ])

    elif activity_type == 'deposit':
        deposit = activity.get('deposit', {})
        amt = format_eth(deposit.get('amountWei', '0'))
        lines.append(f"金额: {amt} ETH")

    elif activity_type == 'withdrawal':
        withdrawal = activity.get('withdrawal', {})
        amt = format_eth(withdrawal.get('amountWei', '0'))
        lines.append(f"金额: {amt} ETH")

    # 添加交易链接
    if activity_id:
        lines.append(f"查看: {get_tx_url(activity_id)}")

    return '\n'.join(lines)


class TelegramNotifier:
    """Telegram 通知推送器。

    将活动消息推送到授权用户的 Telegram。
    """

    def __init__(self, bot: Bot, notify_users: List[int] = None):
        """初始化通知器。

        Args:
            bot: Telegram Bot 实例
            notify_users: 接收通知的用户 ID 列表，默认使用 ADMIN_USERS
        """
        self.bot = bot
        self.notify_users = notify_users or []

        # 如果没有指定用户，使用配置中的用户
        if not self.notify_users:
            self.notify_users = ADMIN_USERS if ADMIN_USERS else ALLOWED_USERS

        logger.info(f"TelegramNotifier initialized for users: {self.notify_users}")

    async def send_notification(self, activity: Dict[str, Any]) -> None:
        """发送活动通知到所有授权用户。

        Args:
            activity: 活动字典
        """
        if not self.notify_users:
            logger.warning("No notify users configured, skipping notification")
            return

        # 格式化消息
        message = format_activity_message(activity)

        # 发送到每个用户
        for user_id in self.notify_users:
            try:
                await self.bot.send_message(chat_id=user_id, text=message)
                logger.info(f"Notification sent to user {user_id} for activity {activity.get('id')}")
            except Exception as e:
                logger.error(f"Failed to send notification to user {user_id}: {e}")
```

**config.py - 添加 NOTIFY_USERS:**
```python
# 在现有环境变量读取部分添加 (约第32行)
NOTIFY_USERS = [
    int(x) for x in os.getenv('NOTIFY_USERS', '').split(',')
    if x.strip().isdigit()
]
# 如果未配置 NOTIFY_USERS，将使用 ADMIN_USERS 或 ALLOWED_USERS
```

**.env.example - 添加配置说明:**
```bash
# 活动监控通知配置
# 接收通知的用户 ID 列表 (逗号分隔)
# 如果未配置，将使用 ADMIN_USERS 或 ALLOWED_USERS
NOTIFY_USERS=
```

**main.py - 集成通知功能:**
```python
# 在文件顶部添加导入
from notifier import TelegramNotifier

# 全局变量存储监控器和通知器
_monitor_instance = None
_notifier_instance = None


async def on_new_activity(activity: dict):
    """ActivityMonitor 回调函数 - 发送 TG 通知"""
    if _notifier_instance:
        await _notifier_instance.send_notification(activity)


async def post_init_with_monitor(app: Application):
    """初始化 Bot 并启动监控"""
    # 调用原有的 post_init 设置命令菜单
    await post_init(app)

    # 创建通知器
    global _notifier_instance
    _notifier_instance = TelegramNotifier(app.bot)

    # 创建监控器并传入回调
    global _monitor_instance
    _monitor_instance = ActivityMonitor(api, on_new_activity)

    # 在后台启动监控
    await _monitor_instance.start_background()
    logger.info("Activity monitor started with Telegram notifications")
```

### Project Structure Notes

**新增/修改文件:**
```
dx-terminal-monitor/
├── notifier.py          # 新增 - 消息格式化和 TelegramNotifier 类
├── config.py            # 修改 - 添加 NOTIFY_USERS
├── main.py              # 修改 - 集成监控和通知
├── .env.example         # 修改 - 添加 NOTIFY_USERS 说明
└── tests/
    └── unit/
        └── test_story_4_2_notifier.py  # 新增 - 通知器测试
```

### 与其他 Story 的关系

**前置依赖:**
- **Story 4-1** - 提供了 `ActivityMonitor` 类和监控基础设施
- 本 Story 将实现 `format_activity_message()` 作为回调传递给 `ActivityMonitor`

**后续 Story:**
- **Story 4-3 (监控控制命令)** - 将使用 `_monitor_instance` 提供启动/停止命令
  - `/monitor_start` - 启动监控 (如果未启动)
  - `/monitor_stop` - 停止监控
  - `/monitor_status` - 查看监控状态

### 测试策略

**单元测试覆盖:**
```python
# tests/unit/test_story_4_2_notifier.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from notifier import format_activity_message, TelegramNotifier


def test_format_swap_message():
    """测试 Swap 消息格式化"""
    activity = {
        "id": "0xabc123",
        "type": "swap",
        "timestamp": "2026-03-01T12:00:00Z",
        "swap": {
            "side": "BUY",
            "tokenSymbol": "USDC",
            "ethAmount": "500000000000000000",  # 0.5 ETH
            "effectivePriceUsd": "3000.00"
        }
    }
    message = format_activity_message(activity)
    assert "SWAP" in message
    assert "BUY" in message
    assert "USDC" in message
    assert "0.500000 ETH" in message
    assert "$3,000.00" in message
    assert "etherscan.io" in message


def test_format_deposit_message():
    """测试 Deposit 消息格式化"""
    activity = {
        "id": "0xdef456",
        "type": "deposit",
        "timestamp": "2026-03-01T12:00:00Z",
        "deposit": {
            "amountWei": "1000000000000000000"  # 1 ETH
        }
    }
    message = format_activity_message(activity)
    assert "DEPOSIT" in message
    assert "1.000000 ETH" in message


def test_format_withdrawal_message():
    """测试 Withdrawal 消息格式化"""
    activity = {
        "id": "0x789xyz",
        "type": "withdrawal",
        "timestamp": "2026-03-01T12:00:00Z",
        "withdrawal": {
            "amountWei": "500000000000000000"  # 0.5 ETH
        }
    }
    message = format_activity_message(activity)
    assert "WITHDRAWAL" in message
    assert "0.500000 ETH" in message


@pytest.mark.asyncio
async def test_telegram_notifier_send():
    """测试 TelegramNotifier 发送逻辑"""
    mock_bot = MagicMock()
    mock_bot.send_message = AsyncMock()

    notifier = TelegramNotifier(mock_bot, notify_users=[123456])
    activity = {
        "id": "0xabc123",
        "type": "swap",
        "timestamp": "2026-03-01T12:00:00Z",
        "swap": {"side": "BUY"}
    }

    await notifier.send_notification(activity)

    assert mock_bot.send_message.called
    call_args = mock_bot.send_message.call_args
    assert call_args.kwargs['chat_id'] == 123456
    assert 'SWAP' in call_args.kwargs['text']
```

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story4.2]
- [Source: monitor.py - ActivityMonitor 类实现]
- [Source: api.py:30-35 - get_activity 方法]
- [Source: main.py:50-61 - format_eth, format_usd 函数]
- [Source: config.py - 环境变量读取模式]
- [Source: _bmad-output/implementation-artifacts/4-1-activity-monitor-service.md]

## Dev Agent Record

### Agent Model Used

Claude (GLM-5)

### Debug Log References

- Initial test run: 28 tests skipped (TDD RED PHASE)
- Fixed 2 tests with proper mocking patterns (test_send_notification_no_users_configured, test_get_tx_url_sepolia)
- Final test run: 28 tests passed, 270 total tests passed (no regressions)

### Completion Notes List

**Implementation completed (2026-03-01):**
- Created `notifier.py` with complete `format_activity_message()` and `TelegramNotifier` implementation
- Implemented helper functions: `format_eth()`, `format_usd()`, `format_timestamp()`, `get_tx_url()`
- Integrated with `ActivityMonitor` callback in `main.py`
- Added `NOTIFY_USERS` configuration with fallback chain: NOTIFY_USERS > ADMIN_USERS > ALLOWED_USERS
- Created 28 unit tests with full coverage of all activity types
- Added Etherscan URL generation for mainnet, sepolia, and holesky

### File List

Created:
- `notifier.py` - Message formatting and TelegramNotifier class
- `tests/unit/test_story_4_2_notifier.py` - 29 unit tests (added Holesky test during review)
- `_bmad-output/test-artifacts/atdd-checklist-4-2.md` - ATDD checklist

Modified:
- `config.py` - Added NOTIFY_USERS configuration
- `.env.example` - Added NOTIFY_USERS documentation
- `main.py` - Integrated TelegramNotifier with ActivityMonitor callback
- `_bmad-output/implementation-artifacts/sprint-status.yaml` - Updated status to done

## Senior Developer Review (AI)

**Review Date:** 2026-03-01
**Review Outcome:** Approve

### Action Items

- [x] [MEDIUM] Update test file header - remove "TDD RED PHASE" comment since feature is implemented
- [x] [MEDIUM] Remove skipif pytestmark since tests now pass
- [x] [LOW] Add type hint to format_usd parameter
- [x] [LOW] Add test for Holesky chain ID (test_get_tx_url_holesky)

### Issues Deferred (Non-blocking)

1. **DRY violation**: Both main.py and notifier.py have format_eth/format_usd functions. Consider refactoring to shared module in future.
2. **Task description mismatch**: Story subtask says "默认使用 ALLOWED_USERS 作为回退" but actual implementation uses NOTIFY_USERS > ADMIN_USERS > ALLOWED_USERS priority chain (actually better than documented).

### Review Summary

All 5 Acceptance Criteria fully implemented and validated:
- ✅ AC1: format_activity_message() implemented in notifier.py:86-135
- ✅ AC2: Supports swap/deposit/withdrawal formatting
- ✅ AC3: NOTIFY_USERS > ADMIN_USERS > ALLOWED_USERS fallback chain
- ✅ AC4: Message contains type, time, amount, and tx link
- ✅ AC5: 29 unit tests (all passing)

Code quality: Good. Clean implementation with proper error handling and logging.
