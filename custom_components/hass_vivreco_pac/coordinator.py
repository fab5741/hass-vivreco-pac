"""Coordinator Vivreco PAC API integration."""

import base64
from datetime import timedelta
import logging

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    API_CHART_URL_TEMPLATE,
    API_ENERGY_URL_TEMPLATE,
    API_LOGIN_URL,
    API_SETTINGS_URL_TEMPLATE,
    API_USER_URL,
)

_LOGGER = logging.getLogger(__name__)


class VivrecoDataUpdateCoordinator(DataUpdateCoordinator):
    """Gère la récupération et la mise à jour des données depuis l'API."""

    def __init__(
        self, hass: HomeAssistant, username, password, update_interval
    ) -> None:
        """Initialise le coordinateur et récupère l'identifiant de la PAC."""
        self.username = username
        self.password = password
        self.api_token = None
        self.hp_id = None

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

    async def _async_update_data(self):
        """Récupère les données depuis l'API."""

        _LOGGER.debug("Appel de mise à jour de données depuis Vivreco API")
        # Si le token n'est pas encore récupéré, essayer de se connecter
        if not self.api_token:
            await self._async_login()

        # Si l'identifiant de la PAC n'est pas encore récupéré, essayer de le récupérer
        if not self.hp_id:
            await self._async_fetch_hp_id()

        # Construire l'URL de l'API avec l'identifiant de la PAC
        api_chart_url = API_CHART_URL_TEMPLATE.format(hp_id=self.hp_id)
        api_energy_url = API_ENERGY_URL_TEMPLATE.format(hp_id=self.hp_id)
        api_settings_url = API_SETTINGS_URL_TEMPLATE.format(hp_id=self.hp_id)

        headers = {"Authorization": f"Bearer {self.api_token}"}
        try:
            async with aiohttp.ClientSession() as session:  # noqa: SIM117
                async with session.get(api_chart_url, headers=headers) as response:
                    if response.status != 200:
                        _LOGGER.error(f"Erreur API : {response.status}")  # noqa: G004
                        return self.data

                    api_data = await response.json()
                    if "elements" not in api_data:
                        _LOGGER.error(
                            "Aucune donnée 'elements' trouvée dans la réponse de l'API"
                        )
                        return self.data

                    _LOGGER.debug(f"Données API récupérées : {api_data}")  # noqa: G004
                    self.data = api_data["elements"]

        except aiohttp.ClientError as e:
            _LOGGER.error(f"Erreur lors de la communication avec l'API : {e}")  # noqa: G004
        except Exception as e:  # noqa: BLE001
            _LOGGER.error(f"Erreur lors de la conversion de la réponse JSON : {e}")  # noqa: G004

        try:
            async with aiohttp.ClientSession() as session:  # noqa: SIM117
                async with session.get(api_energy_url, headers=headers) as response:
                    if response.status != 200:
                        _LOGGER.error(f"Erreur API : {response.status}")  # noqa: G004
                        return self.data

                    api_data = await response.json()
                    _LOGGER.debug(f"Données API énergie récupérées : {api_data}")  # noqa: G004

                    # Vérifier si "values" est une liste ou un dictionnaire
                    if isinstance(api_data.get("values"), list):
                        for item in api_data["values"]:
                            if "energyValues" in item:
                                self.data["energy"] = item["energyValues"]["total"]
                                break
                    else:
                        self.data["energy"] = (
                            api_data["values"]
                            .get("values", {})
                            .get("energyValues", {})
                            .get("total")
                        )

        except aiohttp.ClientError as e:
            _LOGGER.error(f"Erreur lors de la communication avec l'API : {e}")  # noqa: G004
        except Exception as e:  # noqa: BLE001
            _LOGGER.error(f"Erreur lors de la conversion de la réponse JSON : {e}")  # noqa: G004

        try:
            async with aiohttp.ClientSession() as session:  # noqa: SIM117
                async with session.get(api_settings_url, headers=headers) as response:
                    if response.status != 200:
                        _LOGGER.error(f"Erreur API : {response.status}")  # noqa: G004
                        return self.data

                    api_data = await response.json()
                    _LOGGER.debug(f"Données API settings récupérées : {api_data}")  # noqa: G004

                    if "values" not in api_data.get("values"):
                        _LOGGER.error(
                            "Aucune donnée 'values' trouvée dans la réponse de l'API"
                        )
                        return self.data

                    self.data["settings"] = api_data.get("values")["values"]

        except aiohttp.ClientError as e:
            _LOGGER.error(f"Erreur lors de la communication avec l'API : {e}")  # noqa: G004
        except Exception as e:  # noqa: BLE001
            _LOGGER.error(f"Erreur lors de la conversion de la réponse JSON : {e}")  # noqa: G004

        return self.data

    async def _async_login(self):
        """Effectue la connexion via Basic Auth et récupère le token API."""

        headers = {"Authorization": self._generate_basic_auth_header()}
        try:
            async with aiohttp.ClientSession() as session:  # noqa: SIM117
                async with session.post(API_LOGIN_URL, headers=headers) as response:
                    if response.status != 200:
                        _LOGGER.error(
                            f"Erreur lors de la connexion : {response.status}"  # noqa: G004
                        )
                        raise ConfigEntryNotReady("Impossible de se connecter à l'API.")  # noqa: TRY301

                    login_data = await response.json()
                    self.api_token = login_data.get("token")
                    if not self.api_token:
                        _LOGGER.error("Aucun token API trouvé dans la réponse")
                        raise ConfigEntryNotReady("Aucun token API trouvé.")  # noqa: TRY301
                    _LOGGER.debug(f"Token API récupéré : {self.api_token}")  # noqa: G004
        except aiohttp.ClientError as e:
            _LOGGER.error(f"Erreur lors de la tentative de connexion : {e}")  # noqa: G004
            raise ConfigEntryNotReady("Erreur de connexion à l'API.")  # noqa: B904
        except Exception as e:  # noqa: BLE001
            _LOGGER.error(f"Erreur inconnue lors de la connexion : {e}")  # noqa: G004
            raise ConfigEntryNotReady("Erreur inconnue lors de la connexion à l'API.")  # noqa: B904

    async def _async_fetch_hp_id(self):
        """Récupère l'identifiant de la PAC via l'API utilisateur."""

        headers = {"Authorization": f"Bearer {self.api_token}"}
        try:
            async with aiohttp.ClientSession() as session:  # noqa: SIM117
                async with session.get(API_USER_URL, headers=headers) as response:
                    if response.status != 200:
                        _LOGGER.error(
                            f"Erreur lors de la récupération de l'utilisateur : {response.status} - {headers}"  # noqa: G004
                        )
                        raise ConfigEntryNotReady(  # noqa: TRY301
                            "Impossible de récupérer l'identifiant de la PAC."
                        )

                    user_data = await response.json()
                    hp_ids = user_data.get("hp_id", [])
                    if not hp_ids:
                        _LOGGER.error(
                            "Aucun identifiant de PAC trouvé dans la réponse utilisateur"
                        )
                        raise ConfigEntryNotReady("Aucun identifiant de PAC trouvé.")  # noqa: TRY301

                    self.hp_id = hp_ids[0]  # Utilise le premier identifiant trouvé
                    _LOGGER.debug(f"Identifiant de la PAC récupéré : {self.hp_id}")  # noqa: G004
        except aiohttp.ClientError as e:
            _LOGGER.error(
                f"Erreur lors de la récupération de l'identifiant de la PAC : {e}"  # noqa: G004
            )
            raise ConfigEntryNotReady(  # noqa: B904
                "Erreur de récupération de l'identifiant de la PAC."
            )
        except Exception as e:  # noqa: BLE001
            _LOGGER.error(
                f"Erreur inconnue lors de la récupération de l'identifiant de la PAC : {e}"  # noqa: G004
            )
            raise ConfigEntryNotReady(  # noqa: B904
                "Erreur inconnue lors de la récupération de l'identifiant de la PAC."
            )

    def _generate_basic_auth_header(self):
        """Génère l'en-tête Basic Auth pour la connexion."""

        credentials = f"{self.username}:{self.password}"
        encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode(
            "utf-8"
        )
        return f"Basic {encoded_credentials}"
