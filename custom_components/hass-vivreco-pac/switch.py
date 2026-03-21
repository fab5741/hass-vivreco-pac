"""Switch pour le contrôle du chauffage et ECS."""

import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Clés de commande pour l'API
COMMAND_KEY_CH = "auth_p/etat_glob/aut_ch"
COMMAND_KEY_ECS = "auth_p/etat_glob/aut_ecs"


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
):
    """Initialisation de la plateforme switch."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    switches = [
        VivrecoHeatingSwitch(coordinator),
        VivrecoEcsSwitch(coordinator),
    ]

    async_add_entities(switches)


class VivrecoSwitch(CoordinatorEntity, SwitchEntity):
    """Base switch Vivreco."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, coordinator, command_key, name) -> None:
        """Initialisation du switch."""
        super().__init__(coordinator)
        self.coordinator = coordinator
        self._command_key = command_key
        self._attr_name = name
        self._attr_unique_id = f"vivreco_{command_key.replace('/', '_')}"
        self._hp_id = coordinator.hp_id

    @property
    def device_info(self) -> DeviceInfo:
        """Retourne les infos du device."""
        return DeviceInfo(
            identifiers={("vivreco_pac", self._hp_id)},
            model="PAC Connectée",
            manufacturer="Vivreco",
            name="Vivreco PAC",
            configuration_url="https://vivrecocontrol.com",
            serial_number=self._hp_id,
        )

    @property
    def is_on(self) -> bool:
        """Retourne l'état du switch depuis customer_settings_values."""
        return bool(self.coordinator.customer_settings_values.get(self._command_key, False))


class VivrecoHeatingSwitch(VivrecoSwitch):
    """Switch pour le mode chauffage."""

    def __init__(self, coordinator) -> None:
        """Initialisation du switch chauffage."""
        super().__init__(coordinator, COMMAND_KEY_CH, "Mode Chauffage")

    async def async_turn_on(self, **kwargs):
        """Active le chauffage."""
        success = await self.coordinator.async_send_command(self._command_key, True)
        if success:
            self.coordinator.customer_settings_values[self._command_key] = True
            self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Désactive le chauffage."""
        success = await self.coordinator.async_send_command(self._command_key, False)
        if success:
            self.coordinator.customer_settings_values[self._command_key] = False
            self.async_write_ha_state()


class VivrecoEcsSwitch(VivrecoSwitch):
    """Switch pour l'ECS (eau chaude sanitaire)."""

    def __init__(self, coordinator) -> None:
        """Initialisation du switch ECS."""
        super().__init__(coordinator, COMMAND_KEY_ECS, "ECS")

    async def async_turn_on(self, **kwargs):
        """Active l'ECS."""
        success = await self.coordinator.async_send_command(self._command_key, True)
        if success:
            self.coordinator.customer_settings_values[self._command_key] = True
            self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Désactive l'ECS."""
        success = await self.coordinator.async_send_command(self._command_key, False)
        if success:
            self.coordinator.customer_settings_values[self._command_key] = False
            self.async_write_ha_state()
