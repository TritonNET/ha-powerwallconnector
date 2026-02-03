"""Config flow for TritonNET Powerwall Connector."""
from __future__ import annotations

from typing import Any
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DOMAIN, 
    CONF_SITENAME, 
    CONF_HOST, 
    CONF_PORT, 
    DEFAULT_PORT, 
    CONF_TYPE, 
    TYPE_LOCAL
)

class TritonNetConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for TritonNET Powerwall Connector."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step (UI Setup). Defaults to Local."""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({
                    vol.Required(CONF_SITENAME): str,
                    vol.Required(CONF_HOST): str,
                    vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
                })
            )

        # For UI setup, we assume Local type for now
        user_input[CONF_TYPE] = TYPE_LOCAL
        unique_id = f"{user_input[CONF_SITENAME]}_{TYPE_LOCAL}"
        
        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=f"Powerwall: {user_input[CONF_SITENAME]} (Local)", 
            data=user_input
        )

    async def async_step_import(self, import_data: dict[str, Any]) -> FlowResult:
        """Handle import from configuration.yaml."""
        sitename = import_data[CONF_SITENAME]
        conn_type = import_data.get(CONF_TYPE, TYPE_LOCAL)
        
        # FIX: Generate a composite ID so "Local" and "Cloud" don't conflict
        unique_id = f"{sitename}_{conn_type}"
        
        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured(updates=import_data)

        # Create the entry with a distinct title
        return self.async_create_entry(
            title=f"Powerwall: {sitename} ({conn_type})", 
            data=import_data
        )