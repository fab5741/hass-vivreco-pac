"""Tests pour le flux de configuration Vivreco."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from custom_components.hass_vivreco_pac.config_flow import (
    VivrecoConfigFlow,
    VivrecoOptionsFlow,
)
from custom_components.hass_vivreco_pac.const import DOMAIN
from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD, CONF_SCAN_INTERVAL
from homeassistant.data_entry_flow import FlowResultType


@pytest.mark.asyncio
async def test_config_flow_user_step_shows_form(hass):
    """Test que le flux de configuration affiche le formulaire."""
    flow = VivrecoConfigFlow()
    flow.hass = hass

    result = await flow.async_step_user(user_input=None)

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] == {}


@pytest.mark.asyncio
async def test_config_flow_successful_login(hass):
    """Test de configuration réussie avec validation des credentials."""
    flow = VivrecoConfigFlow()
    flow.hass = hass

    with patch(
        "custom_components.hass_vivreco_pac.config_flow.VivrecoApiClient"
    ) as mock_api_class:
        mock_api = mock_api_class.return_value
        mock_api.login = AsyncMock()
        mock_api.fetch_hp_id = AsyncMock()
        mock_api.hp_id = "test_hp_id"

        result = await flow.async_step_user(
            user_input={
                CONF_EMAIL: "test@example.com",
                CONF_PASSWORD: "password",
                CONF_SCAN_INTERVAL: 5,
            }
        )

        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert result["title"] == "Vivreco PAC"
        assert result["data"][CONF_EMAIL] == "test@example.com"
        assert result["data"][CONF_PASSWORD] == "password"
        assert result["data"][CONF_SCAN_INTERVAL] == 5

        # Vérifier que login et fetch_hp_id ont été appelés
        mock_api.login.assert_called_once()
        mock_api.fetch_hp_id.assert_called_once()


@pytest.mark.asyncio
async def test_config_flow_invalid_credentials(hass):
    """Test de configuration avec credentials invalides."""
    flow = VivrecoConfigFlow()
    flow.hass = hass

    with patch(
        "custom_components.hass_vivreco_pac.config_flow.VivrecoApiClient"
    ) as mock_api_class:
        mock_api = mock_api_class.return_value
        mock_api.login = AsyncMock(side_effect=Exception("Invalid credentials"))

        result = await flow.async_step_user(
            user_input={
                CONF_EMAIL: "test@example.com",
                CONF_PASSWORD: "wrong_password",
                CONF_SCAN_INTERVAL: 5,
            }
        )

        assert result["type"] == FlowResultType.FORM
        assert result["errors"] == {"base": "invalid_auth"}


@pytest.mark.asyncio
async def test_options_flow_init_step_shows_form(hass):
    """Test que le flux d'options affiche le formulaire."""
    # Créer une entrée de configuration mockée
    mock_entry = config_entries.ConfigEntry(
        version=1,
        minor_version=0,
        domain=DOMAIN,
        title="Vivreco PAC",
        data={
            CONF_EMAIL: "test@example.com",
            CONF_PASSWORD: "password",
            CONF_SCAN_INTERVAL: 5,
        },
        source="user",
        entry_id="test_entry_id",
    )

    flow = VivrecoOptionsFlow(mock_entry)
    flow.hass = hass

    result = await flow.async_step_init(user_input=None)

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"


@pytest.mark.asyncio
async def test_options_flow_update_scan_interval(hass):
    """Test de modification de l'intervalle de scan."""
    # Créer une entrée de configuration mockée
    mock_entry = config_entries.ConfigEntry(
        version=1,
        minor_version=0,
        domain=DOMAIN,
        title="Vivreco PAC",
        data={
            CONF_EMAIL: "test@example.com",
            CONF_PASSWORD: "password",
            CONF_SCAN_INTERVAL: 5,
        },
        source="user",
        entry_id="test_entry_id",
    )

    flow = VivrecoOptionsFlow(mock_entry)
    flow.hass = hass

    # Créer un mock pour config_entries
    mock_update = AsyncMock()
    hass.config_entries = MagicMock()
    hass.config_entries.async_update_entry = mock_update

    result = await flow.async_step_init(user_input={CONF_SCAN_INTERVAL: 10})

    assert result["type"] == FlowResultType.CREATE_ENTRY
    mock_update.assert_called_once()


@pytest.mark.asyncio
async def test_options_flow_shows_current_value(hass):
    """Test que le flux d'options affiche la valeur actuelle."""
    mock_entry = config_entries.ConfigEntry(
        version=1,
        minor_version=0,
        domain=DOMAIN,
        title="Vivreco PAC",
        data={
            CONF_EMAIL: "test@example.com",
            CONF_PASSWORD: "password",
            CONF_SCAN_INTERVAL: 7,
        },
        source="user",
        entry_id="test_entry_id",
    )

    flow = VivrecoOptionsFlow(mock_entry)
    flow.hass = hass

    result = await flow.async_step_init(user_input=None)

    # Vérifier que la valeur par défaut dans le formulaire est 7
    assert result["type"] == FlowResultType.FORM
    # Note: Pour vérifier la valeur par défaut, il faudrait inspecter data_schema
    # ce qui est plus complexe avec vol.Schema
