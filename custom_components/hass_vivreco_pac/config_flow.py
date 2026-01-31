"""Gère la configuration de l'intégration Vivreco PAC via l'interface UI."""

import logging

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD, CONF_SCAN_INTERVAL
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import VivrecoApiClient
from .const import DEFAULT_UPDATE_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class VivrecoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Gérer un flux de configuration pour Vivreco PAC."""

    VERSION = 1

    @staticmethod
    def async_get_options_flow(config_entry):
        """Obtenir le flux d'options."""
        return VivrecoOptionsFlow(config_entry)

    async def async_step_user(self, user_input=None):
        """Gérer l'étape initiale."""

        errors = {}

        if user_input is not None:
            # Valider les credentials en tentant une connexion
            session = async_get_clientsession(self.hass)
            api = VivrecoApiClient(
                username=user_input[CONF_EMAIL],
                password=user_input[CONF_PASSWORD],
                session=session,
            )

            try:
                # Tenter de se connecter et récupérer l'ID de la PAC
                await api.login()
                await api.fetch_hp_id()

                # Si on arrive ici, les credentials sont valides
                _LOGGER.info(
                    "Connexion réussie à l'API Vivreco pour HP ID: %s", api.hp_id
                )
                return self.async_create_entry(title="Vivreco PAC", data=user_input)

            except Exception as e:
                _LOGGER.error("Échec de connexion à l'API Vivreco: %s", e)
                errors["base"] = "invalid_auth"

        data_schema = vol.Schema(
            {
                vol.Required(CONF_EMAIL): str,
                vol.Required(CONF_PASSWORD): str,
                vol.Optional(
                    CONF_SCAN_INTERVAL, default=DEFAULT_UPDATE_INTERVAL
                ): vol.All(int, vol.Range(min=1)),
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )


class VivrecoOptionsFlow(config_entries.OptionsFlow):
    """Gérer les options de l'intégration Vivreco PAC."""

    def __init__(self, config_entry):
        """Initialiser le flux d'options."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Gérer les options."""
        if user_input is not None:
            # Mettre à jour les données de l'entrée de configuration
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data={**self.config_entry.data, **user_input},
            )
            return self.async_create_entry(title="", data={})

        # Récupérer la valeur actuelle
        current_interval = self.config_entry.data.get(
            CONF_SCAN_INTERVAL, DEFAULT_UPDATE_INTERVAL
        )

        data_schema = vol.Schema(
            {
                vol.Optional(CONF_SCAN_INTERVAL, default=current_interval): vol.All(
                    int, vol.Range(min=1)
                ),
            }
        )

        return self.async_show_form(step_id="init", data_schema=data_schema)
