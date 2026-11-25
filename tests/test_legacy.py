"""Tests pour l'ancienne régulation Vivreco (type Comfile, écran bleu) — issue #8."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.hass_vivreco_pac.coordinator import (
    VivrecoDataUpdateCoordinator,
    is_legacy_energy_format,
    parse_duration_hours,
    parse_legacy_gene,
)
from custom_components.hass_vivreco_pac.sensor import (
    VivrecoCOPSensor,
    VivrecoConsumptionSensor,
    VivrecoLegacyCounterSensor,
    async_setup_entry,
)

# Réponse réelle d'energy_meters d'une ancienne régulation (issue #8)
LEGACY_ENERGY = {
    "values": {
        "time": 1770120894773,
        "values": {
            "tableValues": {
                "gene": [
                    {
                        "d": "2h16",
                        "d1": "3h53",
                        "m": "9h16",
                        "m1": "138h",
                        "total": "21388h16",
                        "w": "5h16",
                        "w1": "28h",
                        "y": "147h16",
                        "y1": "736h",
                    },
                    {
                        "d": 4.845,
                        "d1": 11.0,
                        "m": 27,
                        "m1": 373.0,
                        "total": 43658,
                        "w": 15,
                        "w1": 88.0,
                        "y": 400,
                        "y1": 1886.0,
                    },
                    {
                        "d": 2.583,
                        "d1": 1.0,
                        "m": 4,
                        "m1": 92.0,
                        "total": 12244,
                        "w": 4,
                        "w1": 3.0,
                        "y": 96,
                        "y1": 809.0,
                    },
                    {
                        "d": 7.0,
                        "d1": 6.0,
                        "m": 14.0,
                        "m1": 423.0,
                        "total": 62183.0,
                        "w": 6.0,
                        "w1": 64.0,
                        "y": 437.0,
                        "y1": 2115.0,
                    },
                ]
            }
        },
        "version": "c10:4816ea813c0f49d9a9f83909c3d26adeb1731a0b:4acc",
    }
}


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("21388h16", 21388.27),
        ("138h", 138.0),
        ("0h31", 0.52),
        ("0h", 0.0),
        (12, 12.0),
        (None, None),
        ("n/a", None),
    ],
)
def test_parse_duration_hours(raw, expected):
    """Conversion des durées "XhYY" en heures décimales."""
    assert parse_duration_hours(raw) == expected


def test_legacy_format_detection(mock_api_responses):
    """Ancien format détecté ; format récent (avec energyValues) non."""
    assert is_legacy_energy_format(LEGACY_ENERGY["values"]["values"]) is True
    assert (
        is_legacy_energy_format(mock_api_responses["energy"]["values"]["values"])
        is False
    )
    assert is_legacy_energy_format({}) is False


def test_parse_legacy_gene():
    """gene = [Durée, Conso HP, Conso HC, Démarrages]."""
    parsed = parse_legacy_gene(LEGACY_ENERGY["values"]["values"]["tableValues"]["gene"])
    assert parsed["duration"]["total"] == 21388.27
    assert parsed["energy_hp"]["total"] == 43658
    assert parsed["energy_hc"]["total"] == 12244
    assert parsed["energy_total"]["total"] == 55902
    assert parsed["energy_total"]["d"] == 7.428
    assert parsed["starts"]["total"] == 62183.0


@pytest.fixture
def legacy_api(mock_api_responses):
    """API mockée renvoyant le format d'energy_meters de l'ancienne régulation."""
    api = MagicMock()
    api.api_token = "test_token"
    api.hp_id = "test_hp_id"
    api.login = AsyncMock()
    api.fetch_hp_id = AsyncMock()
    api.get_chart_data = AsyncMock(return_value=mock_api_responses["chart"])
    api.get_chart_data_since1h = AsyncMock(return_value={})
    api.get_usage_data = AsyncMock(return_value={})
    api.get_energy_data = AsyncMock(return_value=LEGACY_ENERGY)
    api.get_settings_data = AsyncMock(return_value=mock_api_responses["settings"])
    return api


async def test_coordinator_legacy_has_no_cop(hass, legacy_api):
    """Le nombre de démarrages ne doit plus être pris pour le COP (issue #15)."""
    coordinator = VivrecoDataUpdateCoordinator(hass, update_interval=5)
    hass.data["hass_vivreco_pac"] = {"api": legacy_api}

    await coordinator._async_update_data()

    assert coordinator.data["legacy"] is True
    assert coordinator.data["cop"] == {}
    assert coordinator.data["legacy_energy"]["starts"]["total"] == 62183.0


async def test_coordinator_recent_format_unchanged(hass, mock_vivreco_api):
    """La régulation récente garde le COP en dernière ligne de gene."""
    coordinator = VivrecoDataUpdateCoordinator(hass, update_interval=5)
    hass.data["hass_vivreco_pac"] = {"api": mock_vivreco_api}

    await coordinator._async_update_data()

    assert coordinator.data["legacy"] is False
    assert coordinator.data["legacy_energy"] == {}
    assert coordinator.data["cop"]["m"] == 3.4


async def _setup_sensors(hass, api):
    coordinator = VivrecoDataUpdateCoordinator(hass, update_interval=5)
    hass.data["hass_vivreco_pac"] = {"api": api}
    await coordinator._async_update_data()
    entry = MagicMock()
    entry.entry_id = "test_entry"
    hass.data["hass_vivreco_pac"]["test_entry"] = coordinator
    added = []
    await async_setup_entry(hass, entry, added.extend)
    return added


async def test_legacy_sensors_created(hass, legacy_api):
    """Ancienne régulation : compteurs globaux, sans COP ni détail par usage."""
    sensors = await _setup_sensors(hass, legacy_api)

    legacy = {
        s.unique_id: s for s in sensors if isinstance(s, VivrecoLegacyCounterSensor)
    }
    assert set(legacy) == {
        "vivreco_energy_total",
        "vivreco_energy_hp",
        "vivreco_energy_hc",
        "vivreco_operating_time",
        "vivreco_compressor_starts",
    }
    assert not any(
        isinstance(s, (VivrecoCOPSensor, VivrecoConsumptionSensor)) for s in sensors
    )

    assert legacy["vivreco_energy_total"].native_value == 55902
    assert legacy["vivreco_operating_time"].native_value == 21388.27
    assert legacy["vivreco_compressor_starts"].native_value == 62183.0
    assert legacy["vivreco_energy_hp"].extra_state_attributes["mois"] == 27


async def test_recent_sensors_unchanged(hass, mock_vivreco_api):
    """Régulation récente : pas de compteur « ancienne régulation »."""
    sensors = await _setup_sensors(hass, mock_vivreco_api)

    assert not any(isinstance(s, VivrecoLegacyCounterSensor) for s in sensors)
    assert any(isinstance(s, VivrecoCOPSensor) for s in sensors)
