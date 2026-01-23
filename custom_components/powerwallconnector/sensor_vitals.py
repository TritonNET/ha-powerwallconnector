"""Vitals sensors (Grid/Battery) for TritonNET Powerwall Connector."""
from __future__ import annotations

import logging
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfElectricPotential,
    UnitOfFrequency,
    UnitOfEnergy,
)

from .entity import TritonNetEntity
from .util import get_entity_unique_id

_LOGGER = logging.getLogger(__name__)

class TritonNetVitalsSensor(TritonNetEntity, SensorEntity):
    """Generic class for sensors derived from the /vitals endpoint."""

    def __init__(
        self, 
        coordinator, 
        sitename, 
        name, 
        id_suffix, 
        json_prefix, 
        json_key,
        device_class,
        unit_of_measurement,
        state_class  # <--- NEW ARGUMENT
    ):
        """
        Initialize the Vitals Sensor.

        :param json_prefix: The dynamic start of the key (e.g., 'TEPOD', 'TESYNC')
        :param json_key: The specific value to extract (e.g., 'POD_nom_energy_remaining')
        """
        coordinator.register_endpoint("vitals", "/vitals")
        
        super().__init__(coordinator, sitename)
        
        self._json_prefix = json_prefix
        self._json_key = json_key
        
        self._attr_name = name
        self._attr_unique_id = get_entity_unique_id(sitename, id_suffix)
        self._attr_device_class = device_class
        self._attr_native_unit_of_measurement = unit_of_measurement
        self._attr_state_class = state_class  # <--- Dynamically set this

    @property
    def native_value(self):
        """Find the value by searching for the prefix in the JSON keys."""
        if not self.coordinator.data or "vitals" not in self.coordinator.data:
            return None
            
        data = self.coordinator.data["vitals"]
        
        # 1. Search for the dynamic key (e.g., find key starting with 'TEPOD--')
        target_block = None
        for key, value in data.items():
            if key.startswith(self._json_prefix):
                target_block = value
                break
        
        if not target_block:
            return None

        # 2. Extract the specific metric
        return target_block.get(self._json_key)