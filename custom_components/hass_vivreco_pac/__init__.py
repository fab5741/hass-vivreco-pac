"""Vivreco PAC integration."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv

from .api import VivrecoApiClient
from .const import DEFAULT_UPDATE_INTERVAL, DOMAIN, PLATFORMS
from .coordinator import VivrecoDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config):
    """Plus de support configuration.yaml, tout passe par le config flow."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Vivreco PAC from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Initialise l'API
    api = VivrecoApiClient(
        username=entry.data[CONF_EMAIL],
        password=entry.data[CONF_PASSWORD],
    )

    # Création du coordinateur
    coordinator = VivrecoDataUpdateCoordinator(
        hass,
        api,
        update_interval=entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_UPDATE_INTERVAL),
    )
    await coordinator.async_config_entry_first_refresh()

    # Stocker le coordinateur
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_update_entry))

    return True


async def async_update_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update options."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""

    _LOGGER.debug("async_unload_entry: %s", entry)
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
