"""WUI-E2E-01: Full end-to-end WebUI flow: create → inject → settle → record → export"""

import asyncio

import aiohttp
import pytest

from ncatbot.webui.server import create_app


@pytest.fixture
async def webui_url():
    app = create_app()
    runner = aiohttp.web.AppRunner(app)
    await runner.setup()
    site = aiohttp.web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    port = site._server.sockets[0].getsockname()[1]
    yield f"http://127.0.0.1:{port}"
    await runner.cleanup()


async def test_full_e2e_flow(webui_url):
    """WUI-E2E-01: create session → start recording → inject → settle → stop → export"""
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(f"{webui_url}/ws") as ws:
            # 1) Create session
            await ws.send_json(
                {"type": "session.create", "id": "1", "payload": {"platform": "qq"}}
            )
            resp = await asyncio.wait_for(ws.receive_json(), timeout=5.0)
            assert resp["type"] == "session.created"
            sid = resp["payload"]["session_id"]

            # 2) Start recording
            await ws.send_json(
                {"type": "recording.start", "payload": {"session_id": sid}}
            )

            # 3) Inject a group message
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

            # 4) Settle
            await ws.send_json(
                {"type": "session.settle", "id": "2", "payload": {"session_id": sid}}
            )
            while True:
                resp = await asyncio.wait_for(ws.receive_json(), timeout=5.0)
                if resp["type"] == "settle.done":
                    break
            assert isinstance(resp["payload"]["api_calls"], list)

            # 5) Stop recording
            await ws.send_json(
                {"type": "recording.stop", "payload": {"session_id": sid}}
            )

            # 6) Export
            await ws.send_json(
                {
                    "type": "recording.export",
                    "id": "3",
                    "payload": {"session_id": sid, "format": "scenario_dsl"},
                }
            )
            resp = await asyncio.wait_for(ws.receive_json(), timeout=5.0)
            assert resp["type"] == "recording.exported"
            code = resp["payload"]["code"]
            assert "from ncatbot.testing import TestHarness, Scenario" in code
            assert "qq.group_message" in code
            assert "await scenario.run(h)" in code

            # 7) Destroy session
            await ws.send_json(
                {"type": "session.destroy", "payload": {"session_id": sid}}
            )
