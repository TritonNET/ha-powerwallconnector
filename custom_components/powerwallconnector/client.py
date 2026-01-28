"""WebSocket Client for TritonNET Powerwall Connector."""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Callable
from datetime import datetime

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.util import dt as dt_util

_LOGGER = logging.getLogger(__name__)

# CONFIGURATION
WATCHDOG_TIMEOUT = 60         # Reconnect if no data for 60s
WS_HEARTBEAT_INTERVAL = 20    # Protocol Ping every 20s

# Connection States
STATE_NOT_CONNECTED = "not_connected"
STATE_CONNECTING = "connecting"
STATE_CONNECTED = "connected"
STATE_DISCONNECTED = "disconnected"
STATE_RETRYING = "retrying"

class TritonNetClient:
    """Manages the WebSocket connection and data state."""

    def __init__(self, hass: HomeAssistant, host: str, port: int) -> None:
        """Initialize the client."""
        self.hass = hass
        self.url = f"ws://{host}:{port}/stream"
        
        self._data: dict[str, Any] = {}
        self.last_update_time: datetime | None = None
        self.status = STATE_NOT_CONNECTED
        
        self._listeners: list[Callable[[], None]] = []
        self._task: asyncio.Task | None = None
        self._watchdog_task: asyncio.Task | None = None
        self._stopping = False
        self.connected = False
        self._last_msg_received = 0.0

    @property
    def data(self) -> dict[str, Any]:
        """Return the current data. Required by sensors."""
        return self._data

    def async_add_listener(self, callback: Callable[[], None]) -> Callable[[], None]:
        """Register a listener for data updates."""
        self._listeners.append(callback)
        return lambda: self._listeners.remove(callback)

    def start(self) -> None:
        """Start the connection loop and watchdog."""
        self._stopping = False
        self._task = self.hass.async_create_background_task(
            self._connect_loop(), "tritonnet_ws_client"
        )
        self._watchdog_task = self.hass.async_create_background_task(
            self._watchdog_loop(), "tritonnet_watchdog"
        )

    async def stop(self) -> None:
        """Stop all tasks."""
        self._stopping = True
        for task in [self._task, self._watchdog_task]:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

    async def _watchdog_loop(self) -> None:
        """Monitor connection 'pulse' and force reset if silent."""
        while not self._stopping:
            await asyncio.sleep(10)
            
            if self.connected and self._last_msg_received > 0:
                time_since_last = dt_util.utcnow().timestamp() - self._last_msg_received
                if time_since_last > WATCHDOG_TIMEOUT:
                    _LOGGER.warning(
                        "Watchdog: No data received for %ss. Reconnecting...", 
                        WATCHDOG_TIMEOUT
                    )
                    if self._task:
                        self._task.cancel() 

    async def _connect_loop(self) -> None:
        """Main loop maintaining the WebSocket connection."""
        session = async_get_clientsession(self.hass)
        backoff = 2

        while not self._stopping:
            self._set_status(STATE_CONNECTING)
            
            try:
                _LOGGER.debug("Connecting to %s...", self.url)
                async with session.ws_connect(
                    self.url, 
                    heartbeat=WS_HEARTBEAT_INTERVAL,
                    timeout=10
                ) as ws:
                    _LOGGER.info("Connected to TritonNET C# Service")
                    self.connected = True
                    self._set_status(STATE_CONNECTED)
                    backoff = 2
                    
                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            self._last_msg_received = dt_util.utcnow().timestamp()
                            try:
                                payload = json.loads(msg.data)
                                self._handle_message(payload)
                            except ValueError:
                                _LOGGER.error("Received invalid JSON from TritonNET")
                        elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.CLOSING):
                            break
                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            break
                            
            except asyncio.CancelledError:
                _LOGGER.debug("Connect loop reset by watchdog or shutdown")
            except (aiohttp.ClientError, asyncio.TimeoutError) as err:
                _LOGGER.warning("Connection failed: %s", err)
            except Exception as ex:
                _LOGGER.exception("Unexpected error in TritonNET client: %s", ex)
            
            self.connected = False
            self._set_status(STATE_DISCONNECTED)

            if not self._stopping:
                await asyncio.sleep(0.5) 
                self._set_status(STATE_RETRYING)
                _LOGGER.info("Retrying in %ss...", backoff)
                try:
                    await asyncio.sleep(backoff)
                except asyncio.CancelledError:
                    break
                backoff = min(backoff * 2, 30)

    def _set_status(self, status: str) -> None:
        """Update status and notify listeners."""
        self.status = status
        self._dispatch_update()

    def _handle_message(self, payload: dict[str, Any]) -> None:
        """Merge data and notify sensors."""
        self.last_update_time = dt_util.utcnow()
        self._data.update(payload)
        self._dispatch_update()

    def _dispatch_update(self) -> None:
        """Notify Home Assistant entities to refresh."""
        for callback in self._listeners:
            callback()