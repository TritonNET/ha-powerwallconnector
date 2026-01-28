"""The TritonNET Powerwall Connector integration."""
from __future__ import annotations

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
# Correct top-level import
from homeassistant import config_entries 

from .const import DOMAIN, CONF_HOST, CONF_PORT, DEFAULT_PORT
from .client import TritonNetClient

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR]

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the TritonNET Powerwall component from yaml configuration."""
    conf = config.get(DOMAIN)
    if conf is None:
        return True

    # 1. FIX: Handle both List (multiple entries) and Dict (single entry)
    if isinstance(conf, list):
        # YAML configuration is a list of entries
        for entry_conf in conf:
            hass.async_create_task(
                hass.config_entries.flow.async_init(
                    DOMAIN, 
                    context={"source": config_entries.SOURCE_IMPORT}, 
                    data=entry_conf
                )
            )
    else:
        # YAML configuration is a single dictionary
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN, 
                context={"source": config_entries.SOURCE_IMPORT}, 
                data=conf
            )
        )
        
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up TritonNET from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    host = entry.data[CONF_HOST]

    port = entry.data.get(CONF_PORT, DEFAULT_PORT)

    client = TritonNetClient(hass, host, port)
    client.start()

    hass.data[DOMAIN][entry.entry_id] = client

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        client: TritonNetClient = hass.data[DOMAIN].pop(entry.entry_id)
        await client.stop()

    return unload_ok