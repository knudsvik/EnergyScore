"""Constants for EnergyScore"""
# Base component constants
NAME = "EnergyScore"
DOMAIN = "energyscore"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "0.0.1"
ISSUE_URL = "https://github.com/knudsvik/energyscore/issues"

# Icons
ICON = "mdi:speedometer"

# Platforms
SENSOR = "sensor"
PLATFORMS = [SENSOR]

# Configuration and options
CONF_PRICE_ENTITY = "price_entity"
CONF_ENERGY_ENTITY = "energy_entity"

# Defaults
DEFAULT_NAME = DOMAIN

# Other
ENERGIES = "energy"
LAST_UPDATED = "last_updated"
PRICES = "price"
QUALITY = "quality"
LAST_HOUR_ENERGY = "last_hour_energy"

# Nordpool
NP_ATTR_RAW = "raw_today"
NP_ATTR_START = "start"
NP_ATTR_VAL = "value"
