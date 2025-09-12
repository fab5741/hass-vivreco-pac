"""Client API pour Vivreco PAC."""

import base64
import logging

import aiohttp

from homeassistant.exceptions import ConfigEntryNotReady

from .const import (
    API_CHART_URL_TEMPLATE,
    API_ENERGY_URL_TEMPLATE,
    API_LOGIN_URL,
    API_SETTINGS_COMMAND,
    API_SETTINGS_URL_TEMPLATE,
    API_USER_URL,
)

_LOGGER = logging.getLogger(__name__)


class VivrecoApiClient:
    """Client pour interagir avec l’API Vivreco."""

    def __init__(self, username: str, password: str) -> None:
        """Client API pour Vivreco PAC."""
        self.username = username
        self.password = password
        self.api_token: str | None = None
        self.hp_id: str | None = None
        self.version: str | None = None

    async def login(self) -> None:
        """Connexion et récupération du token API."""
        headers = {"Authorization": self._generate_basic_auth_header()}
        try:
            async with aiohttp.ClientSession() as session:  # noqa: SIM117
                async with session.post(API_LOGIN_URL, headers=headers) as response:
                    if response.status != 200:
                        raise ConfigEntryNotReady(  # noqa: TRY301
                            f"Erreur connexion API: {response.status}"
                        )
                    login_data = await response.json()
                    self.api_token = login_data.get("token")
                    if not self.api_token:
                        raise ConfigEntryNotReady("Aucun token API trouvé.")  # noqa: TRY301
                    _LOGGER.debug("Token API récupéré : %s", self.api_token)
        except Exception as e:  # noqa: BLE001
            raise ConfigEntryNotReady(f"Erreur connexion API: {e}")  # noqa: B904

    async def fetch_hp_id(self) -> None:
        """Récupère l'identifiant de la PAC."""
        headers = self._headers
        async with aiohttp.ClientSession() as session:  # noqa: SIM117
            async with session.get(API_USER_URL, headers=headers) as response:
                if response.status != 200:
                    raise ConfigEntryNotReady(
                        f"Erreur utilisateur API: {response.status}"
                    )
                user_data = await response.json()
                hp_ids = user_data.get("hp_id", [])
                if not hp_ids:
                    raise ConfigEntryNotReady("Aucun identifiant de PAC trouvé.")
                self.hp_id = hp_ids[0]
                _LOGGER.debug("Identifiant de la PAC récupéré : %s", self.hp_id)

    async def get_chart_data(self) -> dict:
        """Récupère les données de type chart."""
        url = API_CHART_URL_TEMPLATE.format(hp_id=self.hp_id)
        api_data = await self._get_json(url)

        _LOGGER.debug(f"Données API récupérées: {api_data}.")  # noqa: G004
        return api_data

    async def get_energy_data(self) -> dict:
        """Récupère les données de consommation d'énergie."""
        url = API_ENERGY_URL_TEMPLATE.format(hp_id=self.hp_id)
        api_data = await self._get_json(url)

        _LOGGER.debug(f"Données API énergie récupérées: {api_data}.")  # noqa: G004
        return api_data

    async def get_settings_data(self) -> dict:
        """Récupère les paramètres de la PAC."""
        url = API_SETTINGS_URL_TEMPLATE.format(hp_id=self.hp_id)
        api_data = await self._get_json(url)

        if api_data and "values" in api_data:
            values_section = api_data["values"]
            self.version = values_section.get("version")
            _LOGGER.debug("Version des settings récupérée : %s", self.version)

        _LOGGER.debug(f"Données API settings récupérées: {api_data}.")  # noqa: G004
        return api_data

    async def send_command(self, group: str, values: dict) -> dict:
        """Envoie une commande à la PAC."""
        url = API_SETTINGS_COMMAND.format(hp_id=self.hp_id)
        headers = self._headers
        payload = {"group": group, "values": values, "version": self.version}

        async with aiohttp.ClientSession() as session:  # noqa: SIM117
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status != 201:
                    _LOGGER.error("Erreur envoi commande %s : %s", url, response.status)
                    return {}
                return await response.json()

    async def _get_json(self, url: str) -> dict:
        """Envoie une requête GET et retourne la réponse JSON."""
        headers = self._headers
        async with aiohttp.ClientSession() as session:  # noqa: SIM117
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    _LOGGER.error("Erreur API GET %s : %s", url, response.status)
                    return {}
                return await response.json()

    def _generate_basic_auth_header(self) -> str:
        """Génère l'en-tête Basic Auth pour la connexion."""
        credentials = f"{self.username}:{self.password}"
        encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode(
            "utf-8"
        )
        return f"Basic {encoded_credentials}"

    @property
    def _headers(self) -> dict:
        """Retourne les en-têtes d’authentification avec le token."""
        return {"Authorization": f"Bearer {self.api_token}"} if self.api_token else {}
