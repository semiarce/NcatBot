"""WUI-I-01 ~ WUI-I-04: WebUI server accepts WS connections and routes messages"""

import asyncio

import aiohttp
import pytest

from ncatbot.webui.server import create_app


@pytest.fixture
async def webui_server():
    """Start WebUI server on a random port, yield URL, then teardown."""
    app = create_app()
    runner = aiohttp.web.AppRunner(app)
    await runner.setup()
    site = aiohttp.web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    port = site._server.sockets[0].getsockname()[1]
    yield f"http://127.0.0.1:{port}"
    await runner.cleanup()


async def _ws_send_recv(url, msg):
    """Helper: open WS, send JSON, receive one JSON response."""
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(f"{url}/ws") as ws:
            await ws.send_json(msg)
            resp = await asyncio.wait_for(ws.receive_json(), timeout=5.0)
            return resp


async def test_session_create(webui_server):
    """WUI-I-01: session.create returns session_id"""
    resp = await _ws_send_recv(
        webui_server,
        {
            "type": "session.create",
            "id": "req-1",
            "payload": {"platform": "qq"},
        },
    )
    assert resp["type"] == "session.created"
    assert resp["id"] == "req-1"
    assert "session_id" in resp["payload"]


async def test_inject_and_settle(webui_server):
    """WUI-I-02: inject event + settle returns api_calls list"""
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(f"{webui_server}/ws") as ws:
            await ws.send_json(
                {
                    "type": "session.create",
                    "id": "req-1",
                    "payload": {"platform": "qq"},
                }
            )
            resp = await asyncio.wait_for(ws.receive_json(), timeout=5.0)
            sid = resp["payload"]["session_id"]

            await ws.send_json(
                {
                    "type": "event.inject",
                    "payload": {
                        "session_id": sid,
                        "event_type": "message.group",
                        "data": {"text": "/hello"},
                    },
                }
            )

            await ws.send_json(
                {
                    "type": "session.settle",
                    "id": "req-2",
                    "payload": {"session_id": sid},
                }
            )
            while True:
                resp = await asyncio.wait_for(ws.receive_json(), timeout=5.0)
                if resp["type"] == "settle.done":
                    break
            assert resp["id"] == "req-2"
            assert isinstance(resp["payload"]["api_calls"], list)


async def test_recording_export(webui_server):
    """WUI-I-03: recording start → inject → settle → export returns code"""
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(f"{webui_server}/ws") as ws:
            await ws.send_json(
                {
                    "type": "session.create",
                    "id": "r1",
                    "payload": {"platform": "qq"},
                }
            )
            resp = await asyncio.wait_for(ws.receive_json(), timeout=5.0)
            sid = resp["payload"]["session_id"]

            await ws.send_json(
                {
                    "type": "recording.start",
                    "payload": {"session_id": sid},
                }
            )

            await ws.send_json(
                {
                    "type": "event.inject",
                    "payload": {
                        "session_id": sid,
                        "event_type": "message.group",
                        "data": {"text": "/test"},
                    },
                }
            )

            await ws.send_json(
                {
                    "type": "session.settle",
                    "id": "r2",
                    "payload": {"session_id": sid},
                }
            )
            while True:
                resp = await asyncio.wait_for(ws.receive_json(), timeout=5.0)
                if resp["type"] == "settle.done":
                    break

            await ws.send_json(
                {
                    "type": "recording.stop",
                    "payload": {"session_id": sid},
                }
            )

            await ws.send_json(
                {
                    "type": "recording.export",
                    "id": "r3",
                    "payload": {"session_id": sid, "format": "scenario_dsl"},
                }
            )
            resp = await asyncio.wait_for(ws.receive_json(), timeout=5.0)
            assert resp["type"] == "recording.exported"
            assert "qq.group_message" in resp["payload"]["code"]


async def test_session_destroy(webui_server):
    """WUI-I-04: session.destroy cleans up resources"""
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(f"{webui_server}/ws") as ws:
            await ws.send_json(
                {
                    "type": "session.create",
                    "id": "d1",
                    "payload": {"platform": "qq"},
                }
            )
            resp = await asyncio.wait_for(ws.receive_json(), timeout=5.0)
            sid = resp["payload"]["session_id"]

            await ws.send_json(
                {
                    "type": "session.destroy",
                    "payload": {"session_id": sid},
                }
            )
            await ws.send_json(
                {
                    "type": "session.settle",
                    "id": "d2",
                    "payload": {"session_id": sid},
                }
            )
            resp = await asyncio.wait_for(ws.receive_json(), timeout=5.0)
            assert resp["type"] == "error"
