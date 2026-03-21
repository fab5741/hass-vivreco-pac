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
    config = coordinator.data.get("config", {})

    switches = []
    for key, name in MODE.items():
        supported = False
        if key == "auth_p/etat_glob/aut_app_elec":
            supported = config.get("app_elec", False)
        elif key == "auth_p/etat_glob/aut_ch":
            supported = config.get("ch", False)
        elif key == "auth_p/etat_glob/aut_ecs":
            supported = config.get("ecs", False)
        elif key == "auth_p/etat_glob/aut_raf":
            supported = config.get("raf", False)

        if supported:
            switches.append(VivrecoSwitch(coordinator, key, name))

    async_add_entities(switches)


class VivrecoSwitch(VivrecoBaseEntity, SwitchEntity):
    """Représentation d’un switch Vivreco."""

    def __init__(self, coordinator, key: str, name: str) -> None:
        """Init du switch."""
        super().__init__(coordinator)
        self._key = key
        self._attr_has_entity_name = True
        self._attr_translation_key = name
        self._attr_unique_id = f"{DOMAIN}_{key}"
        self._attr_icon = MODE_ICON_MAPPING.get(name)

    @property
    def is_on(self) -> bool:
        """Retourne l'état actuel du switch depuis les données."""
        return bool(self.coordinator.data.get("settings", {}).get(self._key))

    async def async_turn_on(self, **kwargs) -> None:
        """Allume le switch via l’API."""
        # Récupérer tous les settings actuels (l’API exige un payload complet)
        current_settings = dict(self.coordinator.data.get("settings", {}))

        # Appliquer les modifications
        current_settings[self._key] = True

        # Logiques exclusives
        if self._key == "auth_p/etat_glob/aut_raf":
            current_settings["auth_p/etat_glob/aut_ch"] = False
            # valeur pour mode_raf (toujours "normal")
            current_settings["mode_zone_p/ambiance"] = "normal"

        if self._key == "auth_p/etat_glob/aut_ch":
            current_settings["auth_p/etat_glob/aut_raf"] = False
            # mode_zone_p/ambiance déjà dans current_settings

        await self.coordinator.api.send_command(
            group="customer_settings",
            values=current_settings,
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Éteint le switch via l’API."""
        await self.coordinator.api.send_command(
            group="customer_settings", values={self._key: False}
        )
        await self.coordinator.async_request_refresh()
