"""BL-24: SessionSource 私信时间戳过滤测试

验证 SessionSource 的过期私信丢弃逻辑：
  BL-24a: 新鲜私信（age < max_msg_age）正常推送到回调
  BL-24b: 过期私信（age > max_msg_age）被丢弃，不触发回调
  BL-24c: timestamp 为 0 的私信被视为过期，丢弃
  BL-24d: 自定义 max_msg_age 生效
"""

from __future__ import annotations

import time
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ─── 辅助工具 ───────────────────────────────────────────────────────────────


def _make_event(
    *,
    sender_uid: int = 1001,
    receiver_id: int = 2002,
    receiver_type: int = 1,
    talker_id: int = 1001,
    msg_seqno: int = 1,
    msg_key: int = 100,
    timestamp: int = 0,
    content: str = "hello",
    msg_type: int = 1,
) -> SimpleNamespace:
    """构造模拟的 bilibili_api.session.Event"""
    return SimpleNamespace(
        sender_uid=sender_uid,
        receiver_id=receiver_id,
        receiver_type=receiver_type,
        talker_id=talker_id,
        msg_seqno=msg_seqno,
        msg_key=msg_key,
        timestamp=timestamp,
        content=content,
        msg_type=msg_type,
    )


class _FakeSession:
    """替代 bilibili_api.session.Session，捕获注册的事件处理器"""

    def __init__(self, **kwargs: Any):
        self.handlers: dict[str, Any] = {}
        self.logger = MagicMock()

    def on(self, event_type: Any):
        def decorator(func):
            self.handlers[str(event_type.value)] = func
            return func

        return decorator

    async def start(self):
        pass

    def close(self):
        pass


class _FakeEventType:
    """替代 bilibili_api.session.EventType 枚举"""

    def __init__(self, value: int):
        self.value = value

    def __iter__(self):
        return iter([])


# 构造一个最小枚举替身，仅含 TEXT(1)
_TEXT = _FakeEventType(1)
_PICTURE = _FakeEventType(2)

_FAKE_EVENT_TYPES = [_TEXT, _PICTURE]


# ─── Fixture ─────────────────────────────────────────────────────────────────


@pytest.fixture
def fake_session():
    """返回 _FakeSession 实例，patch 掉 bilibili_api 导入"""
    return _FakeSession()


@pytest.fixture
async def source_and_collector(fake_session):
    """创建 SessionSource 并启动，返回 (source, collector, fake_session)"""
    collector = AsyncMock()

    fake_module = MagicMock()
    fake_module.Session = lambda **kw: fake_session
    fake_module.EventType = _FAKE_EVENT_TYPES

    with patch.dict(
        "sys.modules",
        {"bilibili_api.session": fake_module, "bilibili_api": MagicMock()},
    ):
        from ncatbot.adapter.bilibili.source.session_source import SessionSource

        src = SessionSource(
            credential=MagicMock(),
            callback=collector,
            poll_interval=999.0,
        )
        await src.start()

    return src, collector, fake_session


# ─── BL-24a: 新鲜私信正常推送 ───────────────────────────────────────────────


async def test_bl24a_fresh_message_dispatched(source_and_collector):
    """BL-24a: 时间戳在 max_msg_age 内的私信正常传播"""
    _, collector, fake_session = source_and_collector

    now = int(time.time())
    event = _make_event(timestamp=now - 5, msg_seqno=10, content="新消息")

    handler = fake_session.handlers.get("1")
    assert handler is not None, "TEXT handler 未注册"
    await handler(event)

    collector.assert_awaited_once()
    call_args = collector.await_args
    assert call_args[0][0] == "session"
    raw = call_args[0][1]
    assert raw["content"] == "新消息"
    assert raw["msg_seqno"] == 10
    assert raw["sender_uid"] == 1001


# ─── BL-24b: 过期私信被丢弃 ─────────────────────────────────────────────────


async def test_bl24b_stale_message_dropped(source_and_collector):
    """BL-24b: 时间戳超过 max_msg_age 的私信不传播"""
    _, collector, fake_session = source_and_collector

    old_ts = int(time.time()) - 120  # 两分钟前
    event = _make_event(timestamp=old_ts, msg_seqno=99, content="旧消息")

    handler = fake_session.handlers.get("1")
    await handler(event)

    collector.assert_not_awaited()


# ─── BL-24c: timestamp=0 视为过期 ───────────────────────────────────────────


async def test_bl24c_zero_timestamp_dropped(source_and_collector):
    """BL-24c: timestamp 为 0 的私信被视为过期，丢弃"""
    _, collector, fake_session = source_and_collector

    event = _make_event(timestamp=0, msg_seqno=50)

    handler = fake_session.handlers.get("1")
    await handler(event)

    collector.assert_not_awaited()


# ─── BL-24d: 自定义 max_msg_age ─────────────────────────────────────────────


async def test_bl24d_custom_max_msg_age(fake_session):
    """BL-24d: 自定义 max_msg_age=5 时，6 秒前的消息被丢弃"""
    collector = AsyncMock()

    fake_module = MagicMock()
    fake_module.Session = lambda **kw: fake_session
    fake_module.EventType = _FAKE_EVENT_TYPES

    with patch.dict(
        "sys.modules",
        {"bilibili_api.session": fake_module, "bilibili_api": MagicMock()},
    ):
        from ncatbot.adapter.bilibili.source.session_source import SessionSource

        src = SessionSource(
            credential=MagicMock(),
            callback=collector,
            poll_interval=999.0,
            max_msg_age=5.0,
        )
        await src.start()

    handler = fake_session.handlers.get("1")

    # 6 秒前 → 超过 max_msg_age=5 → 丢弃
    event_old = _make_event(timestamp=int(time.time()) - 6, msg_seqno=1)
    await handler(event_old)
    collector.assert_not_awaited()

    # 2 秒前 → 在 max_msg_age=5 内 → 正常推送
    event_new = _make_event(timestamp=int(time.time()) - 2, msg_seqno=2)
    await handler(event_new)
    collector.assert_awaited_once()
