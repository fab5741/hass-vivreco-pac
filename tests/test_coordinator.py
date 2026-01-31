"""Tests pour le coordinateur Vivreco."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.hass_vivreco_pac.coordinator import (
    VivrecoDataUpdateCoordinator,
)


@pytest.mark.asyncio
async def test_coordinator_initialization(hass):
    """Test de l'initialisation du coordinateur."""
    coordinator = VivrecoDataUpdateCoordinator(hass, update_interval=5)

    assert coordinator.name == "Vivreco PAC"
    assert "values" in coordinator.data
    assert "energy" in coordinator.data
    assert "time_values" in coordinator.data
    assert "cop" in coordinator.data
    assert "settings" in coordinator.data
    assert "config" in coordinator.data


@pytest.mark.asyncio
async def test_coordinator_update_data(hass, mock_api_responses):
    """Test de mise à jour des données."""
    coordinator = VivrecoDataUpdateCoordinator(hass, update_interval=5)

    # Mock de l'API
    mock_api = MagicMock()
    mock_api.api_token = "test_token"
    mock_api.hp_id = "test_hp_id"
    mock_api.login = AsyncMock()
    mock_api.fetch_hp_id = AsyncMock()
    mock_api.get_chart_data = AsyncMock(return_value=mock_api_responses["chart"])
    mock_api.get_energy_data = AsyncMock(return_value=mock_api_responses["energy"])
    mock_api.get_settings_data = AsyncMock(return_value=mock_api_responses["settings"])

    # Injecter l'API mockée
    hass.data["hass_vivreco_pac"] = {"api": mock_api}

    # Mettre à jour les données
    await coordinator._async_update_data()

    # Vérifier que les données ont été mises à jour
    assert coordinator.data["values"]["t_ext"] == 5.2
    assert coordinator.data["values"]["t_int"] == 21.5
    assert len(coordinator.data["energy"]) == 3
    assert coordinator.data["energy"][0]["name"] == "ch"
    assert coordinator.data["energy"][0]["y"] == 7546.0


@pytest.mark.asyncio
async def test_coordinator_parses_energy_data_correctly(hass, mock_api_responses):
    """Test du parsing correct des données d'énergie."""
    coordinator = VivrecoDataUpdateCoordinator(hass, update_interval=5)

    mock_api = MagicMock()
    mock_api.api_token = "test_token"
    mock_api.hp_id = "test_hp_id"
    mock_api.login = AsyncMock()
    mock_api.fetch_hp_id = AsyncMock()
    mock_api.get_chart_data = AsyncMock(return_value=mock_api_responses["chart"])
    mock_api.get_energy_data = AsyncMock(return_value=mock_api_responses["energy"])
    mock_api.get_settings_data = AsyncMock(return_value=mock_api_responses["settings"])

    hass.data["hass_vivreco_pac"] = {"api": mock_api}

    await coordinator._async_update_data()

    # Vérifier energyValues
    assert isinstance(coordinator.data["energy"], list)
    assert coordinator.data["energy"][0] == {"name": "ch", "y": 7546.0}
    assert coordinator.data["energy"][1] == {"name": "ecs", "y": 651.0}

    # Vérifier timeValues
    assert isinstance(coordinator.data["time_values"], list)
    assert coordinator.data["time_values"][0] == {"name": "ch", "y": 2185.0}

    # Vérifier COP
    assert isinstance(coordinator.data["cop"], dict)
    assert coordinator.data["cop"]["d"] == 3.6
    assert coordinator.data["cop"]["m"] == 3.4


@pytest.mark.asyncio
async def test_coordinator_detects_config_features(hass, mock_api_responses):
    """Test de la détection des fonctionnalités disponibles."""
    coordinator = VivrecoDataUpdateCoordinator(hass, update_interval=5)

    mock_api = MagicMock()
    mock_api.api_token = "test_token"
    mock_api.hp_id = "test_hp_id"
    mock_api.login = AsyncMock()
    mock_api.fetch_hp_id = AsyncMock()
    mock_api.get_chart_data = AsyncMock(return_value=mock_api_responses["chart"])
    mock_api.get_energy_data = AsyncMock(return_value=mock_api_responses["energy"])
    mock_api.get_settings_data = AsyncMock(return_value=mock_api_responses["settings"])

    hass.data["hass_vivreco_pac"] = {"api": mock_api}

    await coordinator._async_update_data()

    # Vérifier la configuration détectée
    assert coordinator.data["config"]["ch"] is True
    assert coordinator.data["config"]["ecs"] is True
    assert coordinator.data["config"]["raf"] is False


@pytest.mark.asyncio
async def test_coordinator_handles_missing_token(hass, mock_api_responses):
    """Test que le coordinateur se connecte si le token est manquant."""
    coordinator = VivrecoDataUpdateCoordinator(hass, update_interval=5)

    mock_api = MagicMock()
    mock_api.api_token = None  # Pas de token
    mock_api.hp_id = None  # Pas d'ID
    mock_api.login = AsyncMock()
    mock_api.fetch_hp_id = AsyncMock()
    mock_api.get_chart_data = AsyncMock(return_value=mock_api_responses["chart"])
    mock_api.get_energy_data = AsyncMock(return_value=mock_api_responses["energy"])
    mock_api.get_settings_data = AsyncMock(return_value=mock_api_responses["settings"])

    hass.data["hass_vivreco_pac"] = {"api": mock_api}

    await coordinator._async_update_data()

    # Vérifier que login et fetch_hp_id ont été appelés
    mock_api.login.assert_called_once()
    mock_api.fetch_hp_id.assert_called_once()


@pytest.mark.asyncio
async def test_coordinator_handles_empty_energy_data(hass):
    """Test que le coordinateur gère les données d'énergie vides."""
    coordinator = VivrecoDataUpdateCoordinator(hass, update_interval=5)

    mock_api = MagicMock()
    mock_api.api_token = "test_token"
    mock_api.hp_id = "test_hp_id"
    mock_api.login = AsyncMock()
    mock_api.fetch_hp_id = AsyncMock()
    mock_api.get_chart_data = AsyncMock(return_value={"elements": {"values": {}}})
    mock_api.get_energy_data = AsyncMock(return_value={})  # Données vides
    mock_api.get_settings_data = AsyncMock(
        return_value={"values": {"values": {}}}
    )

    hass.data["hass_vivreco_pac"] = {"api": mock_api}

    await coordinator._async_update_data()

    # Vérifier que les données par défaut sont des listes vides
    assert coordinator.data["energy"] == []
    assert coordinator.data["time_values"] == []
    assert coordinator.data["cop"] == {}
