"""Sensor."""

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfEnergy, UnitOfTemperature, UnitOfTime
from homeassistant.core import HomeAssistant

from .const import DOMAIN, SENSORS
from .entity import VivrecoBaseEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
):
    """Initialisation de la plateforme des capteurs."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    config = coordinator.data.get("config", {})

    # Vérifiez si des données sont disponibles avant de configurer les capteurs
    if not coordinator.data or "values" not in coordinator.data:
        _LOGGER.error("Aucune donnée disponible pour configurer les capteurs")
        return

    # Créer les capteurs à partir des données
    sensors = []
    for sensor_key in coordinator.data["values"]:
        if sensor_key == "state":
            sensors.append(VivrecoStateSensor(coordinator, sensor_key))  # noqa: PERF401

    for key, meta in SENSORS.items():
        required = meta.get("requires")
        if (
            required == "ch"
            and not (config.get("ch", False) or config.get("raf", False))
        ) or (required not in (None, "ch") and not config.get(required, False)):
            _LOGGER.debug("Sensor %s ignoré (feature %s non supportée)", key, required)
            continue

        sensors.append(
            VivrecoTemperatureSensor(coordinator, key, SensorDeviceClass.TEMPERATURE)
        )

    if config.get("ch", False):
        sensors.append(
            VivrecoConsumptionSensor(
                coordinator, "ch_wh", "ch", SensorDeviceClass.ENERGY
            )
        )

    if config.get("ecs", False):
        sensors.append(
            VivrecoConsumptionSensor(
                coordinator, "ecs_wh", "ecs", SensorDeviceClass.ENERGY
            )
        )

    if config.get("raf", False):
        sensors.append(
            VivrecoConsumptionSensor(
                coordinator, "raf_wh", "raf", SensorDeviceClass.ENERGY
            )
        )

    # Le capteur "other" est toujours créé
    sensors.append(
        VivrecoConsumptionSensor(
            coordinator, "other_wh", "other", SensorDeviceClass.ENERGY
        )
    )

    # Capteurs de durée de fonctionnement
    if config.get("ch", False):
        sensors.append(
            VivrecoDurationSensor(coordinator, "ch_duration", "ch")
        )

    if config.get("ecs", False):
        sensors.append(
            VivrecoDurationSensor(coordinator, "ecs_duration", "ecs")
        )

    if config.get("raf", False):
        sensors.append(
            VivrecoDurationSensor(coordinator, "raf_duration", "raf")
        )

    # Durée "other" toujours créée
    sensors.append(
        VivrecoDurationSensor(coordinator, "other_duration", "other")
    )

    async_add_entities(sensors)


class VivrecoSensor(VivrecoBaseEntity, SensorEntity):
    """Représentation d'un capteur Vivreco."""

    def __init__(self, coordinator, sensor_key, device_class=None) -> None:
        """Initialisation du capteur."""

        super().__init__(coordinator)
        self.coordinator = coordinator
        self._sensor_key = sensor_key
        self._device_class = device_class
        self._attr_has_entity_name = True
        self._attr_translation_key = sensor_key
        self._attr_unique_id = f"vivreco_{sensor_key}"

    @property
    def native_value(self):
        """Valeur native."""
        return self.coordinator.data["values"].get(self._sensor_key)

    @property
    def unique_id(self):
        """Retourne l'identifiant unique du capteur."""
        return f"vivreco_{self._sensor_key}"

    @property
    def device_class(self):
        """Retourne la classe du capteur (température ici)."""
        return self._device_class


class VivrecoTemperatureSensor(VivrecoSensor):
    """Représentation d'un capteur de température Vivreco."""

    @property
    def native_unit_of_measurement(self):
        """Retourne l'unité de mesure (°C pour les températures)."""
        return UnitOfTemperature.CELSIUS

    @property
    def state_class(self):
        """TYpe mesure."""
        return SensorStateClass.MEASUREMENT


class VivrecoStateSensor(VivrecoBaseEntity, SensorEntity):
    """Représentation du capteur d'état de la pompe à chaleur."""

    def __init__(self, coordinator, sensor_key) -> None:
        """Initialisation du capteur d'état."""

        super().__init__(coordinator)
        self.coordinator = coordinator
        self._sensor_key = sensor_key
        self._attr_has_entity_name = True
        self._attr_translation_key = sensor_key
        self._attr_unique_id = f"vivreco_{sensor_key}"

        # Déclaration comme capteur ENUM
        self._attr_device_class = SensorDeviceClass.ENUM
        self._attr_options = ["bt", "degi", "raf", "ecs", "arret"]

    @property
    def native_value(self):
        """Retourne l'état actuel de la pompe à chaleur."""
        return self.coordinator.data["values"].get(self._sensor_key)

    @property
    def unique_id(self):
        """Retourne l'identifiant unique du capteur."""
        return f"vivreco_{self._sensor_key}"


class VivrecoConsumptionSensor(VivrecoSensor):
    """Représentation d'un capteur de consommation quotidienne Vivreco."""

    def __init__(self, coordinator, sensor_key, energy_type, device_class=None) -> None:
        """Initialisation du capteur avec un nom et un type d'énergie spécifique."""

        # Appel du constructeur parent
        super().__init__(coordinator, sensor_key, device_class)
        self.energy_type = energy_type  # Stocke le type d'énergie

    @property
    def native_unit_of_measurement(self):
        """Retourne l'unité de mesure (kWh pour la consommation)."""
        return UnitOfEnergy.KILO_WATT_HOUR

    @property
    def state_class(self):
        """Type compteur cumulatif."""
        return SensorStateClass.TOTAL_INCREASING

    def get_consumption(self):
        """Retourne la consommation pour un type d'énergie donné (ch, ecs, raf, other)."""
        ch_consumption = None

        # Vérifier que energy existe et est bien un tableau
        energy_data = self.coordinator.data.get("energy")
        if not energy_data or not isinstance(energy_data, list):
            return None

        for item in energy_data:
            if item.get("name") == self.energy_type:
                ch_consumption = item.get("y")
                break

        return ch_consumption

    @property
    def state(self):
        """Retourne la consommation quotidienne en kWh pour le chauffage (ch)."""
        return self.get_consumption()


class VivrecoDurationSensor(VivrecoSensor):
    """Représentation d'un capteur de durée de fonctionnement Vivreco."""

    def __init__(self, coordinator, sensor_key, duration_type) -> None:
        """Initialisation du capteur avec un nom et un type de durée spécifique."""

        # Appel du constructeur parent
        super().__init__(coordinator, sensor_key, SensorDeviceClass.DURATION)
        self.duration_type = duration_type

    @property
    def native_unit_of_measurement(self):
        """Retourne l'unité de mesure (heures pour la durée)."""
        return UnitOfTime.HOURS

    @property
    def state_class(self):
        """Type compteur cumulatif."""
        return SensorStateClass.TOTAL_INCREASING

    def get_duration(self):
        """Retourne la durée de fonctionnement pour un type donné (ch, ecs, raf, other)."""
        # Vérifier que time_values existe et est bien un tableau
        time_data = self.coordinator.data.get("time_values")
        if not time_data or not isinstance(time_data, list):
            return None

        for item in time_data:
            if item.get("name") == self.duration_type:
                return item.get("y")

        return None

    @property
    def state(self):
        """Retourne la durée totale de fonctionnement en heures."""
        return self.get_duration()
