import pytest
import asyncio
import aiohttp
from backend.config.settings import get_config_manager

# Load server settings from the configuration
config_manager = get_config_manager("../../config/config.json")
server_settings = config_manager.server
BASE_URL = f"http://{server_settings.host}:{server_settings.port}"


@pytest.mark.asyncio
async def test_concurrent_sessions():
    async with aiohttp.ClientSession() as session:
        # Create two sessions
        response1 = await session.post(f"{BASE_URL}/api/session")
        assert response1.status == 200
        data1 = await response1.json()
        session_id1 = data1["session_id"]

        response2 = await session.post(f"{BASE_URL}/api/session")
        assert response2.status == 200
        data2 = await response2.json()
        session_id2 = data2["session_id"]

        async def session_task(session_id: str, message: str):
            ws_url = f"ws://{server_settings.host}:{server_settings.port}/ws/{session_id}"
            async with session.ws_connect(ws_url) as ws:
                await ws.send_str(message)
                response = await ws.receive()
                assert response.type == aiohttp.WSMsgType.TEXT
                assert response.data is not None
                # The exact response content depends on the agent's logic,
                # so we'll just check that we get a non-empty response.
                assert len(response.data) > 0

        # Run two session tasks concurrently
        await asyncio.gather(
            session_task(session_id1, "Hello from session 1"),
            session_task(session_id2, "Hello from session 2")
        )
