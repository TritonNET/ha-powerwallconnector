"""Constants for the TritonNET Powerwall Connector integration."""

DOMAIN = "powerwallconnector"

# Common Config
CONF_SITENAME = "sitename"
CONF_TYPE = "type"

# Connection Types
TYPE_LOCAL = "local"
TYPE_CLOUD = "cloud"

# Local Config
CONF_HOST = "host"
CONF_PORT = "port"
DEFAULT_PORT = 8676

# Cloud (Postgres) Config
CONF_PG_HOST = "pg_host"
CONF_PG_PORT = "pg_port"
CONF_PG_DB = "pg_db"
CONF_PG_USER = "pg_user"
CONF_PG_PASSWORD = "pg_password"

DEFAULT_PG_PORT = 5432
DEFAULT_PG_DB = "postgres" 

# Local Client Consts
KEY_GRID_STATUS = "grid_status"
VALUE_GRID_CONNECTED = "UP"