"""Sensor platform for TritonNET Powerwall Connector."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN, 
    CONF_SITENAME, 
    COORDINATOR_INSTANT,
    COORDINATOR_REGULAR,
    COORDINATOR_INFREQUENT
)
from .sensor_version import TritonNetVersionSensor
from .sensor_soe import TritonNetBatterySensor

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    
    # 1. Get Coordinators
    coordinators = hass.data[DOMAIN][entry.entry_id]
    
    coord_instant = coordinators[COORDINATOR_INSTANT]
    coord_regular = coordinators[COORDINATOR_REGULAR]
    coord_infrequent = coordinators[COORDINATOR_INFREQUENT]
    
    sitename = entry.data[CONF_SITENAME]

    sensors = []

    # 2. Assign Sensors to appropriate coordinators
    
    # Version -> Infrequent (e.g., 1 hour)
    sensors.append(
        TritonNetVersionSensor(coord_infrequent, sitename, "version")
    )

    # Battery -> Instant (e.g., 2 seconds)
    sensors.append(
        TritonNetBatterySensor(coord_instant, sitename)
    )

    # Future sensors can use coord_regular...

    async_add_entities(sensors)
    
    # 3. Initial Refresh for all
    await coord_instant.async_request_refresh()
    await coord_regular.async_request_refresh()
    await coord_infrequent.async_request_refresh()