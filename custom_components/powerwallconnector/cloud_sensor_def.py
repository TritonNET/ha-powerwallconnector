from homeassistant.const import (
    UnitOfElectricPotential,
    UnitOfFrequency,
    UnitOfEnergy,
    UnitOfPower,
    PERCENTAGE,
    EntityCategory,
)

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)

# =============================================================================
#  CLOUD SENSOR CONFIGURATION
# =============================================================================
# Define your SQL sensors here.
# The Coordinator will automatically provide $1 (start of today UTC) and $2 (end of today UTC).
# Make sure your query returns a column named 'value' or just one aggregate column.

CLOUD_SENSOR_DEFINITIONS = [
    {
        "name": "Total Solar Generation Today",
        "key": "solar_gen_today",
        "unit": UnitOfEnergy.WATT_HOUR,
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL,
        "query": """
            SELECT SUM(solar_generated_wh) as value
            FROM energy_records
            WHERE timestamp >= $1 AND timestamp < $2
        """
    },
    # Example of another entity (You can add your 10+ others here)
    {
        "name": "Total Grid Import Today",
        "key": "grid_import_today",
        "unit": UnitOfEnergy.WATT_HOUR,
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL,
        "query": """
            SELECT SUM(grid_imported_wh) as value
            FROM energy_records
            WHERE timestamp >= $1 AND timestamp < $2
        """
    },
]