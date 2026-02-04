"""PostgreSQL Client for TritonNET Cloud Connector."""
from __future__ import annotations

import logging
import ssl
from datetime import timedelta
import asyncpg

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

_LOGGER = logging.getLogger(__name__)

class TritonNetCloudCoordinator(DataUpdateCoordinator):
    """Coordinator to poll PostgreSQL every 5 minutes."""

    def __init__(self, hass: HomeAssistant, config: dict, sitename: str) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"TritonNET Cloud {sitename}",
            update_interval=timedelta(minutes=5),
        )
        self.config = config
        self.sitename = sitename
        self._pool = None
        self.queries: dict[str, str] = {} 

    def register_query(self, key: str, query: str):
        """Register a query to be executed during update."""
        self.queries[key] = query

    def _make_ssl_context(self) -> ssl.SSLContext:
        """Create SSL context in a background thread."""
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx

    async def _async_setup_pool(self):
        """Setup the asyncpg connection pool."""
        if not self._pool:
            try:
                # SSL Context is created safely in executor to avoid blocking loop
                # ssl_context = await self.hass.async_add_executor_job(self._make_ssl_context)
                
                # UPDATE: You mentioned your server rejected SSL upgrades.
                # We keep SSL=False as per the previous fix to ensure connection success.
                self._pool = await asyncpg.create_pool(
                    user=self.config["user"],
                    password=self.config["password"],
                    database=self.config["database"],
                    host=self.config["host"],
                    port=self.config["port"],
                    ssl=False 
                )
            except Exception as err:
                _LOGGER.error("Failed to create Postgres pool: %s", err)
                raise UpdateFailed(f"Connection Error: {err}")

    async def _async_update_data(self) -> dict:
        """Fetch data from PostgreSQL by running all registered queries."""
        if not self.queries:
            return {}

        await self._async_setup_pool()
        
        data = {}
        
        # --- TIMEZONE FIX ---
        # The database stores timestamps in Local Time.
        # We must query using Local Time (Naive) to match the database records.
        # Previously, converting to UTC shifted the query back 13 hours (into yesterday).
        
        # 1. Get Start of Day in Local Time (e.g. 2026-02-04 00:00:00)
        # .replace(tzinfo=None) strips the timezone so asyncpg treats it as a plain timestamp
        start_of_day = dt_util.start_of_local_day().replace(tzinfo=None)
        
        # 2. End of Day is just +1 Day
        end_of_day = start_of_day + timedelta(days=1)

        async with self._pool.acquire() as connection:
            for key, sql in self.queries.items():
                try:
                    # Pass the Naive Local timestamps directly to the query
                    row = await connection.fetchrow(sql, start_of_day, end_of_day)
                    
                    if row:
                        val = row.get("value") if "value" in row else row[0]
                        data[key] = val or 0
                    else:
                        data[key] = 0
                        
                except Exception as err:
                    _LOGGER.error("Error executing query for %s: %s", key, err)
                    data[key] = None 

        return data

    async def close(self):
        """Close the pool."""
        if self._pool:
            await self._pool.close()