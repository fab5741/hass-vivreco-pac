"""Number platform for Vivreco PAC."""

import logging

from homeassistant.components.number import NumberDeviceClass, NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CHAUFFAGE_SETPOINTS, DOMAIN, ECS_SETPOINTS
from .entity import VivrecoBaseEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up Vivreco PAC number entities based on config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    numbers = []

    numbers.extend(
        VivrecoEcsConsignesNumber(coordinator, mode, info)
        for mode, info in ECS_SETPOINTS.items()
    )

    numbers.extend(
        VivrecoChauffageConsignesNumber(coordinator, mode, info)
        for mode, info in CHAUFFAGE_SETPOINTS.items()
    )

    async_add_entities(numbers)


class VivrecoEcsConsignesNumber(VivrecoBaseEntity, NumberEntity):
    """Generic ECS setpoint number entity."""

    def __init__(self, coordinator, mode, info) -> None:
        """Init des Numbers."""

        super().__init__(coordinator)
        self._mode = mode
        self._key = info["key"]
        self._attr_unique_id = f"{DOMAIN}_ecs_consigne_{mode}"
        self._attr_has_entity_name = True
        self.native_min_value = info["min"]
        self.native_max_value = info["max"]
        self.native_step = 0.1
        self.mode = "box"
        self._attr_translation_key = f"ecs_consigne_{mode}"
        self.native_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._attr_entity_category = EntityCategory.CONFIG
        self.device_class = NumberDeviceClass.TEMPERATURE
        self._attr_has_entity_name = True

    @property
    def native_value(self):
        """Current ECS temperature for this mode."""
        return self.coordinator.data.get("settings", {}).get(self._key)

    @property
    def available(self) -> bool:
        """La consigne ECS est toujours disponible."""
        return True

    async def async_set_native_value(self, value: float) -> None:
        """Send new ECS temperature to API."""
        _LOGGER.debug("Setting %s temperature to %s", self._mode, value)
        await self.coordinator.api.send_command(
            group="customer_settings",
            values={self._key: value},
        )
        await self.coordinator.async_request_refresh()


class VivrecoChauffageConsignesNumber(VivrecoBaseEntity, NumberEntity):
    """Generic chauffage setpoint number entity."""

    def __init__(self, coordinator, mode, info) -> None:
        """Init des Numbers Chauffage."""
        super().__init__(coordinator)
        self._mode = mode
        self._key = info["key"]
        self._attr_unique_id = f"{DOMAIN}_chauffage_consigne_{mode}"
        self._attr_has_entity_name = True
        self.native_min_value = info["min"]
        self.native_max_value = info["max"]
        self.native_step = 0.1
        self.mode = "box"
        self._attr_translation_key = f"chauffage_consigne_{mode}"
        self.native_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._attr_entity_category = EntityCategory.CONFIG
        self.device_class = NumberDeviceClass.TEMPERATURE

    @property
    def native_value(self):
        """Current chauffage temperature for this mode."""
        return self.coordinator.data.get("settings", {}).get(self._key)

    async def async_set_native_value(self, value: float) -> None:
        """Send new chauffage temperature to API."""
        _LOGGER.debug("Setting chauffage %s temperature to %s", self._mode, value)
        await self.coordinator.api.send_command(
            group="customer_settings",
            values={self._key: value},
        )
        await self.coordinator.async_request_refresh()
