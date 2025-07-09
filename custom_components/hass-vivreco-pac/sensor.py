"""Sensor."""

import logging

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
):
    """Initialisation de la plateforme des capteurs."""  # noqa: D401

    coordinator = hass.data[DOMAIN][entry.entry_id]

    # Vérifiez si des données sont disponibles avant de configurer les capteurs
    if not coordinator.data or "values" not in coordinator.data:
        _LOGGER.error("Aucune donnée disponible pour configurer les capteurs.")
        return

    # Créer les capteurs à partir des données
    sensors = []
    for sensor_key in coordinator.data["values"]:
        label = coordinator.data["labels"].get(sensor_key, sensor_key)

        if sensor_key == "state":
            sensors.append(VivrecoStateSensor(coordinator, sensor_key, label))
        elif sensor_key == "comp_one":
            sensors.append(VivrecoCompSensor(coordinator, sensor_key, label))
        elif sensor_key in ["t_ecs", "cons_t_int", "t_int", "cons_t_ecs", "t_ext"]:
            sensors.append(
                VivrecoTemperatureSensor(
                    coordinator, sensor_key, label, SensorDeviceClass.TEMPERATURE
                )
            )

    sensors.append(
        VivrecoConsumptionSensor(
            coordinator, "ch_wh", "ch_wh", 0, SensorDeviceClass.ENERGY
        )
    )
    sensors.append(
        VivrecoConsumptionSensor(
            coordinator, "ecs_wh", "ecs_wh", 1, SensorDeviceClass.ENERGY
        )
    )
    sensors.append(
        VivrecoConsumptionSensor(
            coordinator, "other_wh", "other_wh", 2, SensorDeviceClass.ENERGY
        )
    )

    async_add_entities(sensors)


class VivrecoSensor(CoordinatorEntity, SensorEntity):
    """Représentation d'un capteur Vivreco."""

    def __init__(self, coordinator, sensor_key, name, device_class=None) -> None:
        """Initialisation du capteur."""  # noqa: D401

        super().__init__(coordinator)
        self.coordinator = coordinator
        self._sensor_key = sensor_key
        self._device_class = device_class
        self._attr_name = f"Vivreco PAC {name}"
        self._attr_unique_id = f"vivreco_{sensor_key}"

    @property
    def state(self):
        """Retourne la valeur actuelle du capteur."""
        return self.coordinator.data["values"].get(self._sensor_key)

    @property
    def unique_id(self):
        """Retourne l'identifiant unique du capteur."""
        return f"vivreco_{self._sensor_key}"

    @property
    def device_class(self):
        """Retourne la classe du capteur (température ici)."""
        return self._device_class

    @property
    def device_info(self) -> DeviceInfo:
        """Retourne device info."""
        return DeviceInfo(
            identifiers={("vivreco_pac", self.coordinator.hp_id)},
            model="PAC Connectée",
            manufacturer="Vivreco",
            name="Vivreco PAC",
            configuration_url="https://vivrecocontrol.com",
            serial_number=self.coordinator.hp_id,
        )


class VivrecoTemperatureSensor(VivrecoSensor):
    """Représentation d'un capteur de température Vivreco."""

    @property
    def unit_of_measurement(self):
        """Retourne l'unité de mesure (°C pour les températures)."""
        return "°C"


class VivrecoStateSensor(CoordinatorEntity, SensorEntity):
    """Représentation du capteur d'état de la pompe à chaleur."""

    def __init__(self, coordinator, sensor_key, name) -> None:
        """Initialisation du capteur d'état."""  # noqa: D401

        super().__init__(coordinator)
        self.coordinator = coordinator
        self._sensor_key = sensor_key
        self._attr_name = f"Vivreco PAC {name}"
        self._attr_unique_id = f"vivreco_{sensor_key}"

    @property
    def state(self):
        """Retourne l'état actuel de la pompe à chaleur."""
        state_value = self.coordinator.data["values"].get(self._sensor_key)

        # Gérer les états possibles
        state_mapping = {
            "bt": "Chauffage",
            "degi": "Dégivrage",
            "arret": "Inactive",
        }

        return state_mapping.get(state_value, "Inconnu")

    @property
    def device_info(self) -> DeviceInfo:
        """Retourne device info."""
        return DeviceInfo(
            identifiers={("vivreco_pac", self.coordinator.hp_id)},
            model="PAC Connectée",
            manufacturer="Vivreco",
            name="Vivreco PAC",
            configuration_url="https://vivrecocontrol.com",
            serial_number=self.coordinator.hp_id,
        )

    @property
    def unique_id(self):
        """Retourne l'identifiant unique du capteur."""
        return f"vivreco_{self._sensor_key}"


class VivrecoCompSensor(CoordinatorEntity, BinarySensorEntity):
    """Représentation d'un capteur binaire pour le compresseur."""

    def __init__(self, coordinator, sensor_key, name) -> None:
        """Initialisation du capteur binaire."""  # noqa: D401

        super().__init__(coordinator)
        self.coordinator = coordinator
        self._sensor_key = sensor_key
        self._attr_name = f"Vivreco PAC {name}"
        self._attr_unique_id = f"vivreco_{sensor_key}"

    @property
    def is_on(self):
        """Retourne True si le compresseur est en marche (1), False sinon (0)."""
        return bool(self.coordinator.data["values"].get(self._sensor_key))

    @property
    def unique_id(self):
        """Retourne l'identifiant unique du capteur."""
        return f"vivreco_{self._sensor_key}"

    @property
    def device_info(self) -> DeviceInfo:
        """Retourne device info."""
        return DeviceInfo(
            identifiers={("vivreco_pac", self.coordinator.hp_id)},
            model="PAC Connectée",
            manufacturer="Vivreco",
            name="Vivreco PAC",
            configuration_url="https://vivrecocontrol.com",
            serial_number=self.coordinator.hp_id,
        )


class VivrecoConsumptionSensor(VivrecoSensor):
    """Représentation d'un capteur de consommation quotidienne Vivreco."""

    def __init__(
        self, coordinator, sensor_key, name, energy_type, device_class=None
    ) -> None:
        """Initialisation du capteur avec un nom et un type d'énergie spécifique."""  # noqa: D401

        # Appel du constructeur parent
        super().__init__(coordinator, sensor_key, name, device_class)
        self.energy_type = energy_type  # Stocke le type d'énergie

    @property
    def unit_of_measurement(self):
        """Retourne l'unité de mesure (kWh pour la consommation)."""
        return "kWh"

    @property
    def state_class(self):  # noqa: D102
        return "total_increasing"  # Indique que c'est un compteur cumulatif

    def get_consumption(self):
        """Retourne la consommation pour un type d'énergie donné (ch, ecs, other)."""
        ch_consumption = self.coordinator.data["energy"][self.energy_type]["y"]
        return ch_consumption if ch_consumption is not None else "N/A"

    @property
    def state(self):
        """Retourne la consommation quotidienne en kWh pour le chauffage (ch)."""
        return self.get_consumption()
