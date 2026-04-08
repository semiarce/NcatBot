"""WUI-01 ~ WUI-04: HarnessProxy wraps TestHarness for WebUI sessions"""

import pytest
from ncatbot.webui.session import HarnessProxy


async def test_proxy_start_stop():
    """WUI-01: HarnessProxy can start and stop a TestHarness"""
    proxy = HarnessProxy(platform="qq")
    await proxy.start()
    assert proxy._harness is not None
    await proxy.stop()
    assert proxy._harness is None


async def test_proxy_inject_and_settle():
    """WUI-02: HarnessProxy can inject events and settle"""
    proxy = HarnessProxy(platform="qq")
    await proxy.start()
    try:
        await proxy.inject("message.group", {"text": "hello"})
        calls = await proxy.settle()
        assert isinstance(calls, list)
    finally:
        await proxy.stop()


async def test_proxy_unknown_event_type():
    """WUI-04: HarnessProxy raises KeyError for unknown event types"""
    proxy = HarnessProxy(platform="qq")
    await proxy.start()
    try:
        with pytest.raises(KeyError):
            await proxy.inject("unknown.event", {})
    finally:
        await proxy.stop()
