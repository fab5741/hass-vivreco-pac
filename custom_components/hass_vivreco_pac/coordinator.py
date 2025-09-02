"""Coordinator Vivreco PAC API integration."""

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class VivrecoDataUpdateCoordinator(DataUpdateCoordinator):
    """Gère la récupération et la mise à jour des données depuis l'API."""

    def __init__(self, hass: HomeAssistant, update_interval) -> None:
        """Initialise le coordinateur."""
        super().__init__(
            hass,
            _LOGGER,
            name="Vivreco PAC",
            update_interval=timedelta(minutes=update_interval),
        )

        self.data = {
            "values": {},
            "labels": {},
            "energy": {},
            "settings": {},
        }

    @property
    def api(self):
        """API Vivreco."""
        return self.hass.data[DOMAIN]["api"]

    async def _async_update_data(self):
        """Récupère les données depuis l'API."""

        _LOGGER.debug("Appel de mise à jour de données depuis Vivreco API")
        # Si le token n'est pas encore récupéré, essayer de se connecter
        if not self.api.api_token:
            await self.api.login()

        # Si l'identifiant de la PAC n'est pas encore récupéré, essayer de le récupérer
        if not self.api.hp_id:
            await self.api.fetch_hp_id()

        chart_data = await self.api.get_chart_data()
        energy_data = await self.api.get_energy_data()
        settings_data = await self.api.get_settings_data()

        if chart_data and "elements" in chart_data:
            self.data = chart_data["elements"]

        if energy_data:
            self.data["energy"] = (
                energy_data.get("values", {})
                .get("values", {})
                .get("energyValues", {})
                .get("total", {})
            )

        if settings_data and "values" in settings_data:
            self.data["settings"] = settings_data["values"]["values"]

        return self.data
