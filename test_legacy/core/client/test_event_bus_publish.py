"""
EventBus 发布、事件流和 waiter 测试
"""

import asyncio

import pytest

from ncatbot.core import NcatBotEvent
from ncatbot.core.event import EventParser, GroupMessageEvent


class TestEventBusPublish:
    """测试自定义事件发布"""

    @pytest.mark.asyncio
    async def test_publish_exact_match(self, event_bus):
        results = []

        async def handler(event):
            results.append(event.type)
            return "handled"

        event_bus.subscribe("test.event", handler)
        event = NcatBotEvent("test.event", {"data": "test"})

        publish_results = await event_bus.publish(event)

        assert results == ["test.event"]
        assert publish_results == ["handled"]
        assert event.results == ["handled"]
        await event_bus.close()

    @pytest.mark.asyncio
    async def test_publish_no_match(self, event_bus):
        event = NcatBotEvent("unmatched.event", {})
        results = await event_bus.publish(event)
        assert results == []
        await event_bus.close()

    @pytest.mark.asyncio
    async def test_publish_multiple_handlers(self, event_bus):
        call_order = []

        async def handler1(event):
            call_order.append(1)
            return 1

        async def handler2(event):
            call_order.append(2)
            return 2

        event_bus.subscribe("test.event", handler1)
        event_bus.subscribe("test.event", handler2)

        event = NcatBotEvent("test.event", {})
        results = await event_bus.publish(event)

        assert len(call_order) == 2
        assert set(results) == {1, 2}
<<<<<<< HEAD:test_legacy/core/client/test_event_bus_publish.py
=======
        await event_bus.close()
>>>>>>> 278158becc79ca73dbaac6cf936d50c353304b18:test/core/client/test_event_bus_publish.py


class TestEventBusPriority:
    """测试处理器优先级"""

    @pytest.mark.asyncio
    async def test_handler_priority_order(self, event_bus):
<<<<<<< HEAD:test_legacy/core/client/test_event_bus_publish.py
        """高优先级处理器先执行"""
=======
>>>>>>> 278158becc79ca73dbaac6cf936d50c353304b18:test/core/client/test_event_bus_publish.py
        call_order = []

        async def low_priority(event):
            call_order.append("low")

        async def high_priority(event):
            call_order.append("high")

        async def medium_priority(event):
            call_order.append("medium")

        event_bus.subscribe("test.event", low_priority, priority=1)
        event_bus.subscribe("test.event", high_priority, priority=100)
        event_bus.subscribe("test.event", medium_priority, priority=50)

        event = NcatBotEvent("test.event", {})
        await event_bus.publish(event)

        assert call_order == ["high", "medium", "low"]
<<<<<<< HEAD:test_legacy/core/client/test_event_bus_publish.py

    @pytest.mark.asyncio
    async def test_stop_propagation_in_handler(self, event_bus):
        """处理器中调用 stop_propagation()"""
=======
        await event_bus.close()

    @pytest.mark.asyncio
    async def test_stop_propagation_in_handler(self, event_bus):
>>>>>>> 278158becc79ca73dbaac6cf936d50c353304b18:test/core/client/test_event_bus_publish.py
        call_order = []

        async def first_handler(event):
            call_order.append("first")
            event.stop_propagation()

        async def second_handler(event):
            call_order.append("second")

        event_bus.subscribe("test.event", first_handler, priority=100)
        event_bus.subscribe("test.event", second_handler, priority=1)

        event = NcatBotEvent("test.event", {})
        await event_bus.publish(event)

        assert call_order == ["first"]
<<<<<<< HEAD:test_legacy/core/client/test_event_bus_publish.py


class TestEventBusTimeout:
    """测试处理器超时"""

    @pytest.mark.asyncio
    async def test_handler_timeout(self, event_bus_short_timeout):
        """处理器超时触发 HandlerTimeoutError"""

        async def slow_handler(event):
            await asyncio.sleep(0.12)
            return "done"

        event_bus_short_timeout.subscribe("test.event", slow_handler)

        event = NcatBotEvent("test.event", {})
        await event_bus_short_timeout.publish(event)

        assert len(event.exceptions) == 1
        assert isinstance(event.exceptions[0], HandlerTimeoutError)

    @pytest.mark.asyncio
    async def test_handler_custom_timeout(self, event_bus):
        """自定义超时时间"""

        async def slow_handler(event):
            await asyncio.sleep(0.02)
            return "done"

        event_bus.subscribe("test.event", slow_handler, timeout=0.01)

        event = NcatBotEvent("test.event", {})
        await event_bus.publish(event)

        assert len(event.exceptions) == 1
        assert isinstance(event.exceptions[0], HandlerTimeoutError)

    def test_handler_timeout_error_str(self):
        """测试 HandlerTimeoutError 字符串表示"""
        error = HandlerTimeoutError(
            meta_data={"name": "TestPlugin"}, handler="test_handler", time=5.0
        )

        error_str = str(error)

        assert "TestPlugin" in error_str
        assert "test_handler" in error_str
        assert "5" in error_str
