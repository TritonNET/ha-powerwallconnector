"""Sensor platform for TritonNET Powerwall Connector."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfElectricPotential,
    UnitOfFrequency,
    UnitOfEnergy,
    UnitOfPower,
    PERCENTAGE,
    EntityCategory,
)

from .const import DOMAIN, CONF_SITENAME
from .entity import TritonNetEntity
from .client import TritonNetClient
from .util import get_entity_unique_id

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    client: TritonNetClient = hass.data[DOMAIN][entry.entry_id]
    sitename = entry.data[CONF_SITENAME]

    sensors = []

    # --- DIAGNOSTICS (Always Available) ---
    sensors.append(TritonNetConnectionStatus(client, sitename))
    sensors.append(TritonNetLastUpdateSensor(client, sitename))

    # --- SENSOR DEFINITIONS ---
    # 1. System
    sensors.append(TritonNetSensor(client, sitename, "Version", "version", icon="mdi:tag-text"))
    
    # 2. Battery
    sensors.append(TritonNetSensor(client, sitename, "Battery Level", "battery_level", 
                                   device_class=SensorDeviceClass.BATTERY, 
                                   unit=PERCENTAGE, 
                                   state_class=SensorStateClass.MEASUREMENT))
    
    sensors.append(TritonNetSensor(client, sitename, "Battery Capacity", "battery_capacity", 
                                   device_class=SensorDeviceClass.ENERGY, 
                                   unit=UnitOfEnergy.WATT_HOUR, 
                                   state_class=SensorStateClass.TOTAL))
    
    sensors.append(TritonNetSensor(client, sitename, "Battery Energy Remaining", "battery_energy_remaining", 
                                   device_class=SensorDeviceClass.ENERGY, 
                                   unit=UnitOfEnergy.WATT_HOUR, 
                                   state_class=SensorStateClass.TOTAL))

    # 3. Power Flow
    sensors.append(TritonNetSensor(client, sitename, "Battery Power", "battery_power", 
                                   device_class=SensorDeviceClass.POWER, 
                                   unit=UnitOfPower.WATT, 
                                   state_class=SensorStateClass.MEASUREMENT))

    sensors.append(TritonNetSensor(client, sitename, "Site Power", "site_power", 
                                   device_class=SensorDeviceClass.POWER, 
                                   unit=UnitOfPower.WATT, 
                                   state_class=SensorStateClass.MEASUREMENT))
    
    sensors.append(TritonNetSensor(client, sitename, "Solar Power", "solar_power", 
                                   device_class=SensorDeviceClass.POWER, 
                                   unit=UnitOfPower.WATT, 
                                   state_class=SensorStateClass.MEASUREMENT))

    sensors.append(TritonNetSensor(client, sitename, "Home Load", "home_load", 
                                   device_class=SensorDeviceClass.POWER, 
                                   unit=UnitOfPower.WATT, 
                                   state_class=SensorStateClass.MEASUREMENT))

    sensors.append(TritonNetSensor(client, sitename, "Battery Charging Power", "battery_charging_power", 
                                   device_class=SensorDeviceClass.POWER, 
                                   unit=UnitOfPower.WATT, 
                                   state_class=SensorStateClass.MEASUREMENT))
    
    sensors.append(TritonNetSensor(client, sitename, "Battery Discharging Power", "battery_discharging_power", 
                                   device_class=SensorDeviceClass.POWER, 
                                   unit=UnitOfPower.WATT, 
                                   state_class=SensorStateClass.MEASUREMENT))

    sensors.append(TritonNetSensor(client, sitename, "Grid Import Power", "grid_import_power", 
                                   device_class=SensorDeviceClass.POWER, 
                                   unit=UnitOfPower.WATT, 
                                   state_class=SensorStateClass.MEASUREMENT))
    
    sensors.append(TritonNetSensor(client, sitename, "Grid Export Power", "grid_export_power", 
                                   device_class=SensorDeviceClass.POWER, 
                                   unit=UnitOfPower.WATT, 
                                   state_class=SensorStateClass.MEASUREMENT))

    # 4. Energy Totals
    sensors.append(TritonNetSensor(client, sitename, "Battery Energy Charged", "battery_energy_charged", 
                                   device_class=SensorDeviceClass.ENERGY, 
                                   unit=UnitOfEnergy.KILO_WATT_HOUR, 
                                   state_class=SensorStateClass.TOTAL_INCREASING))
    
    sensors.append(TritonNetSensor(client, sitename, "Battery Energy Discharged", "battery_energy_discharged", 
                                   device_class=SensorDeviceClass.ENERGY, 
                                   unit=UnitOfEnergy.KILO_WATT_HOUR, 
                                   state_class=SensorStateClass.TOTAL_INCREASING))

    sensors.append(TritonNetSensor(client, sitename, "Grid Import Energy", "grid_import_energy", 
                                   device_class=SensorDeviceClass.ENERGY, 
                                   unit=UnitOfEnergy.KILO_WATT_HOUR, 
                                   state_class=SensorStateClass.TOTAL_INCREASING))

    sensors.append(TritonNetSensor(client, sitename, "Grid Export Energy", "grid_export_energy", 
                                   device_class=SensorDeviceClass.ENERGY, 
                                   unit=UnitOfEnergy.KILO_WATT_HOUR, 
                                   state_class=SensorStateClass.TOTAL_INCREASING))

    sensors.append(TritonNetSensor(client, sitename, "Solar Energy Produced", "solar_energy_produced", 
                                   device_class=SensorDeviceClass.ENERGY, 
                                   unit=UnitOfEnergy.WATT_HOUR, 
                                   state_class=SensorStateClass.TOTAL_INCREASING))

    # 5. Grid Vitals
    sensors.append(TritonNetSensor(client, sitename, "Grid Voltage", "grid_voltage", 
                                   device_class=SensorDeviceClass.VOLTAGE, 
                                   unit=UnitOfElectricPotential.VOLT, 
                                   state_class=SensorStateClass.MEASUREMENT))

    sensors.append(TritonNetSensor(client, sitename, "Grid Frequency", "grid_frequency", 
                                   device_class=SensorDeviceClass.FREQUENCY, 
                                   unit=UnitOfFrequency.HERTZ, 
                                   state_class=SensorStateClass.MEASUREMENT))

    async_add_entities(sensors)


class TritonNetSensor(TritonNetEntity, SensorEntity):
    """Generic Sensor for values from the C# WebSocket stream."""

    def __init__(self, client, sitename, name, json_key, device_class=None, unit=None, state_class=None, icon=None):
        """Initialize the sensor."""
        super().__init__(client, sitename)
        self._json_key = json_key
        
        self._attr_name = name
        self._attr_unique_id = get_entity_unique_id(sitename, json_key)
        self._attr_device_class = device_class
        self._attr_native_unit_of_measurement = unit
        self._attr_state_class = state_class
        if icon:
            self._attr_icon = icon

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.client.data.get(self._json_key)


class TritonNetConnectionStatus(TritonNetEntity, SensorEntity):
    """
    Reports the status of the connection. 
    If connected, it reports the Powerwall Status (e.g. SystemGridConnected).
    If disconnected, it reports the Connection State (e.g. Connecting, Retrying).
    This entity NEVER goes unavailable.
    """
    _attr_name = "Service Connection"
    _attr_icon = "mdi:ethernet"
    _attr_entity_category = EntityCategory.DIAGNOSTIC 

    def __init__(self, client, sitename):
        super().__init__(client, sitename)
        self._attr_unique_id = get_entity_unique_id(sitename, "service_connection_state")

    @property
    def available(self) -> bool:
        """Override: Always available."""
        return True

    @property
    def native_value(self):
        """Return Powerwall Status if connected, else Connection State."""
        if self.client.connected:
            # We are connected! Return the actual status from the Powerwall
            # Default to "Connected" if the JSON hasn't arrived yet
            return self.client.data.get("status", "Connected")
        
        # We are NOT connected. Return internal state (Connecting, Disconnected, Retrying)
        return self.client.status


class TritonNetLastUpdateSensor(TritonNetEntity, SensorEntity):
    """
    Reports the timestamp of the last message received from the C# service.
    This entity NEVER goes unavailable.
    """
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_name = "Last Update"
    _attr_icon = "mdi:clock-check-outline"
    
    # FIX: Use EntityCategory Enum, not string
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, client, sitename):
        super().__init__(client, sitename)
        self._attr_unique_id = get_entity_unique_id(sitename, "last_update_ts")

    @property
    def available(self) -> bool:
        """Override: Always available."""
        return True

    @property
    def native_value(self):
        """Return the last update time from the client."""
        return self.client.last_update_time