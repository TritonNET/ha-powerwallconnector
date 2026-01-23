"""Constants for the TritonNET Powerwall Connector integration."""

DOMAIN = "powerwallconnector"

# Configuration Keys
CONF_SITENAME = "sitename"
CONF_HOST = "host"
CONF_PORT = "port"

# Parent Key
CONF_POLLING_FREQUENCY = "polling_frequency"

# Sub-keys for the polling_frequency dictionary
CONF_INSTANT = "instant"
CONF_REGULAR = "regular"
CONF_INFREQUENT = "infrequent"

# Defaults (Seconds)
DEFAULT_PORT = 8675
DEFAULT_INSTANT = 2         # 2 Seconds
DEFAULT_REGULAR = 600       # 10 Minutes
DEFAULT_INFREQUENT = 3600   # 1 Hour

# Coordinator Dictionary Keys
COORDINATOR_INSTANT = "coord_instant"
COORDINATOR_REGULAR = "coord_regular"
COORDINATOR_INFREQUENT = "coord_infrequent"

# API Status Values
GRID_STATUS_CONNECTED = "SystemGridConnected"