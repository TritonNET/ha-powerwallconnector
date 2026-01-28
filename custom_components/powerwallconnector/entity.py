"""Base Entity for TritonNET."""
from __future__ import annotations

from homeassistant.helpers.entity import Entity
from .client import TritonNetClient

class TritonNetEntity(Entity):
    """Base class for all TritonNET entities."""

    _attr_has_entity_name = True
    _attr_should_poll = False  # We are Push-based now

    def __init__(self, client: TritonNetClient, sitename: str) -> None:
        """Initialize the entity."""
        self.client = client
        self._sitename = sitename
        self._attr_device_info = {
            "identifiers": {( "powerwallconnector", sitename )},
            "name": f"Powerwall Connector: {sitename}",
            "manufacturer": "Tesla / TritonNET",
            "model": "TritonNET Powerwall Monitor (Local)",
        }

    @property
    def available(self) -> bool:
        """Return True if the WebSocket is connected."""
        return self.client.connected

    async def async_added_to_hass(self) -> None:
        """Register callbacks when entity is added."""
        # Ensure this matches the method name in client.py
        self.async_on_remove(
            self.client.async_add_listener(self.async_write_ha_state)
        )