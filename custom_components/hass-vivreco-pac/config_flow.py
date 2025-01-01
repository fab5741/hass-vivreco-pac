import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

_LOGGER = logging.getLogger(__name__)

class VivrecoConfigFlow(config_entries.ConfigFlow, domain="vivreco_pac"):
    """Gère le flux de configuration de l'intégration Vivreco PAC."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Traitement de la première étape de configuration."""
        if user_input:
            username = user_input.get("username")
            password = user_input.get("password")

            if not username or not password:
                return self.async_show_form(
                    step_id="user",
                    data_schema=self._get_data_schema(),
                    errors={"base": "invalid_credentials"}
                )

            # Enregistrer les informations et poursuivre
            return self.async_create_entry(
                title="Vivreco PAC",
                data={"username": username, "password": password},
            )

        return self.async_show_form(
            step_id="user",
            data_schema=self._get_data_schema(),
        )

    def _get_data_schema(self):
        """Retourne le schéma de la configuration du formulaire."""
        return vol.Schema({
            vol.Required("username"): str,
            vol.Required("password"): str,
        })

