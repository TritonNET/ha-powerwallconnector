"""Version sensor for TritonNET Powerwall Connector."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

class TritonNetVersionSensor(CoordinatorEntity, SensorEntity):
    """Representation of the Version Sensor."""

    def __init__(self, coordinator, sitename, sensor_name):
        """Initialize the sensor."""
        # 1. Register the required endpoint logic BEFORE calling super().__init__
        coordinator.register_endpoint("version", "/version")

        super().__init__(coordinator)
        self._sitename = sitename
        
        # Naming: "[SiteName] [Sensor Name]" -> "MyHome Proxy Version"
        self._attr_name = f"{sitename} {sensor_name}"
        self._attr_unique_id = f"{sitename}_version".lower().replace(" ", "_")
        self._attr_icon = "mdi:tag-text-outline"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        # 1. Check if the "version" key exists in the data
        if not self.coordinator.data or "version" not in self.coordinator.data:
            return None
            
        version_data = self.coordinator.data["version"]
        
        if not version_data:
            return None

        # 2. Return the value from the API response
        return version_data.get("version")

    @property
    def extra_state_attributes(self):
        """Return extra attributes."""
        if not self.coordinator.data or "version" not in self.coordinator.data:
            return {}

        version_data = self.coordinator.data["version"]
        return {
            "raw_vint": version_data.get("vint") if version_data else None
        }