"""Switch platform for Vivreco PAC."""

import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, MODE, MODE_ICON_MAPPING
from .entity import VivrecoBaseEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up Vivreco PAC switches based on config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    switches = []

    for key, name in MODE.items():
        switches.append(VivrecoSwitch(coordinator, key, name))

    async_add_entities(switches)


class VivrecoSwitch(VivrecoBaseEntity, SwitchEntity):
    """Représentation d’un switch Vivreco."""

    def __init__(self, coordinator, key, name) -> None:
        """Init du switch."""
        super().__init__(coordinator)
        self._key = key
        self._attr_has_entity_name = True
        self._attr_translation_key = name
        self._attr_unique_id = f"{DOMAIN}_{key}"
        self._attr_icon = MODE_ICON_MAPPING.get(name)

    @property
    def is_on(self):
        """Retourne l'état actuel du switch depuis les données."""
        return bool(self.coordinator.data.get("settings", {}).get(self._key))

    async def async_turn_on(self, **kwargs):
        """Allume le switch via l’API."""
        values = {self._key: True}

        # logiques exclusives
        if self._key == "auth_p/etat_glob/aut_raf":
            values["auth_p/etat_glob/aut_ch"] = False
            # valeur pour mode_raf (toujours "normal")
            values["mode_zone_p/ambiance"] = "normal"

        if self._key == "auth_p/etat_glob/aut_ch":
            values["auth_p/etat_glob/aut_raf"] = False
            # récupération valeur actuelle depuis le coordinator / select
            current_zone = self.coordinator.data.get("settings", {}).get(
                "mode_zone_p/ambiance", "normal"
            )
            values["mode_zone_p/ambiance"] = current_zone

        await self.coordinator.api.send_command(
            group="customer_settings",
            values=values,
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """Éteint le switch via l’API."""
        await self.coordinator.api.send_command(
            group="customer_settings", values={self._key: False}
        )
        await self.coordinator.async_request_refresh()
