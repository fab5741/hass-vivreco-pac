"""Tests pour le coordinateur Vivreco."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.hass_vivreco_pac.coordinator import VivrecoDataUpdateCoordinator


@pytest.fixture
def mock_api_for_coordinator(mock_api_responses):
    """Fixture pour créer un mock complet de l'API."""
    mock_api = MagicMock()
    mock_api.api_token = "test_token"
    mock_api.hp_id = "test_hp_id"
    mock_api.login = AsyncMock()
    mock_api.fetch_hp_id = AsyncMock()

    # Mock des appels de données
    mock_api.get_chart_data = AsyncMock(return_value=mock_api_responses["chart"])
    mock_api.get_chart_data_since1h = AsyncMock(
        return_value=mock_api_responses["chart_since1h"]
    )
    mock_api.get_usage_data = AsyncMock(return_value=mock_api_responses["usage"])
    mock_api.get_energy_data = AsyncMock(return_value=mock_api_responses["energy"])
    mock_api.get_settings_data = AsyncMock(return_value=mock_api_responses["settings"])

    return mock_api


@pytest.mark.asyncio
async def test_coordinator_initialization(hass):
    """Test de l'initialisation du coordinateur."""
    coordinator = VivrecoDataUpdateCoordinator(hass, update_interval=5)

    assert coordinator.name == "Vivreco PAC"
    assert "values" in coordinator.data
    assert "humidity" in coordinator.data
    assert "usage" in coordinator.data


@pytest.mark.asyncio
async def test_coordinator_update_data_success(hass, mock_api_for_coordinator):
    """Test complet de mise à jour des données (standard, humidité et usage)."""
    coordinator = VivrecoDataUpdateCoordinator(hass, update_interval=5)
    hass.data["hass_vivreco_pac"] = {"api": mock_api_for_coordinator}

    await coordinator._async_update_data()

    # Vérification des données de base (chart_data)
    assert coordinator.data["values"]["t_ext"] == 5.2
    assert coordinator.data["values"]["t_int"] == 21.5

    # Vérification de l'humidité (dernière valeur de la liste dans chart_since1h)
    # Dans ton mock_api_responses, la dernière valeur de 't_ext' est 8.6
    # (Adapte ici selon la valeur réelle dans ta fixture pour 'hyg')
    assert coordinator.data["humidity"] is not None

    # Vérification du calcul d'usage
    # Pour 'bt' : (322 * 100) / 1440 = 22.36
    assert coordinator.data["usage"]["bt"] == 22.36
    assert coordinator.data["usage"]["rate"] == 99.79


@pytest.mark.asyncio
async def test_coordinator_parses_energy_and_cop(hass, mock_api_for_coordinator):
    """Test du parsing des données d'énergie et du calcul du COP."""
    coordinator = VivrecoDataUpdateCoordinator(hass, update_interval=5)
    hass.data["hass_vivreco_pac"] = {"api": mock_api_for_coordinator}

    await coordinator._async_update_data()

    # Vérifier energyValues
    assert isinstance(coordinator.data["energy"], list)
    assert coordinator.data["energy"][0]["name"] == "ch"
    assert coordinator.data["energy"][0]["y"] == 7546.0

    # Vérifier COP (dernière valeur de tableValues.gene)
    assert coordinator.data["cop"]["d"] == 3.6
    assert coordinator.data["cop"]["m"] == 3.4


@pytest.mark.asyncio
async def test_coordinator_detects_features_from_settings(
    hass, mock_api_for_coordinator
):
    """Test de la détection des switches disponibles selon les settings."""
    coordinator = VivrecoDataUpdateCoordinator(hass, update_interval=5)
    hass.data["hass_vivreco_pac"] = {"api": mock_api_for_coordinator}

    await coordinator._async_update_data()

    # Vérifier la configuration détectée
    assert coordinator.data["config"]["ch"] is True
    assert coordinator.data["config"]["ecs"] is True
    assert coordinator.data["config"]["raf"] is False  # Car absent du mock settings


@pytest.mark.asyncio
async def test_coordinator_reconnects_if_token_missing(hass, mock_api_for_coordinator):
    """Test que le coordinateur déclenche login() si aucun token n'est présent."""
    coordinator = VivrecoDataUpdateCoordinator(hass, update_interval=5)

    # On force l'absence de token
    mock_api_for_coordinator.api_token = None
    mock_api_for_coordinator.hp_id = None

    hass.data["hass_vivreco_pac"] = {"api": mock_api_for_coordinator}

    await coordinator._async_update_data()

    # Vérifier que les méthodes de connexion ont été appelées
    mock_api_for_coordinator.login.assert_called_once()
    mock_api_for_coordinator.fetch_hp_id.assert_called_once()


@pytest.mark.asyncio
async def test_coordinator_handles_api_errors_gracefully(
    hass, mock_api_for_coordinator
):
    """Test que le coordinateur ne crash pas si l'API renvoie des données vides."""
    coordinator = VivrecoDataUpdateCoordinator(hass, update_interval=5)

    # Mock de TOUS les retours en vide
    mock_api_for_coordinator.get_chart_data.return_value = {}
    mock_api_for_coordinator.get_chart_data_since1h.return_value = {}  # Ajouté
    mock_api_for_coordinator.get_usage_data.return_value = {}  # Ajouté
    mock_api_for_coordinator.get_energy_data.return_value = {}
    mock_api_for_coordinator.get_settings_data.return_value = {}

    hass.data["hass_vivreco_pac"] = {"api": mock_api_for_coordinator}

    await coordinator._async_update_data()

    # Vérifier que les structures restent cohérentes ou vides
    assert coordinator.data["energy"] == []
    assert coordinator.data["cop"] == {}
    assert coordinator.data["usage"] == {}
    assert coordinator.data["humidity"] is None
