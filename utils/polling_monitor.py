"""Polling health monitor - 检测并自动恢复 polling 静默死亡问题。"""

import asyncio
import logging
import os
import time

logger = logging.getLogger(__name__)


class PollingMonitor:
    """监控 polling 健康状态，若 polling 停止则重启进程。"""

    def __init__(self, check_interval: int = 300, max_silent_time: int = 1800):
        """
        Args:
            check_interval: 检查间隔（秒）
            max_silent_time: 最大静默时间（秒），超过则重启
        """
        self.check_interval = check_interval
        self.max_silent_time = max_silent_time
        self._last_poll_time = time.time()
        self._running = False
        self._task = None

    def record_poll_activity(self):
        """记录 polling 活动（每次 getUpdates 成功时调用）。"""
        self._last_poll_time = time.time()

    async def start(self):
        """启动监控。"""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._monitor_loop())
        logger.info(
            f"Polling monitor started (check_interval={self.check_interval}s, "
            f"max_silent_time={self.max_silent_time}s)"
        )

    async def _monitor_loop(self):
        """监控循环。"""
        while self._running:
            await asyncio.sleep(self.check_interval)
            silent_time = time.time() - self._last_poll_time
            if silent_time > self.max_silent_time:
                logger.error(
                    f"Polling silent death detected! "
                    f"No activity for {silent_time:.0f}s (max: {self.max_silent_time}s). "
                    f"Restarting bot..."
                )
                # 强制退出，让外层 while True 重试逻辑接管
                os._exit(1)
            else:
                logger.debug(f"Polling healthy (last activity {silent_time:.0f}s ago)")

    async def stop(self):
        """停止监控。"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        logger.info("Polling monitor stopped")


# 全局监控实例
_polling_monitor: PollingMonitor | None = None


def get_polling_monitor() -> PollingMonitor:
    """获取全局 polling 监控实例。"""
    global _polling_monitor
    if _polling_monitor is None:
        _polling_monitor = PollingMonitor()
    return _polling_monitor
