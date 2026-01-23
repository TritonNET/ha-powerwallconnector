"""Base entity for TritonNET Powerwall Connector."""
from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import TritonNetConnectorCoordinator
from .util import get_device_identifier, get_device_name

class TritonNetEntity(CoordinatorEntity[TritonNetConnectorCoordinator]):
    """Base class for all TritonNET entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: TritonNetConnectorCoordinator, sitename: str) -> None:
        """Initialize the base entity."""
        super().__init__(coordinator)
        self._sitename = sitename
        self._device_identifier = get_device_identifier(sitename)

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_identifier)},
            
            name=get_device_name(self._sitename),
            
            manufacturer="Tesla",
            model="Powerwall Connector Proxy",
            configuration_url=f"http://{self.coordinator.host}:{self.coordinator.port}",
        )