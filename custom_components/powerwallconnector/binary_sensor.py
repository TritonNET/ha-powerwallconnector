"""Binary Sensor platform for TritonNET Powerwall Connector."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)

from .const import DOMAIN, CONF_SITENAME, KEY_GRID_STATUS, VALUE_GRID_CONNECTED
from .entity import TritonNetEntity
from .client import TritonNetClient
from .util import get_entity_unique_id

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary sensor platform."""
    client: TritonNetClient = hass.data[DOMAIN][entry.entry_id]
    sitename = entry.data[CONF_SITENAME]

    async_add_entities([
        TritonNetGridStatusBinarySensor(client, sitename)
    ])

class TritonNetGridStatusBinarySensor(TritonNetEntity, BinarySensorEntity):
    """Binary Sensor for Grid Status."""

    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_name = "Grid Status"

    def __init__(self, client, sitename):
        super().__init__(client, sitename)
        self._attr_unique_id = get_entity_unique_id(sitename, "grid_status")

    @property
    def is_on(self) -> bool | None:
        """Return True if grid is connected."""
        status = self.client.data.get(KEY_GRID_STATUS)
        if status is None:
            return None
        return status == VALUE_GRID_CONNECTED