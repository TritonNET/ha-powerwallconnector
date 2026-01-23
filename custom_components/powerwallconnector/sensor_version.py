"""Version sensor for TritonNET Powerwall Connector."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from .entity import TritonNetEntity
from .util import get_entity_unique_id

class TritonNetVersionSensor(TritonNetEntity, SensorEntity):
    """Representation of the Version Sensor."""

    def __init__(self, coordinator, sitename, sensor_id_suffix):
        """Initialize the sensor."""
        coordinator.register_endpoint("version", "/version")
        super().__init__(coordinator, sitename)
        
        # Human-readable name for the Entity
        # Combined result in UI: "PWCon My Home Version"
        self._attr_name = "Version"
        
        # Unique ID using the utility
        # Result: "my_home_version"
        self._attr_unique_id = get_entity_unique_id(sitename, sensor_id_suffix)
        
        self._attr_icon = "mdi:tag-text-outline"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if not self.coordinator.data or "version" not in self.coordinator.data:
            return None
        version_data = self.coordinator.data["version"]
        return version_data.get("version") if version_data else None

    @property
    def extra_state_attributes(self):
        """Return extra attributes."""
        if not self.coordinator.data or "version" not in self.coordinator.data:
            return {}
        version_data = self.coordinator.data["version"]
        return {
            "raw_vint": version_data.get("vint") if version_data else None
        }