"""Tests pour le client API Vivreco."""

from unittest.mock import AsyncMock, patch

import aiohttp
import pytest

from custom_components.hass_vivreco_pac.api import VivrecoApiClient
from homeassistant.exceptions import ConfigEntryNotReady


@pytest.mark.asyncio
async def test_login_success(mock_aiohttp_session, mock_api_responses, mock_response):
    """Test de connexion réussie."""
    api = VivrecoApiClient("test@example.com", "password", mock_aiohttp_session)

    response = await mock_response(200, mock_api_responses["login"])
    mock_aiohttp_session.post = AsyncMock(return_value=response)

    await api.login()

    assert api.api_token == "test_token_123"
    mock_aiohttp_session.post.assert_called_once()


@pytest.mark.asyncio
async def test_login_failure_invalid_credentials(mock_aiohttp_session, mock_response):
    """Test de connexion échouée avec identifiants invalides."""
    api = VivrecoApiClient("test@example.com", "wrong", mock_aiohttp_session)

    response = await mock_response(401, {})
    mock_aiohttp_session.post = AsyncMock(return_value=response)

    with pytest.raises(ConfigEntryNotReady):
        await api.login()


@pytest.mark.asyncio
async def test_login_network_error(mock_aiohttp_session):
    """Test de connexion échouée avec erreur réseau."""
    api = VivrecoApiClient("test@example.com", "password", mock_aiohttp_session)

    mock_aiohttp_session.post = AsyncMock(
        side_effect=aiohttp.ClientError("Network error")
    )

    with pytest.raises(ConfigEntryNotReady):
        await api.login()


@pytest.mark.asyncio
async def test_fetch_hp_id_success(mock_aiohttp_session, mock_api_responses, mock_response):
    """Test de récupération de l'ID de la PAC."""
    api = VivrecoApiClient("test@example.com", "password", mock_aiohttp_session)
    api.api_token = "test_token"

    response = await mock_response(200, mock_api_responses["user"])
    mock_aiohttp_session.get = AsyncMock(return_value=response)

    await api.fetch_hp_id()

    assert api.hp_id == "test_hp_id_456"


@pytest.mark.asyncio
async def test_get_chart_data_success(mock_aiohttp_session, mock_api_responses, mock_response):
    """Test de récupération des données chart."""
    api = VivrecoApiClient("test@example.com", "password", mock_aiohttp_session)
    api.api_token = "test_token"
    api.hp_id = "test_hp_id"

    response = await mock_response(200, mock_api_responses["chart"])
    mock_aiohttp_session.get = AsyncMock(return_value=response)

    data = await api.get_chart_data()

    assert data == mock_api_responses["chart"]
    assert data["elements"]["values"]["t_ext"] == 5.2


@pytest.mark.asyncio
async def test_get_energy_data_success(mock_aiohttp_session, mock_api_responses, mock_response):
    """Test de récupération des données d'énergie."""
    api = VivrecoApiClient("test@example.com", "password", mock_aiohttp_session)
    api.api_token = "test_token"
    api.hp_id = "test_hp_id"

    response = await mock_response(200, mock_api_responses["energy"])
    mock_aiohttp_session.get = AsyncMock(return_value=response)

    data = await api.get_energy_data()

    assert "values" in data
    energy_values = data["values"]["values"]["energyValues"]["total"]
    assert len(energy_values) == 3
    assert energy_values[0]["name"] == "ch"
    assert energy_values[0]["y"] == 7546.0


@pytest.mark.asyncio
async def test_get_json_with_401_invalidates_token(
    mock_aiohttp_session, mock_response
):
    """Test que le token est invalidé en cas d'erreur 401."""
    api = VivrecoApiClient("test@example.com", "password", mock_aiohttp_session)
    api.api_token = "test_token"
    api.hp_id = "test_hp_id"

    response = await mock_response(401, {})
    mock_aiohttp_session.get = AsyncMock(return_value=response)

    data = await api._get_json("http://test.com")

    assert api.api_token is None
    assert data == {}


@pytest.mark.asyncio
async def test_send_command_success(mock_aiohttp_session, mock_response):
    """Test d'envoi de commande réussi."""
    api = VivrecoApiClient("test@example.com", "password", mock_aiohttp_session)
    api.api_token = "test_token"
    api.hp_id = "test_hp_id"
    api.version = "v180"

    response = await mock_response(201, {"status": "ok"})
    mock_aiohttp_session.post = AsyncMock(return_value=response)

    result = await api.send_command(
        "customer_settings", {"auth_p/etat_glob/aut_ch": True}
    )

    assert result == {"status": "ok"}
    mock_aiohttp_session.post.assert_called_once()


@pytest.mark.asyncio
async def test_send_command_network_error(mock_aiohttp_session):
    """Test d'envoi de commande avec erreur réseau."""
    api = VivrecoApiClient("test@example.com", "password", mock_aiohttp_session)
    api.api_token = "test_token"
    api.hp_id = "test_hp_id"
    api.version = "v180"

    mock_aiohttp_session.post = AsyncMock(
        side_effect=aiohttp.ClientError("Network error")
    )

    result = await api.send_command(
        "customer_settings", {"auth_p/etat_glob/aut_ch": True}
    )

    assert result == {}


@pytest.mark.asyncio
async def test_generate_basic_auth_header():
    """Test de génération du header Basic Auth."""
    api = VivrecoApiClient("test@example.com", "password", None)

    header = api._generate_basic_auth_header()

    # dGVzdEBleGFtcGxlLmNvbTpwYXNzd29yZA== est l'encodage base64 de "test@example.com:password"
    assert header == "Basic dGVzdEBleGFtcGxlLmNvbTpwYXNzd29yZA=="


def test_headers_property_with_token():
    """Test de la propriété _headers avec token."""
    api = VivrecoApiClient("test@example.com", "password", None)
    api.api_token = "test_token"

    headers = api._headers

    assert headers == {"Authorization": "Bearer test_token"}


def test_headers_property_without_token():
    """Test de la propriété _headers sans token."""
    api = VivrecoApiClient("test@example.com", "password", None)

    headers = api._headers

    assert headers == {}
