"""Binary Sensor platform for TritonNET Powerwall Connector."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN, 
    CONF_SITENAME, 
    COORDINATOR_INSTANT
)
from .binary_sensor_grid import TritonNetGridStatusSensor

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary sensor platform."""
    
    # 1. Get the INSTANT coordinator
    coordinators = hass.data[DOMAIN][entry.entry_id]
    coord_instant = coordinators[COORDINATOR_INSTANT]
    
    sitename = entry.data[CONF_SITENAME]

    sensors = []

    # 2. Add Grid Status Sensor (Instant poll)
    sensors.append(
        TritonNetGridStatusSensor(coord_instant, sitename)
    )

    async_add_entities(sensors)
    
    # 3. Refresh to get data immediately
    await coord_instant.async_request_refresh()