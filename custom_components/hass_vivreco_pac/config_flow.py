"""Gère la configuration de l'intégration Vivreco PAC via l'interface UI."""

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD, CONF_SCAN_INTERVAL

from .const import DEFAULT_UPDATE_INTERVAL, DOMAIN


class VivrecoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Gérer un flux de configuration pour Vivreco PAC."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Gérer l'étape initiale."""

        errors = {}

        if user_input is not None:
            return self.async_create_entry(title="Vivreco PAC", data=user_input)

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
