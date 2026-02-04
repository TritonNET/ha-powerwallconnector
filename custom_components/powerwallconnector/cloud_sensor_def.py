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

CLOUD_SENSOR_DEFINITIONS = [
    # --- BASIC ENERGY TOTALS ---
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
    {
        "name": "Total Grid Export Today",
        "key": "grid_export_today",
        "unit": UnitOfEnergy.WATT_HOUR,
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL,
        "query": """
            SELECT SUM(grid_exported_wh) as value
            FROM energy_records
            WHERE timestamp >= $1 AND timestamp < $2
        """
    },
    {
        "name": "Total Home Usage Today",
        "key": "home_usage_today",
        "unit": UnitOfEnergy.WATT_HOUR,
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL,
        "query": """
            SELECT SUM(home_usage_wh) as value
            FROM energy_records
            WHERE timestamp >= $1 AND timestamp < $2
        """
    },

    # --- FINANCIAL METRICS (Daily) ---
    {
        "name": "Total Import Cost Today",
        "key": "import_cost_today",
        "unit": "$",
        "device_class": SensorDeviceClass.MONETARY,
        "state_class": SensorStateClass.TOTAL,
        "query": """
            SELECT ROUND(SUM(erf.cost_import)::numeric, 4) as value
            FROM energy_record_financials as erf
            JOIN energy_records as er ON erf.id = er.id
            WHERE er.timestamp >= $1 AND er.timestamp < $2
        """
    },
    {
        "name": "Total Export Revenue Today",
        "key": "export_revenue_today",
        "unit": "$",
        "device_class": SensorDeviceClass.MONETARY,
        "state_class": SensorStateClass.TOTAL,
        "query": """
            SELECT ROUND(SUM(erf.revenue_export)::numeric, 4) as value
            FROM energy_record_financials as erf
            JOIN energy_records as er ON erf.id = er.id
            WHERE er.timestamp >= $1 AND er.timestamp < $2
        """
    },
    {
        "name": "Avoided Cost Today",
        "key": "avoided_cost_today",
        "unit": "$",
        "device_class": SensorDeviceClass.MONETARY,
        "state_class": SensorStateClass.TOTAL,
        "query": """
            SELECT ROUND(SUM(erf.savings_solar + erf.savings_battery)::numeric, 4) as value
            FROM energy_record_financials as erf
            JOIN energy_records as er ON erf.id = er.id
            WHERE er.timestamp >= $1 AND er.timestamp < $2
        """
    },
    {
        "name": "Total System Return Today",
        "key": "total_return_today",
        "unit": "$",
        "device_class": SensorDeviceClass.MONETARY,
        "state_class": SensorStateClass.TOTAL,
        "query": """
            SELECT 
              ROUND(SUM(erf.revenue_export + erf.savings_solar + erf.savings_battery)::numeric, 4) as value
            FROM energy_record_financials as erf
            JOIN energy_records as er ON erf.id = er.id
            WHERE er.timestamp >= $1 AND er.timestamp < $2
        """
    },

    # --- FINANCIAL METRICS (Lifetime) ---
    {
        "name": "Lifetime System Return",
        "key": "total_return_lifetime",
        "unit": "$",
        "device_class": SensorDeviceClass.MONETARY,
        "state_class": SensorStateClass.TOTAL,
        "query": """
            SELECT 
              ROUND(SUM(erf.revenue_export + erf.savings_solar + erf.savings_battery)::numeric, 0) as value
            FROM energy_record_financials as erf
            JOIN energy_records as er ON erf.id = er.id
            WHERE er.timestamp < $2 
            AND $1::timestamp IS NOT NULL 
        """
    },

    # --- EFFICIENCY METRICS (Daily) ---
    {
        "name": "Solar Self-Consumption Today",
        "key": "solar_self_consumption_today",
        "unit": PERCENTAGE,
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
        "query": """
            SELECT
              CASE WHEN SUM(solar_generated_wh) > 0
                THEN ROUND(
                    ( (SUM(solar_generated_wh)::numeric - SUM(grid_exported_wh)::numeric) / SUM(solar_generated_wh)::numeric * 100.0 ), 
                    1
                )
                ELSE 0 
              END as value
            FROM energy_records
            WHERE timestamp >= $1 AND timestamp < $2
        """
    },
    {
        "name": "Grid Independence Today",
        "key": "grid_independence_today",
        "unit": PERCENTAGE,
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
        "query": """
            SELECT
              CASE WHEN SUM(home_usage_wh) > 0 
                THEN ROUND(((1 - (SUM(grid_imported_wh)::numeric / SUM(home_usage_wh)::numeric)) * 100), 1)
                ELSE 100 
              END as value
            FROM energy_records
            WHERE timestamp >= $1 AND timestamp < $2
        """
    }
]