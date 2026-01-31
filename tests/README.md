# Tests Vivreco PAC

Tests unitaires pour l'intégration Home Assistant Vivreco PAC.

## Installation des dépendances

```bash
pip install -r requirements_test.txt
```

## Lancer les tests

### Tous les tests
```bash
pytest
```

### Tests spécifiques
```bash
# Tests de l'API
pytest tests/test_api.py

# Tests du coordinateur
pytest tests/test_coordinator.py

# Tests du config flow
pytest tests/test_config_flow.py
```

### Avec couverture
```bash
pytest --cov=custom_components.hass_vivreco_pac --cov-report=html
```

### Mode verbose
```bash
pytest -v
```

## Structure des tests

- `conftest.py` : Fixtures communes (hass, mocks API, etc.)
- `test_api.py` : Tests du client API (login, fetch_hp_id, get_data, send_command)
- `test_coordinator.py` : Tests du coordinateur (update_data, parsing, config detection)
- `test_config_flow.py` : Tests du flux de configuration et d'options

## Coverage

Les tests couvrent :
- ✅ Client API (login, erreurs réseau, 401, commandes)
- ✅ Coordinateur (parsing des données, détection config, gestion erreurs)
- ✅ Config flow (validation credentials, options flow)
- ✅ Gestion des erreurs et cas limites
