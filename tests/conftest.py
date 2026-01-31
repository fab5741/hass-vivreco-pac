"""Fixtures communes pour les tests."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.core import HomeAssistant


class AsyncContextManagerMock:
    """Mock pour un context manager asynchrone (utilisé pour aiohttp responses)."""

    def __init__(self, return_value):
        """Initialise le context manager mock."""
        self.return_value = return_value

    async def __aenter__(self):
        """Entrée du context manager."""
        return self.return_value

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Sortie du context manager."""
        return None


@pytest.fixture
async def hass():
    """Fixture Home Assistant."""
    hass_instance = HomeAssistant("/tmp/hass-test")
    hass_instance.data = {}
    await hass_instance.async_start()
    yield hass_instance
    await hass_instance.async_stop()


@pytest.fixture
def mock_aiohttp_session():
    """Mock de la session aiohttp."""
    session = MagicMock()
    return session


@pytest.fixture
def mock_api_responses():
    """Réponses mockées de l'API Vivreco."""
    return {
        "login": {"token": "test_token_123"},
        "user": {"hp_id": ["test_hp_id_456"]},
        "chart": {
            "elements": {
                "values": {
                    "t_ext": 5.2,
                    "t_int": 21.5,
                    "t_ecs": 55.0,
                    "state": "bt",
                },
                "labels": {},
            }
        },
        "energy": {
            "values": {
                "values": {
                    "energyValues": {
                        "total": [
                            {"name": "ch", "y": 7546.0},
                            {"name": "ecs", "y": 651.0},
                            {"name": "other", "y": 308.0},
                        ]
                    },
                    "timeValues": {
                        "total": [
                            {"name": "ch", "y": 2185.0},
                            {"name": "ecs", "y": 69.0},
                            {"name": "other", "y": 80.0},
                        ]
                    },
                    "tableValues": {
                        "gene": [
                            {"d": "6h49", "total": "2334h"},
                            {"d": 24.0, "total": 8505.0},
                            {"d": 3.6, "m": 3.4, "y": 3.4, "total": None},
                        ]
                    },
                }
            }
        },
        "settings": {
            "values": {
                "version": "v180:test",
                "values": {
                    "auth_p/etat_glob/aut_ch": True,
                    "auth_p/etat_glob/aut_ecs": True,
                    "mode_zone_p/ambiance": "normal",
                    "consigne_p/t_normal_ch": 20.0,
                    "consigne_ecs/t_normal_ecs": 50.0,
                },
            }
        },
    }


@pytest.fixture
def mock_response():
    """Mock d'une réponse HTTP."""

    def _mock_response(status=200, json_data=None):
        response = MagicMock()
        response.status = status
        response.json = AsyncMock(return_value=json_data or {})
        return AsyncContextManagerMock(response)

    return _mock_response
