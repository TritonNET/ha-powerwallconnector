"""Base Entity for TritonNET."""
from __future__ import annotations

from homeassistant.helpers.entity import Entity
from .client import TritonNetClient
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .postgres_client import TritonNetCloudCoordinator

class TritonNetPowerwallCloudConnectorEntity(CoordinatorEntity):
    """Base class for Cloud (Postgres) entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: TritonNetCloudCoordinator, sitename: str) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._sitename = sitename
        self._attr_device_info = {
            "identifiers": {( "powerwallconnector_cloud", sitename )},
            "name": f"PW Cloud Con {sitename}",
            "manufacturer": "Tesla / TritonNET",
            "model": "TritonNET Cloud Analytics",
        }