import voluptuous as vol
from homeassistant.helpers import config_validation as cv

DOMAIN = "hass-vivreco-pac"

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)
