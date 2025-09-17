"""Base Vivreco entity."""

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import MODE_EMOJI


class VivrecoBaseEntity(CoordinatorEntity):
    """Classe de base pour toutes les entités Vivreco PAC."""

    def __init__(self, coordinator) -> None:
        """Base Vivreco entity."""

        super().__init__(coordinator)
        self.coordinator = coordinator

    @property
    def device_info(self) -> DeviceInfo:
        """Retourne les infos communes de l'appareil."""
        config = self.coordinator.data.get("config", {})

        # Affiche uniquement les icônes des options actives
        active_icons = "".join(
            MODE_EMOJI.get(key, "") for key, value in config.items() if value
        )

        return DeviceInfo(
            identifiers={("vivreco_pac", self.coordinator.api.hp_id)},
            model="PAC Connectée",
            manufacturer="Vivreco",
            name="Vivreco PAC",
            configuration_url="https://vivrecocontrol.com",
            serial_number=self.coordinator.api.hp_id,
            hw_version=active_icons or "Aucune option active",
        )
