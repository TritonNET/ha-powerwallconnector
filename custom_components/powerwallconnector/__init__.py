"""The TritonNET Powerwall Connector integration."""
from __future__ import annotations

import logging
import re
import voluptuous as vol
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType
from .util import custom_time_period


from .const import (
    DOMAIN,
    CONF_SITENAME,
    CONF_POLLING_FREQUENCY,
    DEFAULT_PORT,
    DEFAULT_POLLING_FREQUENCY,
)
from .coordinator import TritonNetConnectorCoordinator

_LOGGER = logging.getLogger(__name__)
PLATFORMS: list[Platform] = [Platform.SENSOR]

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.All(
            cv.ensure_list,
            [
                vol.Schema(
                    {
                        vol.Required(CONF_SITENAME): cv.string,
                        vol.Required(CONF_HOST): cv.string,
                        vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
                        vol.Optional(
                            CONF_POLLING_FREQUENCY, default=DEFAULT_POLLING_FREQUENCY
                        ): custom_time_period,
                    }
                )
            ],
        )
    },
    extra=vol.ALLOW_EXTRA,
)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Read YAML and trigger the Import Flow."""
    if DOMAIN not in config:
        return True

    for site_config in config[DOMAIN]:
        import_data = site_config.copy()
        if CONF_POLLING_FREQUENCY in import_data:
            freq = import_data[CONF_POLLING_FREQUENCY]
            if isinstance(freq, timedelta):
                import_data[CONF_POLLING_FREQUENCY] = int(freq.total_seconds())

        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN,
                context={"source": "import"},
                data=import_data, # Use the clean data
            )
        )
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the integration from a Config Entry."""
    hass.data.setdefault(DOMAIN, {})

    sitename = entry.data[CONF_SITENAME]
    host = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]
    raw_freq = entry.data.get(CONF_POLLING_FREQUENCY, DEFAULT_POLLING_FREQUENCY)
    
    try:
        if isinstance(raw_freq, (int, float)):
             interval = timedelta(seconds=raw_freq)
        else:
             interval = custom_time_period(raw_freq)
    except:
        interval = timedelta(seconds=5)

    _LOGGER.debug("Setting up Entry for %s at %s:%s", sitename, host, port)

    coordinator = TritonNetConnectorCoordinator(
        hass, 
        host, 
        port, 
        interval, 
        sitename
    )

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok