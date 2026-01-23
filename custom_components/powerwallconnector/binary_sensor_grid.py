"""Grid Status binary sensor for TritonNET Powerwall Connector."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)

from .const import GRID_STATUS_CONNECTED
from .entity import TritonNetEntity
from .util import get_entity_unique_id

class TritonNetGridStatusSensor(TritonNetEntity, BinarySensorEntity):
    """Representation of the Grid Status."""

    # "connectivity" class maps True -> "Connected" and False -> "Disconnected"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(self, coordinator, sitename):
        """Initialize the sensor."""
        # 1. Register the endpoint
        coordinator.register_endpoint("grid_status", "/api/system_status/grid_status")
        
        super().__init__(coordinator, sitename)
        
        self._attr_name = "Grid Status"
        self._attr_unique_id = get_entity_unique_id(sitename, "grid_status")

    @property
    def is_on(self) -> bool | None:
        """Return True if the binary sensor is on."""
        if not self.coordinator.data or "grid_status" not in self.coordinator.data:
            return None
            
        data = self.coordinator.data["grid_status"]
        if not data:
            return None

        # Logic: True if status matches constant
        status = data.get("grid_status")
        return status == GRID_STATUS_CONNECTED