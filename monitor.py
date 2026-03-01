"""
Activity Monitor Service for Story 4-1

Monitors Agent trading activity and triggers callbacks for new activities.
"""

import asyncio
import logging
import os
from typing import Callable, Dict, Any, List

from api import TerminalAPI

logger = logging.getLogger(__name__)


class ActivityMonitor:
    """监控 Agent 活动并触发回调处理新活动。

    该类定期轮询 Terminal Markets API 获取最新活动，
    过滤已处理的活动，并对新活动执行回调函数。

    Args:
        api: TerminalAPI 实例用于获取活动数据
        callback: 异步回调函数，接收活动字典作为参数

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
        """从环境变量获取轮询间隔，默认 30 秒。

        Returns:
            轮询间隔秒数，最小 10 秒
        """
        try:
            interval = int(os.getenv('POLL_INTERVAL', '30'))
        except ValueError:
            logger.warning("Invalid POLL_INTERVAL value, using default 30s")
            interval = 30
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
            # API 返回 cursor 作为唯一标识
            activity_id = activity.get('cursor') or activity.get('id')
            if activity_id and activity_id not in self.seen_ids:
                new_items.append(activity)
                self.seen_ids.add(activity_id)
        return new_items

    async def _preload_existing_activities(self):
        """预加载已存在的活动 ID，避免启动时发送历史通知。

        首次启动时获取现有活动并记录其 ID，但不触发回调。
        """
        try:
            result = await self.api.get_activity(50)
            if "error" not in result:
                activities = result.get("items", result.get("activities", []))
                for activity in activities:
                    activity_id = activity.get('cursor') or activity.get('id')
                    if activity_id:
                        self.seen_ids.add(activity_id)
                logger.info(f"Preloaded {len(self.seen_ids)} existing activity IDs")
        except Exception as e:
            logger.warning(f"Failed to preload activities: {e}")

    async def start(self):
        """启动监控循环。

        该方法会阻塞运行，直到调用 stop()。
        建议在后台任务中运行: asyncio.create_task(monitor.start())
        """
        self.running = True
        logger.info(f"Activity monitor started (interval: {self.poll_interval}s)")

        # 预加载已存在的活动，避免启动时发送历史通知
        await self._preload_existing_activities()

        while self.running:
            try:
                # 获取活动
                result = await self.api.get_activity(10)

                if "error" in result:
                    logger.error(f"Failed to fetch activity: {result['error']}")
                else:
                    # API 返回 items 而不是 activities
                    activities = result.get("items", result.get("activities", []))
                    if activities:
                        logger.debug(f"Fetched {len(activities)} activities, latest: {activities[0].get('cursor', 'unknown')}")

                    # 过滤新活动
                    new_items = self._filter_new(activities)

                    if new_items:
                        logger.info(f"Found {len(new_items)} new activities to notify")

                    # 触发回调
                    for item in new_items:
                        try:
                            await self.callback(item)
                        except Exception as e:
                            logger.error(f"Callback error for activity {item.get('cursor')}: {e}")

            except Exception as e:
                logger.error(f"Monitor loop error: {e}")

            # 等待下一次轮询
            await asyncio.sleep(self.poll_interval)

        logger.info("Activity monitor stopped")

    def stop(self):
        """停止监控循环。

        设置 running 标志为 False，监控循环会在下一次迭代退出。
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
