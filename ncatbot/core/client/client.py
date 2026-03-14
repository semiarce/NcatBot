"""BotClient — Bot 统一入口

负责引导 Adapter 启动、组装 BotAPIClient、接通事件流。
暂不涉及服务管理、注册器、插件加载等。
"""

from __future__ import annotations

import asyncio
from typing import Optional, TYPE_CHECKING

from ncatbot.adapter.base import BaseAdapter
from ncatbot.adapter.napcat.adapter import NapCatAdapter
from ncatbot.api.client import BotAPIClient
from ncatbot.core.dispatcher import AsyncEventDispatcher
from ncatbot.utils import get_log, setup_logging

if TYPE_CHECKING:
    pass

LOG = get_log("BotClient")


class BotClient:
    """Bot 生命周期管理器

    用法::

        bot = BotClient()

        @bot.on("message.group")
        async def on_group_msg(event):
            await event.reply("hello")

        bot.run()
    """

    def __init__(self, adapter: Optional[BaseAdapter] = None) -> None:
        setup_logging()
        self._adapter = adapter or NapCatAdapter()
        self._api: Optional[BotAPIClient] = None
        self._dispatcher: Optional[AsyncEventDispatcher] = None
        self._running = False
        self._listen_task: Optional[asyncio.Task] = None

        # 待注册的 handler（在 run 之前通过 @bot.on() 收集）
        self._pending_handlers: list[tuple[str, object, dict]] = []

    @property
    def api(self) -> BotAPIClient:
        if self._api is None:
            LOG.warning("API 不可用：BotClient 尚未启动")
            raise RuntimeError("API 不可用：BotClient 尚未启动")
        return self._api

    @property
    def dispatcher(self) -> AsyncEventDispatcher:
        if self._dispatcher is None:
            LOG.warning("Dispatcher 不可用：BotClient 尚未启动")
            raise RuntimeError("Dispatcher 不可用：BotClient 尚未启动")
        return self._dispatcher

    # ---- 启动 ----

    def run(self) -> None:
        """同步阻塞启动（setup → connect → listen → shutdown）"""
        try:
            asyncio.run(self._run_blocking())
        except KeyboardInterrupt:
            LOG.info("收到 Ctrl+C，正在退出…")

    async def run_async(self) -> None:
        """异步非阻塞启动。

        完成 startup 后在后台启动监听，立即返回::

            bot = BotClient()
            await bot.run_async()
            # 此处 bot.api / bot.dispatcher 已可用
            async with bot.dispatcher.events(EventType.MESSAGE) as stream:
                async for event in stream:
                    ...
        """
        await self._startup()
        self._listen_task = asyncio.create_task(self._listen_forever())
        LOG.info("Bot 已就绪，后台监听已启动")

    async def shutdown(self) -> None:
        """关闭 Dispatcher 和 Adapter，释放资源。"""
        if not self._running:
            return
        self._running = False
        LOG.info("正在关闭…")
        try:
            if self._listen_task and not self._listen_task.done():
                self._listen_task.cancel()
                try:
                    await self._listen_task
                except asyncio.CancelledError:
                    pass
            if self._dispatcher is not None:
                await self._dispatcher.close()
            await self._adapter.disconnect()
        except Exception as e:
            LOG.error("关闭异常: %s", e)
        LOG.info("已关闭")

    # ---- 内部 ----

    async def _run_blocking(self) -> None:
        """同步 run() 的内部实现：startup → 阻塞 listen → shutdown"""
        await self._startup()
        LOG.info("Bot 已就绪，开始监听事件")
        try:
            await self._adapter.listen()
        except asyncio.CancelledError:
            LOG.info("Bot 被取消")
        finally:
            await self.shutdown()

    async def _listen_forever(self) -> None:
        """后台监听 task，异常时自动 shutdown"""
        try:
            await self._adapter.listen()
        except asyncio.CancelledError:
            pass
        except Exception as e:
            LOG.error("监听异常: %s", e)
        finally:
            await self.shutdown()

    async def _startup(self) -> None:
        """引导启动：adapter setup → connect → 组装 API → 接通事件流"""
        # 1. 准备 + 连接
        LOG.info("正在启动 Adapter: %s", self._adapter.name)
        await self._adapter.setup()
        await self._adapter.connect()

        # 2. 从 adapter 取出底层 IBotAPI，包装为 BotAPIClient
        raw_api = self._adapter.get_api()
        self._api = BotAPIClient(raw_api)
        LOG.info("BotAPIClient 已就绪")

        # 3. 创建 dispatcher 并接通事件回调
        self._dispatcher = AsyncEventDispatcher()
        self._adapter.set_event_callback(self._dispatcher.callback)
