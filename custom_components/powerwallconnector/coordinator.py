"""DataUpdateCoordinator for TritonNET Powerwall Connector."""
from __future__ import annotations

import logging
import asyncio
from datetime import timedelta
import async_timeout
import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

_LOGGER = logging.getLogger(__name__)

class TritonNetConnectorCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(
        self, 
        hass: HomeAssistant, 
        host: str, 
        port: int, 
        interval: timedelta, 
        sitename: str
    ) -> None:
        """Initialize."""
        self.host = host
        self.port = port
        self.sitename = sitename
        self.base_url = f"http://{host}:{port}"
        
        # Registry of endpoints: {"key": "/api/path"}
        self._endpoints: dict[str, str] = {}

        super().__init__(
            hass,
            _LOGGER,
            name=f"TritonNET Connector {sitename}",
            update_interval=interval,
        )

    def register_endpoint(self, key: str, path: str) -> None:
        """Register an endpoint to be polled."""
        if key not in self._endpoints:
            _LOGGER.debug(f"Registering endpoint '{key}' with path '{path}'")
            self._endpoints[key] = path

    async def _async_update_data(self):
        """Fetch data from all registered API endpoints."""
        if not self._endpoints:
            _LOGGER.debug("No endpoints registered yet, skipping fetch.")
            return {}

        try:
            async with async_timeout.timeout(10):
                async with aiohttp.ClientSession() as session:
                    # Build full URLs
                    urls = {
                        key: f"{self.base_url}{path}" 
                        for key, path in self._endpoints.items()
                    }

                    # Create fetch tasks
                    tasks = {
                        key: self._fetch_json(session, url) 
                        for key, url in urls.items()
                    }
                    
                    # Run all requests in parallel
                    results = await asyncio.gather(*tasks.values(), return_exceptions=True)
                    
                    # Map results back to keys
                    data = dict(zip(tasks.keys(), results))

                    # Handle errors for individual endpoints
                    for key, result in data.items():
                        if isinstance(result, Exception):
                            _LOGGER.error(f"Error fetching {key}: {result}")
                            data[key] = None

                    return data

        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")

    async def _fetch_json(self, session, url):
        """Helper to fetch a single URL."""
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.json()