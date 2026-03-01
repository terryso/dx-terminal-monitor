# Story 4.1: 活动监控服务

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

作为**用户**,我需要**系统自动监控 Agent 的交易活动**,以便**实时了解 Agent 的操作情况**。

## Acceptance Criteria

1. 创建 `monitor.py` 模块
2. 实现 `ActivityMonitor` 类
3. 定期轮询 `api.get_activity()` 获取最新活动
4. 记录已处理的活动 ID,避免重复推送
5. 支持 .env 配置轮询间隔 (默认 30 秒)
6. 添加单元测试

## Tasks / Subtasks

- [ ] **Task 1: 创建 monitor.py 模块结构** (AC: #1)
  - [ ] 在项目根目录创建 `monitor.py` 文件
  - [ ] 导入必要模块 (asyncio, os, logging, typing)
  - [ ] 定义 `ActivityMonitor` 类基础结构
  - [ ] 添加文档字符串和类型注解

- [ ] **Task 2: 实现 ActivityMonitor.__init__()** (AC: #2, #5)
  - [ ] 接收 `TerminalAPI` 实例和回调函数参数
  - [ ] 初始化 `seen_ids: set[str]` 用于记录已处理活动
  - [ ] 从环境变量读取 `POLL_INTERVAL`,默认 30 秒
  - [ ] 添加 `running: bool` 状态标志

- [ ] **Task 3: 实现活动过滤逻辑** (AC: #4)
  - [ ] 实现 `_filter_new()` 方法
  - [ ] 比较活动 ID 与 `seen_ids` 集合
  - [ ] 返回新活动列表
  - [ ] 将新活动 ID 添加到 `seen_ids`

- [ ] **Task 4: 实现监控循环** (AC: #3)
  - [ ] 实现 `start()` 异步方法
  - [ ] 使用 `while running` 循环
  - [ ] 调用 `api.get_activity()` 获取活动
  - [ ] 过滤新活动并触发回调
  - [ ] 使用 `asyncio.sleep()` 等待轮询间隔
  - [ ] 实现 `stop()` 方法设置 `running = False`

- [ ] **Task 5: 添加环境变量配置** (AC: #5)
  - [ ] 在 `.env.example` 中添加 `POLL_INTERVAL` 说明
  - [ ] 默认值: 30 秒
  - [ ] 最小值: 10 秒 (避免 API 限流)
  - [ ] 更新 `config.py` 读取 `POLL_INTERVAL`

- [ ] **Task 6: 添加单元测试** (AC: #6)
  - [ ] 创建 `tests/unit/test_story_4_1_monitor.py`
  - [ ] 测试 `ActivityMonitor` 初始化
  - [ ] 测试活动过滤逻辑 (新活动/已处理活动)
  - [ ] 测试监控循环 (使用 AsyncMock)
  - [ ] 测试 stop 方法停止循环
  - [ ] 测试环境变量配置读取

## Dev Notes

### 技术栈要求

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | >=3.12 | 主要开发语言 |
| aiohttp | >=3.9.3 | HTTP 客户端 (复用 api.py) |
| pytest | >=8.0 | 测试框架 |
| pytest-asyncio | >=0.23 | 异步测试支持 |

### 现有 API 依赖

**api.py - get_activity() 方法 (已实现):**
```python
# api.py:30-35
async def get_activity(self, limit: int = 10) -> dict:
    """获取最近活动"""
    return await self._get(
        f"/activity/{self.vault}",
        {"limit": limit, "order": "desc"}
    )
```

**API 响应格式 (参考 Terminal Markets API):**
```json
{
  "activities": [
    {
      "id": "0xabc123...",
      "type": "swap",
      "timestamp": "2026-03-01T12:00:00Z",
      "data": {...}
    }
  ]
}
```

### 新增代码实现指南

**monitor.py - ActivityMonitor 类:**
```python
import asyncio
import logging
import os
from typing import Callable, Dict, Any, List

from api import TerminalAPI

logger = logging.getLogger(__name__)


class ActivityMonitor:
    """监控 Agent 活动并触发回调处理新活动。

    该类定期轮询 Terminal Markets API 获取最新活动,
    过滤已处理的活动,并对新活动执行回调函数。

    Args:
        api: TerminalAPI 实例用于获取活动数据
        callback: 异步回调函数,接收活动字典作为参数

    Example:
        async def on_new_activity(activity: dict):
            print(f"New activity: {activity['type']}")

        monitor = ActivityMonitor(api, on_new_activity)
        await monitor.start()
    """

    def __init__(
        self,
        api: TerminalAPI,
        callback: Callable[[Dict[str, Any]], Any]
    ):
        """初始化活动监控器。

        Args:
            api: TerminalAPI 实例
            callback: 新活动回调函数 (async function)
        """
        self.api = api
        self.callback = callback
        self.seen_ids: set[str] = set()
        self.poll_interval = self._get_poll_interval()
        self.running: bool = False
        self._task: asyncio.Task | None = None

    def _get_poll_interval(self) -> int:
        """从环境变量获取轮询间隔,默认 30 秒。

        Returns:
            轮询间隔秒数,最小 10 秒
        """
        interval = int(os.getenv('POLL_INTERVAL', '30'))
        return max(interval, 10)  # 最小 10 秒

    def _filter_new(self, activities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """过滤出新活动。

        Args:
            activities: 活动列表

        Returns:
            未处理过的新活动列表
        """
        new_items = []
        for activity in activities:
            activity_id = activity.get('id')
            if activity_id and activity_id not in self.seen_ids:
                new_items.append(activity)
                self.seen_ids.add(activity_id)
        return new_items

    async def start(self):
        """启动监控循环。

        该方法会阻塞运行,直到调用 stop()。
        建议在后台任务中运行: asyncio.create_task(monitor.start())
        """
        self.running = True
        logger.info(f"Activity monitor started (interval: {self.poll_interval}s)")

        while self.running:
            try:
                # 获取活动
                result = await self.api.get_activity(10)

                if "error" in result:
                    logger.error(f"Failed to fetch activity: {result['error']}")
                else:
                    activities = result.get("activities", [])

                    # 过滤新活动
                    new_items = self._filter_new(activities)

                    # 触发回调
                    for item in new_items:
                        try:
                            await self.callback(item)
                        except Exception as e:
                            logger.error(f"Callback error for activity {item.get('id')}: {e}")

            except Exception as e:
                logger.error(f"Monitor loop error: {e}")

            # 等待下一次轮询
            await asyncio.sleep(self.poll_interval)

        logger.info("Activity monitor stopped")

    def stop(self):
        """停止监控循环。

        设置 running 标志为 False,监控循环会在下一次迭代退出。
        """
        self.running = False
        logger.info("Activity monitor stop requested")

    async def start_background(self) -> asyncio.Task:
        """在后台任务中启动监控。

        Returns:
            运行监控循环的 asyncio.Task
        """
        self._task = asyncio.create_task(self.start())
        return self._task
```

**config.py - 添加 POLL_INTERVAL:**
```python
# 在现有环境变量读取部分添加
POLL_INTERVAL = int(os.getenv('POLL_INTERVAL', '30'))
```

**.env.example - 添加配置说明:**
```bash
# 活动监控配置
# 轮询间隔 (秒),最小 10 秒,默认 30 秒
POLL_INTERVAL=30
```

### Project Structure Notes

**新增/修改文件:**
```
dx-terminal-monitor/
├── monitor.py           # 新增 - ActivityMonitor 类
├── config.py            # 修改 - 添加 POLL_INTERVAL
├── .env.example         # 修改 - 添加 POLL_INTERVAL 说明
└── tests/
    └── unit/
        └── test_story_4_1_monitor.py  # 新增 - 监控器测试
```

### 与后续 Story 的依赖

**Story 4-2 (TG 消息推送):**
- 本 Story 提供监控基础设施
- Story 4-2 将实现 `format_activity_message()` 回调
- 回调将格式化活动并推送到 Telegram

**Story 4-3 (监控控制命令):**
- 本 Story 提供 `start()` 和 `stop()` 方法
- Story 4-3 将实现 `/monitor_start` 和 `/monitor_stop` 命令
- 需要集成 `ActivityMonitor` 到 Bot 主循环

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story4.1]
- [Source: _bmad-output/project-context.md#技术栈]
- [Source: api.py:30-35 - get_activity 方法]
- [Source: config.py - 环境变量读取模式]

## Dev Agent Record

### Agent Model Used

Claude (GLM-5)

### Debug Log References

None (story not yet implemented)

### Completion Notes List

Story created with comprehensive developer context including:
- Complete `ActivityMonitor` class implementation guide
- Unit test templates
- Environment variable configuration
- Integration patterns for Story 4-2 and 4-3

### File List

Created:
- `/Users/nick/projects/dx-terminal-monitor/_bmad-output/implementation-artifacts/4-1-activity-monitor-service.md`

To be created during implementation:
- `monitor.py` - ActivityMonitor class
- `tests/unit/test_story_4_1_monitor.py` - Unit tests

To be modified:
- `config.py` - Add POLL_INTERVAL
- `.env.example` - Add POLL_INTERVAL documentation
