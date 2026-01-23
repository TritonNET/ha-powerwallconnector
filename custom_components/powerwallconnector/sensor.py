"""Sensor platform for TritonNET Powerwall Connector."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.const import (
    UnitOfElectricPotential,
    UnitOfFrequency,
    UnitOfEnergy,
)
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass, # <--- Make sure this is imported
)

from .const import (
    DOMAIN, 
    CONF_SITENAME, 
    COORDINATOR_INSTANT,
    COORDINATOR_INFREQUENT,
)
from .sensor_version import TritonNetVersionSensor
from .sensor_soe import TritonNetBatterySensor
from .sensor_vitals import TritonNetVitalsSensor

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    
    coordinators = hass.data[DOMAIN][entry.entry_id]
    coord_instant = coordinators[COORDINATOR_INSTANT]
    coord_infrequent = coordinators[COORDINATOR_INFREQUENT]
    
    sitename = entry.data[CONF_SITENAME]

    sensors = []

    # --- Existing Sensors ---
    sensors.append(TritonNetVersionSensor(coord_infrequent, sitename, "version"))
    sensors.append(TritonNetBatterySensor(coord_instant, sitename))

    # --- New Vitals Sensors ---
    
    # 1. Grid Voltage (Instantaneous -> MEASUREMENT)
    sensors.append(
        TritonNetVitalsSensor(
            coord_instant, sitename,
            name="Grid Voltage",
            id_suffix="grid_volt",
            json_prefix="TESYNC",
            json_key="ISLAND_VL1N_Main",
            device_class=SensorDeviceClass.VOLTAGE,
            unit_of_measurement=UnitOfElectricPotential.VOLT,
            state_class=SensorStateClass.MEASUREMENT 
        )
    )

    # 2. Grid Frequency (Instantaneous -> MEASUREMENT)
    sensors.append(
        TritonNetVitalsSensor(
            coord_instant, sitename,
            name="Grid Frequency",
            id_suffix="grid_freq",
            json_prefix="TESYNC",
            json_key="ISLAND_FreqL1_Main",
            device_class=SensorDeviceClass.FREQUENCY,
            unit_of_measurement=UnitOfFrequency.HERTZ,
            state_class=SensorStateClass.MEASUREMENT
        )
    )

    # 3. Battery Capacity (Energy Total -> TOTAL)
    # 'Total' allows values to fluctuate (up/down) but satisfies the Energy class requirement.
    sensors.append(
        TritonNetVitalsSensor(
            coord_instant, sitename,
            name="Battery Capacity",
            id_suffix="battery_cap",
            json_prefix="TEPOD",
            json_key="POD_nom_full_pack_energy",
            device_class=SensorDeviceClass.ENERGY,
            unit_of_measurement=UnitOfEnergy.WATT_HOUR,
            state_class=SensorStateClass.TOTAL
        )
    )

    # 4. Battery Remaining (Energy Total -> TOTAL)
    sensors.append(
        TritonNetVitalsSensor(
            coord_instant, sitename,
            name="Battery Energy Remaining",
            id_suffix="battery_rem",
            json_prefix="TEPOD",
            json_key="POD_nom_energy_remaining",
            device_class=SensorDeviceClass.ENERGY,
            unit_of_measurement=UnitOfEnergy.WATT_HOUR,
            state_class=SensorStateClass.TOTAL
        )
    )

    async_add_entities(sensors)
    
    await coord_instant.async_request_refresh()
    await coord_infrequent.async_request_refresh()