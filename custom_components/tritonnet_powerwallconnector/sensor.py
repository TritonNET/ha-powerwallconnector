"""Sensor platform for TritonNET Powerwall Connector."""
from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import DOMAIN, CONF_SITENAME

# Import your sensor classes
from .sensor_version import TritonNetVersionSensor

async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the sensor platform."""
    if discovery_info is None:
        return

    sitename = discovery_info[CONF_SITENAME]
    coordinator = hass.data[DOMAIN][sitename]

    sensors = []

    # Instantiate Version Sensor
    # (Inside __init__, this sensor will call coordinator.register_endpoint)
    sensors.append(
        TritonNetVersionSensor(coordinator, sitename, "Version")
    )

    # Add sensors to Home Assistant
    async_add_entities(sensors)

    # Force a refresh now that sensors have registered their endpoints.
    await coordinator.async_request_refresh()