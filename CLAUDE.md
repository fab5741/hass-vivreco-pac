# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Vue d'ensemble du projet

Intégration Home Assistant pour les pompes à chaleur Vivreco. Cette intégration permet de superviser et contrôler les PAC Vivreco via leur API cloud (vivrecocontrol.com).

## Architecture

### Structure des composants

L'intégration suit l'architecture standard Home Assistant avec un pattern coordinator :

- **api.py** : Client API (`VivrecoApiClient`) gérant l'authentification Basic Auth et les appels REST vers l'API Vivreco
- **coordinator.py** : `VivrecoDataUpdateCoordinator` centralise la récupération des données (chart, energy, settings) avec rafraîchissement périodique
- **Entités platformes** : Chaque plateforme (climate, sensor, binary_sensor, switch, number, select, water_heater) hérite de `VivrecoBaseEntity`

### Flux de données

1. **Authentification** : Login avec Basic Auth → récupération token Bearer → récupération hp_id
2. **Coordinateur** : Appels périodiques vers 3 endpoints (chart, energy, settings) fusionnés dans `coordinator.data`
3. **Entités** : Lisent `coordinator.data` et envoient des commandes via `coordinator.api.send_command()`

### Points clés

- Les fonctionnalités disponibles sont détectées dynamiquement dans `coordinator.data["config"]` en vérifiant la présence des clés dans settings (ch, raf, ecs, app_elec)
- Les entités ne sont créées que si la fonctionnalité est supportée par la PAC
- La version des settings est automatiquement récupérée et incluse dans les commandes pour éviter les conflits

## Commandes de développement

### Validation

```bash
# Validation HACS (GitHub Action)
# Voir .github/workflows/validate.yml

# Validation hassfest (GitHub Action)
# Voir .github/workflows/hassfest.yaml
```

### Test manuel

```bash
# Installation dans Home Assistant
cp -r custom_components/hass_vivreco_pac /path/to/homeassistant/custom_components/

# Redémarrer Home Assistant pour charger l'intégration
```

## API Vivreco

### Endpoints utilisés

- **Login** : `POST /api/v1/herja/login` (Basic Auth)
- **User info** : `GET /api/v1/herja/user/me` (récupère hp_id)
- **Chart data** : `GET /api/v1/charts/{hp_id}/dashboard` (températures, états)
- **Energy data** : `GET /api/v1/commands/{hp_id}/values/energy_meters` (consommation)
- **Settings** : `GET /api/v1/commands/{hp_id}/values/customer_settings` (configuration, version)
- **Command** : `POST /api/v1/commands/{hp_id}/command` (envoi de commandes)

### Format des commandes

```python
{
    "group": "customer_settings",
    "values": {
        "auth_p/etat_glob/aut_ch": True,
        "mode_zone_p/ambiance": "confort"
    },
    "version": "1.2.3"  # Version récupérée depuis settings
}
```

## Constantes importantes

- **SENSORS** : Définit les capteurs de température avec leurs dépendances (requires: "ch", "ecs", etc.)
- **MODE** : Mapping des clés API vers les modes de fonctionnement (mode_ch, mode_ecs, etc.)
- **CHAUFFAGE_SETPOINTS** : Consignes de température pour chaque preset (confort, normal, réduit, hg)
- **ECS_SETPOINTS** : Consignes pour l'eau chaude sanitaire
- **MODE_AMBIANCE_ZONE_PRINCIPALE** : Presets disponibles pour le chauffage
- **MODE_AMBIANCE_ECS** : Presets disponibles pour l'ECS

## Traductions

Les fichiers de traduction se trouvent dans `custom_components/hass_vivreco_pac/translations/` :
- fr.json (français)
- en.json (anglais)

Utiliser `translation_key` dans les entités pour référencer les traductions.

## Platformes disponibles

1. **climate** : Contrôle chauffage/rafraîchissement avec presets
2. **water_heater** : Contrôle du ballon d'eau chaude
3. **sensor** : Températures (t_ext, t_int, t_ecs, consignes)
4. **binary_sensor** : États on/off (compresseur, modes actifs)
5. **switch** : Activation/désactivation des modes (ch, raf, ecs, app_elec)
6. **number** : Réglage des consignes de température
7. **select** : Sélection des presets (ambiance zone principale, mode ECS)