=======
        await event_bus.close()
>>>>>>> 278158becc79ca73dbaac6cf936d50c353304b18:test/core/client/test_event_bus_publish.py


class TestEventBusExceptionHandling:
    """测试异常处理"""

    @pytest.mark.asyncio
    async def test_handler_exception_captured(self, event_bus):
<<<<<<< HEAD:test_legacy/core/client/test_event_bus_publish.py
        """处理器异常被捕获到 event.exceptions"""

=======
>>>>>>> 278158becc79ca73dbaac6cf936d50c353304b18:test/core/client/test_event_bus_publish.py
        async def failing_handler(event):
            raise ValueError("Handler error")

        async def normal_handler(event):
            return "ok"

        event_bus.subscribe("test.event", failing_handler, priority=100)
        event_bus.subscribe("test.event", normal_handler, priority=1)

        event = NcatBotEvent("test.event", {})
        results = await event_bus.publish(event)

        assert len(event.exceptions) == 1
        assert isinstance(event.exceptions[0], ValueError)
        assert "ok" in results
<<<<<<< HEAD:test_legacy/core/client/test_event_bus_publish.py


class TestEventBusHandlerTypes:
    """测试不同类型的处理器"""

    @pytest.mark.asyncio
    async def test_async_handler_execution(self, event_bus):
        """异步处理器正确执行"""
        result = []

        async def async_handler(event):
            await asyncio.sleep(0.01)
            result.append("async")
            return "async_result"

        event_bus.subscribe("test.event", async_handler)

        event = NcatBotEvent("test.event", {})
        results = await event_bus.publish(event)

        assert result == ["async"]
        assert "async_result" in results

    @pytest.mark.asyncio
    async def test_sync_handler_execution(self, event_bus):
        """同步处理器正确执行"""
        result = []

        def sync_handler(event):
            result.append("sync")
            return "sync_result"

        event_bus.subscribe("test.event", sync_handler)

        event = NcatBotEvent("test.event", {})
        results = await event_bus.publish(event)

        assert result == ["sync"]
        assert "sync_result" in results
=======
        await event_bus.close()


class TestEventBusAdapterStream:
    """测试 adapter 事件入口、流式消费和 wait_event"""

    @pytest.mark.asyncio
    async def test_on_adapter_event_dispatches_normalized_event(
        self, event_bus, mock_api, sample_message_event_data
    ):
        handled = asyncio.Event()
        seen_types = []

        async def handler(event):
            seen_types.append(event.type)
            handled.set()

        event_bus.subscribe("ncatbot.message_event", handler)
        message_event = EventParser.parse(sample_message_event_data, mock_api)

        await event_bus.on_adapter_event(message_event)
        await asyncio.wait_for(handled.wait(), timeout=1.0)

        assert seen_types == ["ncatbot.message_event"]
        await event_bus.close()

    @pytest.mark.asyncio
    async def test_wait_event_returns_matching_adapter_event(
        self, event_bus, mock_api, sample_message_event_data
    ):
        waiter = asyncio.create_task(
            event_bus.wait_event(lambda event: event.post_type == "message", timeout=1.0)
        )

        message_event = EventParser.parse(sample_message_event_data, mock_api)
        await event_bus.on_adapter_event(message_event)

        received = await waiter

        assert isinstance(received, GroupMessageEvent)
        assert received.raw_message == "Hello, world!"
        await event_bus.close()

    @pytest.mark.asyncio
    async def test_async_iterator_yields_adapter_events(
        self, event_bus, mock_api, sample_message_event_data
    ):
        async def consume_one():
            async for event in event_bus:
                return event
            return None

        consumer = asyncio.create_task(consume_one())

        message_event = EventParser.parse(sample_message_event_data, mock_api)
        await event_bus.on_adapter_event(message_event)

        received = await asyncio.wait_for(consumer, timeout=1.0)

        assert isinstance(received, GroupMessageEvent)
        assert received.group_id == "123456789"
        await event_bus.close()

    @pytest.mark.asyncio
    async def test_custom_publish_does_not_match_adapter_waiter(self, event_bus):
        waiter = asyncio.create_task(
            event_bus.wait_event(lambda event: event.post_type == "message", timeout=0.05)
        )

        with pytest.raises(asyncio.TimeoutError):
            await event_bus.publish(NcatBotEvent("test.event", {}))
            await waiter

        await event_bus.close()
>>>>>>> 278158becc79ca73dbaac6cf936d50c353304b18:test/core/client/test_event_bus_publish.py
