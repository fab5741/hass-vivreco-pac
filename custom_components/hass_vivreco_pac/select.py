"""Select platform for Vivreco PAC."""

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, MODE_AMBIANCE_ECS, MODE_AMBIANCE_ZONE_PRINCIPALE
from .entity import VivrecoBaseEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up Vivreco PAC select entities based on config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    config = coordinator.data.get("config", {})

    selects = []

    # Mode zone principale : seulement si chauffage ou rafraîchissement supporté
    if config.get("ch", False) or config.get("raf", False):
        selects.append(VivrecoModeZoneSelect(coordinator))

    # Mode ECS : seulement si ECS supporté
    if config.get("ecs", False):
        selects.append(VivrecoModeEcsSelect(coordinator))

    async_add_entities(selects)


class VivrecoModeZoneSelect(VivrecoBaseEntity, SelectEntity):
    """Select entity pour le mode_zone_p/ambiance."""

    def __init__(self, coordinator) -> None:
        """Init du select."""
        super().__init__(coordinator)
        self._attr_has_entity_name = True
        self._attr_unique_id = f"{DOMAIN}_mode_zone_principale"
        self._attr_options = MODE_AMBIANCE_ZONE_PRINCIPALE
        self._attr_current_option = self._get_current_value()
        self._attr_translation_key = "mode_zone_principale"
        self._attr_entity_category = EntityCategory.CONFIG

    def _get_current_value(self):
        value = self.coordinator.data.get("settings", {}).get("mode_zone_p/ambiance")
        # Si None, on retourne "automatique" par défaut
        return value if value is not None else "normal"

    @property
    def current_option(self):
        """Valeur actuelle."""
        return self._get_current_value()

    @property
    def available(self) -> bool:
        """Le select n'est disponible que si le mode_raf est désactivé."""
        settings = self.coordinator.data.get("settings", {})
        return not settings.get("auth_p/etat_glob/aut_raf", False)

    @property
    def options(self):
        """Liste des options possibles."""
        return list(self._attr_options)

    async def async_select_option(self, option: str):
        """Change le mode_zone_p/ambiance via l'API."""
        if option not in self._attr_options:
            _LOGGER.warning("Option invalide: %s", option)
            return

        await self.coordinator.api.send_command(
            group="customer_settings", values={"mode_zone_p/ambiance": option}
        )
        await self.coordinator.async_request_refresh()


class VivrecoModeEcsSelect(VivrecoBaseEntity, SelectEntity):
    """Select entity pour le mode_ecs/ambiance_ecs (ECS)."""

    def __init__(self, coordinator) -> None:
        """Init du select ECS."""
        super().__init__(coordinator)
        self._attr_has_entity_name = True
        self._attr_unique_id = f"{DOMAIN}_mode_ecs"
        self._attr_options = MODE_AMBIANCE_ECS
        self._attr_translation_key = "mode_ecs"
        self._attr_entity_category = EntityCategory.CONFIG

    def _get_current_value(self):
        value = self.coordinator.data.get("settings", {}).get("mode_ecs/ambiance_ecs")
        return value if value is not None else "normal"

    @property
    def current_option(self):
        """Valeur actuelle ECS."""
        return self._get_current_value()

    @property
    def options(self):
        """Liste des options possibles ECS."""
        return list(self._attr_options)

    async def async_select_option(self, option: str):
        """Change le mode_ecs/ambiance_ecs via l'API."""
        if option not in self._attr_options:
            _LOGGER.warning("Option ECS invalide: %s", option)
            return

        await self.coordinator.api.send_command(
            group="customer_settings", values={"mode_ecs/ambiance_ecs": option}
        )
        await self.coordinator.async_request_refresh()
