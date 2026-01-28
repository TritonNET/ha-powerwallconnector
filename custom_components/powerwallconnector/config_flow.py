"""Config flow for TritonNET Powerwall Connector."""
from __future__ import annotations

from typing import Any
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, CONF_SITENAME, CONF_HOST, CONF_PORT, DEFAULT_PORT

class TritonNetConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for TritonNET Powerwall Connector."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({
                    vol.Required(CONF_SITENAME): str,
                    vol.Required(CONF_HOST): str,
                    vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
                })
            )

        return self.async_create_entry(
            title=f"Powerwall: {user_input[CONF_SITENAME]}", 
            data=user_input
        )

    async def async_step_import(self, import_data: dict[str, Any]) -> FlowResult:
        """Handle import from configuration.yaml."""
        sitename = import_data[CONF_SITENAME]
        
        # Prevent duplicate entries for the same site
        await self.async_set_unique_id(sitename)
        self._abort_if_unique_id_configured(updates=import_data)

        return self.async_create_entry(
            title=f"Powerwall: {sitename}", 
            data=import_data
        )