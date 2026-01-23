"""The TritonNET Powerwall Connector integration."""
from __future__ import annotations

import logging
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
    CONF_HOST,
    CONF_PORT,
    DEFAULT_PORT,
    CONF_POLLING_FREQUENCY,
    CONF_INSTANT,
    CONF_REGULAR,
    CONF_INFREQUENT,
    DEFAULT_INSTANT,
    DEFAULT_REGULAR,
    DEFAULT_INFREQUENT,
    COORDINATOR_INSTANT,
    COORDINATOR_REGULAR,
    COORDINATOR_INFREQUENT,
)
from .coordinator import TritonNetConnectorCoordinator

_LOGGER = logging.getLogger(__name__)
PLATFORMS: list[Platform] = [Platform.SENSOR]

# New Nested Schema
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
                        
                        # Nesting the keys under polling_frequency
                        vol.Optional(CONF_POLLING_FREQUENCY, default={}): vol.Schema(
                            {
                                vol.Optional(CONF_INSTANT, default=DEFAULT_INSTANT): custom_time_period,
                                vol.Optional(CONF_REGULAR, default=DEFAULT_REGULAR): custom_time_period,
                                vol.Optional(CONF_INFREQUENT, default=DEFAULT_INFREQUENT): custom_time_period,
                            }
                        ),
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
        
        # --- Clean Data for JSON Storage ---
        # The schema gives us timedeltas inside the dict, we need ints (seconds)
        if CONF_POLLING_FREQUENCY in import_data:
            freq_data = import_data[CONF_POLLING_FREQUENCY]
            # Convert each timedelta to seconds (int)
            for key in [CONF_INSTANT, CONF_REGULAR, CONF_INFREQUENT]:
                if key in freq_data and isinstance(freq_data[key], timedelta):
                    freq_data[key] = int(freq_data[key].total_seconds())
            
            # Update the main dict with the cleaned sub-dict
            import_data[CONF_POLLING_FREQUENCY] = freq_data

        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN,
                context={"source": "import"},
                data=import_data,
            )
        )
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the integration from a Config Entry."""
    hass.data.setdefault(DOMAIN, {})

    sitename = entry.data[CONF_SITENAME]
    host = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]
    
    # Retrieve the nested dict (or empty dict if missing)
    freq_config = entry.data.get(CONF_POLLING_FREQUENCY, {})

    # --- Helper to extract time ---
    def get_interval(key, default_seconds):
        # 1. Try to get value from the nested dict
        val = freq_config.get(key)
        
        # 2. Safety: If missing, fallback to default
        if val is None:
            return timedelta(seconds=default_seconds)

        # 3. Convert (handles int from storage or string/timedelta edge cases)
        try:
            if isinstance(val, (int, float)):
                return timedelta(seconds=val)
            return custom_time_period(val)
        except:
            return timedelta(seconds=default_seconds)

    # 1. Determine the 3 intervals
    int_instant = get_interval(CONF_INSTANT, DEFAULT_INSTANT)
    int_regular = get_interval(CONF_REGULAR, DEFAULT_REGULAR)
    int_infrequent = get_interval(CONF_INFREQUENT, DEFAULT_INFREQUENT)

    _LOGGER.debug(
        "Setup %s: Instant=%s, Regular=%s, Infrequent=%s", 
        sitename, int_instant, int_regular, int_infrequent
    )

    # 2. Create the 3 Coordinators
    coord_instant = TritonNetConnectorCoordinator(hass, host, port, int_instant, sitename)
    coord_regular = TritonNetConnectorCoordinator(hass, host, port, int_regular, sitename)
    coord_infrequent = TritonNetConnectorCoordinator(hass, host, port, int_infrequent, sitename)

    # 3. Store them
    hass.data[DOMAIN][entry.entry_id] = {
        COORDINATOR_INSTANT: coord_instant,
        COORDINATOR_REGULAR: coord_regular,
        COORDINATOR_INFREQUENT: coord_infrequent,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok