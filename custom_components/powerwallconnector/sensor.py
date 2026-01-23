"""Sensor platform for TritonNET Powerwall Connector."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, CONF_SITENAME
from .sensor_version import TritonNetVersionSensor

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform from a Config Entry."""
    
    # Get the coordinator we created in __init__.py
    coordinator = hass.data[DOMAIN][entry.entry_id]
    sitename = entry.data[CONF_SITENAME]

    sensors = []

    # Instantiate sensors
    sensors.append(
        TritonNetVersionSensor(coordinator, sitename, "version")
    )

    async_add_entities(sensors)
    
    # Force first refresh
    await coordinator.async_request_refresh()