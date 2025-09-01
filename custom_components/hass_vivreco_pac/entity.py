"""Base Vivreco entity."""

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity


class VivrecoBaseEntity(CoordinatorEntity):
    """Classe de base pour toutes les entités Vivreco PAC."""

    def __init__(self, coordinator) -> None:
        """Base Vivreco entity."""

        super().__init__(coordinator)
        self.coordinator = coordinator

    @property
    def device_info(self) -> DeviceInfo:
        """Retourne les infos communes de l'appareil."""
        return DeviceInfo(
            identifiers={("vivreco_pac", self.coordinator.api.hp_id)},
            model="PAC Connectée",
            manufacturer="Vivreco",
            name="Vivreco PAC",
            configuration_url="https://vivrecocontrol.com",
            serial_number=self.coordinator.api.hp_id,
        )
