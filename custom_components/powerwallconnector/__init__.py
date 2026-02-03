"""The TritonNET Powerwall Connector integration."""
from __future__ import annotations

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant import config_entries 

from .const import (
    DOMAIN, CONF_HOST, CONF_PORT, DEFAULT_PORT, CONF_SITENAME,
    CONF_PG_HOST, CONF_PG_PORT, CONF_PG_DB, 
    CONF_PG_USER, CONF_PG_PASSWORD, DEFAULT_PG_PORT, DEFAULT_PG_DB
)
from .client import TritonNetClient
from .postgres_client import TritonNetCloudCoordinator
from .util import resolve_env_var

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR]

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the TritonNET Powerwall component from yaml configuration."""
    conf = config.get(DOMAIN)
    if conf is None:
        return True

    entries = conf if isinstance(conf, list) else [conf]

    for entry_conf in entries:
        processed_conf = { k: resolve_env_var(v) for k, v in entry_conf.items() }
        
        # We use sitename as the unique ID
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN, 
                context={"source": config_entries.SOURCE_IMPORT}, 
                data=processed_conf
            )
        )
        
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up TritonNET from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    sitename = entry.data[CONF_SITENAME]
    
    # Storage for this entry
    data_store = {
        "local_client": None,
        "cloud_coordinator": None
    }

    # 1. Setup Local Client (if host is provided)
    if entry.data.get(CONF_HOST):
        host = entry.data[CONF_HOST]
        port = entry.data.get(CONF_PORT, DEFAULT_PORT)
        client = TritonNetClient(hass, host, port)
        client.start()
        data_store["local_client"] = client

    # 2. Setup Cloud Coordinator (if pg_host is provided)
    if entry.data.get(CONF_PG_HOST):
        pg_config = {
            "host": entry.data[CONF_PG_HOST],
            "port": entry.data.get(CONF_PG_PORT, DEFAULT_PG_PORT),
            "user": entry.data[CONF_PG_USER],
            "password": entry.data[CONF_PG_PASSWORD],
            "database": entry.data.get(CONF_PG_DB, DEFAULT_PG_DB),
        }
        coordinator = TritonNetCloudCoordinator(hass, pg_config, sitename)
        # Note: We don't refresh here yet because sensors haven't registered their queries
        data_store["cloud_coordinator"] = coordinator

    hass.data[DOMAIN][entry.entry_id] = data_store

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        data_store = hass.data[DOMAIN].pop(entry.entry_id)
        
        if data_store["local_client"]:
            await data_store["local_client"].stop()
            
        if data_store["cloud_coordinator"]:
            await data_store["cloud_coordinator"].close()

    return unload_ok