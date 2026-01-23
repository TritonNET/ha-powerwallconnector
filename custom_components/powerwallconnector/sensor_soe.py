"""Battery SOE sensor for TritonNET Powerwall Connector."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE

from .entity import TritonNetEntity
from .util import get_entity_unique_id

class TritonNetBatterySensor(TritonNetEntity, SensorEntity):
    """Representation of the Battery Level Sensor."""

    # These attributes enable the automatic battery icon and graph
    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(self, coordinator, sitename):
        """Initialize the sensor."""
        # 1. Register the endpoint
        coordinator.register_endpoint("soe", "/api/system_status/soe")
        
        super().__init__(coordinator, sitename)
        
        self._attr_name = "Battery Level"
        self._attr_unique_id = get_entity_unique_id(sitename, "battery_level")

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if not self.coordinator.data or "soe" not in self.coordinator.data:
            return None
            
        data = self.coordinator.data["soe"]
        
        if not data:
            return None

        # Return the percentage, optionally rounded to 1 decimal place
        raw_value = data.get("percentage")
        if raw_value is not None:
            return round(raw_value, 1)
        return None