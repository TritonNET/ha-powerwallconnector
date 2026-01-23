"""The TritonNET Powerwall Connector integration."""
from __future__ import annotations

import logging
import voluptuous as vol

from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.discovery import async_load_platform

from .const import (
    DOMAIN,
    CONF_SITENAME,
    CONF_POLLING_FREQUENCY,
    DEFAULT_PORT,
    DEFAULT_POLLING_FREQUENCY,
)
from .coordinator import TritonNetConnectorCoordinator

_LOGGER = logging.getLogger(__name__)

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
                        ): cv.time_period,
                    }
                )
            ],
        )
    },
    extra=vol.ALLOW_EXTRA,
)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the TritonNET Powerwall Connector component."""
    if DOMAIN not in config:
        return True

    hass.data[DOMAIN] = {}

    for site_config in config[DOMAIN]:
        sitename = site_config[CONF_SITENAME]
        host = site_config[CONF_HOST]
        port = site_config[CONF_PORT]
        interval = site_config[CONF_POLLING_FREQUENCY]

        _LOGGER.debug(
            "Setting up TritonNET Connector for site: %s at %s:%s with interval %s",
            sitename,
            host,
            port,
            interval,
        )

        # Initialize the coordinator (Endpoints are registered later by sensors)
        coordinator = TritonNetConnectorCoordinator(
            hass, 
            host, 
            port, 
            interval, 
            sitename
        )
        
        hass.data[DOMAIN][sitename] = coordinator

        hass.async_create_task(
            async_load_platform(hass, "sensor", DOMAIN, site_config, config)
        )

    return True