"""Config flow for TritonNET Powerwall Connector."""
from __future__ import annotations

from typing import Any
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, CONF_SITENAME

class TritonNetConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for TritonNET Powerwall Connector."""

    VERSION = 1

    async def async_step_import(self, import_data: dict[str, Any]) -> FlowResult:
        """Handle import from configuration.yaml."""
        sitename = import_data[CONF_SITENAME]
        
        # Prevent duplicate entries
        await self.async_set_unique_id(sitename)
        self._abort_if_unique_id_configured(updates=import_data)

        return self.async_create_entry(
            title=f"Powerwall: {sitename}", 
            data=import_data
        )