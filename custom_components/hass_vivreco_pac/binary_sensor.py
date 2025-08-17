"""Binary sensor platform for Vivreco PAC."""

import logging

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, MODE, MODE_ICON_MAPPING
from .entity import VivrecoBaseEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
):
    """Set up binary sensors for Vivreco PAC."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    if not coordinator.data or "settings" not in coordinator.data:
        _LOGGER.error(
            "Aucune donnée 'settings' disponible pour configurer les binary sensors"
        )
        return

    entities = []

    # Ajouter le compresseur si présent
    if "comp_one" in coordinator.data.get("values", {}):
        entities.append(
            VivrecoCompSensor(
                coordinator,
                "comp_one",
            )
        )

    # Ajouter les modes
    if "settings" in coordinator.data:
        entities.extend(
            VivrecoModeSensor(coordinator, sensor_key, entity_name)
            for sensor_key, entity_name in MODE.items()
        )

    async_add_entities(entities)


class VivrecoModeSensor(VivrecoBaseEntity, BinarySensorEntity):
    """Représentation d'un capteur binaire pour les modes de fonctionnement."""

    def __init__(self, coordinator, sensor_key, name) -> None:
        """Initialisation du capteur binaire."""  # noqa: D401

        super().__init__(coordinator)
        self.coordinator = coordinator
        self._sensor_key = sensor_key
        self._entity_name = name
        self._attr_has_entity_name = True
        self._attr_translation_key = name
        self._attr_unique_id = f"vivreco_{name}"

    @property
    def is_on(self):
        """Retourne True si le mode est actif."""
        return bool(self.coordinator.data["settings"].get(self._sensor_key))

    @property
    def unique_id(self):
        """Retourne l'identifiant unique du capteur."""
        return self._attr_unique_id

    @property
    def icon(self):
        """Retourne une icône spécifique selon le mode."""
        return MODE_ICON_MAPPING.get(self._entity_name, "mdi:eye")


class VivrecoCompSensor(VivrecoBaseEntity, BinarySensorEntity):
    """Représentation d'un capteur binaire pour le compresseur."""

    def __init__(self, coordinator, sensor_key) -> None:
        """Initialisation du capteur binaire."""  # noqa: D401

        super().__init__(coordinator)
        self.coordinator = coordinator
        self._sensor_key = sensor_key
        self._attr_has_entity_name = True
        self._attr_translation_key = sensor_key
        self._attr_unique_id = f"vivreco_{sensor_key}"

    @property
    def is_on(self):
        """Retourne True si le compresseur est en marche (1), False sinon (0)."""
        return bool(self.coordinator.data["values"].get(self._sensor_key))

    @property
    def unique_id(self):
        """Retourne l'identifiant unique du capteur."""
        return self._attr_unique_id

    @property
    def icon(self):
        """Icone."""
        return "mdi:engine-outline"
