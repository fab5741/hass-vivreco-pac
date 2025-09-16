"""Water heater platform for Vivreco PAC (basé sur states API)."""

import logging

from homeassistant.components.water_heater import (
    WaterHeaterEntity,
    WaterHeaterEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant

from .const import DOMAIN, ECS_SETPOINTS, MODE_AMBIANCE_ECS
from .entity import VivrecoBaseEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
):
    """Set up the Vivreco PAC water heater entity."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([VivrecoWaterHeater(coordinator)])


class VivrecoWaterHeater(VivrecoBaseEntity, WaterHeaterEntity):
    """Représentation de l’ECS comme chauffe-eau."""

    _attr_has_entity_name = True
    _attr_translation_key = "ecs"
    _attr_unique_id = f"{DOMAIN}_water_heater"
    _attr_supported_features = (
        WaterHeaterEntityFeature.TARGET_TEMPERATURE
        | WaterHeaterEntityFeature.ON_OFF
        | WaterHeaterEntityFeature.OPERATION_MODE
    )
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_operation_list = MODE_AMBIANCE_ECS

    def __init__(self, coordinator) -> None:
        """Init."""
        super().__init__(coordinator)
        self._update_temp_range(self.current_operation)

    def _update_temp_range(self, mode: str):
        """Met à jour les min/max dynamiques en fonction du mode ECS."""
        ecs_mode = mode if mode in ECS_SETPOINTS else "normal"
        self._attr_min_temp = ECS_SETPOINTS[ecs_mode]["min"]
        self._attr_max_temp = ECS_SETPOINTS[ecs_mode]["max"]

    @property
    def is_on(self) -> bool:
        """Retourne True si l’ECS est activée (dans les settings)."""
        return bool(
            self.coordinator.data.get("settings", {}).get("auth_p/etat_glob/aut_ecs")
        )

    @property
    def current_temperature(self):
        """Retourne la température actuelle du ballon ECS (valeur `t_ecs`)."""
        return self.coordinator.data.get("values", {}).get("t_ecs")

    @property
    def current_operation(self) -> str:
        """Retourne le mode ECS actuel (hg, reduit, normal, auto)."""
        return self.coordinator.data.get("settings", {}).get(
            "mode_ecs/ambiance_ecs", "normal"
        )

    @property
    def target_temperature(self):
        """Retourne la consigne ECS en fonction du mode actuel."""
        mode = self.current_operation
        key = ECS_SETPOINTS.get(mode, ECS_SETPOINTS["normal"])["key"]
        return self.coordinator.data.get("settings", {}).get(key)

    async def async_set_temperature(self, **kwargs):
        """Définit une nouvelle consigne ECS pour le mode actif."""
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is None:
            return

        mode = self.current_operation
        key = ECS_SETPOINTS.get(mode, ECS_SETPOINTS["normal"])["key"]

        _LOGGER.debug("Changement consigne ECS %s → %.1f °C", mode, temperature)
        await self.coordinator.api.send_command(
            group="customer_settings", values={key: temperature}
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_on(self):
        """Active la production ECS."""
        await self.coordinator.api.send_command(
            group="customer_settings", values={"auth_p/etat_glob/aut_ecs": True}
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self):
        """Désactive la production ECS."""
        await self.coordinator.api.send_command(
            group="customer_settings", values={"auth_p/etat_glob/aut_ecs": False}
        )
        await self.coordinator.async_request_refresh()

    async def async_set_operation_mode(self, operation_mode: str) -> None:
        """Change le mode ECS (hg, reduit, normal, auto)."""
        if operation_mode not in MODE_AMBIANCE_ECS:
            _LOGGER.warning("Mode ECS invalide: %s", operation_mode)
            return

        # Récupère la consigne actuelle pour ce mode, sinon min par défaut
        key = ECS_SETPOINTS.get(operation_mode, ECS_SETPOINTS["normal"])["key"]
        current_temp = self.coordinator.data.get("settings", {}).get(
            key, ECS_SETPOINTS[operation_mode]["min"]
        )

        _LOGGER.debug("Changement mode ECS → %s", operation_mode)
        await self.coordinator.api.send_command(
            group="customer_settings",
            values={key: current_temp, "mode_ecs/ambiance_ecs": operation_mode},
        )
        await self.coordinator.async_request_refresh()
        self._update_temp_range(operation_mode)

    async def async_turn_on(self) -> None:  # noqa: F811
        """Active l'ECS."""
        await self.coordinator.api.send_command(
            group="customer_settings", values={"auth_p/etat_glob/aut_ecs": True}
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self) -> None:  # noqa: F811
        """Désactive l'ECS."""
        await self.coordinator.api.send_command(
            group="customer_settings", values={"auth_p/etat_glob/aut_ecs": False}
        )
        await self.coordinator.async_request_refresh()
