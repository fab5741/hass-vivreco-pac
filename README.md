# Intégration Vivreco Pompe à chaleur pour Home Assistant

[![GitHub release](https://img.shields.io/github/v/release/fab5741/hass-vivreco-pac.svg?include_prereleases=&sort=semver&color=blue)](https://github.com/fab5741/hass-vivreco-pac/releases/)
[![Tests](https://github.com/fab5741/hass-vivreco-pac/workflows/Tests/badge.svg)](https://github.com/fab5741/hass-vivreco-pac/actions/workflows/tests.yml)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![HACS validation](https://github.com/fab5741/hass-vivreco-pac/workflows/HACS%20validation/badge.svg)](https://github.com/fab5741/hass-vivreco-pac/actions)
[![Validate with hassfest](https://github.com/fab5741/hass-vivreco-pac/workflows/Validate%20with%20hassfest/badge.svg)](https://github.com/fab5741/hass-vivreco-pac/actions)

Intégration non officielle pour [Home Assistant][home-assistant] permettant de connecter et superviser les pompes à chaleur [Vivreco][vivreco].
Cette intégration récupère les données de fonctionnement et de température via l'API officielle de [Vivreco][vivreco].

## ✨ Fonctionnalités

### Capteurs de température
- 🌡️ Température extérieure
- 🏠 Température intérieure
- 🚿 Température eau chaude sanitaire (ECS)
- 📊 Consignes de température (chauffage et ECS)

### Capteurs d'énergie et performance
- ⚡ Consommation énergétique (chauffage, ECS, rafraîchissement, autre)
- ⏱️ Durées de fonctionnement cumulées
- 📈 **COP (Coefficient de Performance)** avec historique
  - Mesure l'efficacité énergétique de votre PAC
  - Historique par jour, semaine, mois, année

### Contrôles
- ⚙️ Entité **Climate** pour chauffage/rafraîchissement
- 🚿 Entité **Water Heater** pour ballon ECS
- 🔘 **Switches** pour activer/désactiver modes (ch, raf, ecs, appoint électrique)
- 🎚️ **Numbers** pour régler les consignes de température
- 📋 **Selects** pour choisir les modes (ambiance, ECS)

### États
- 🔄 État du compresseur
- 📊 Mode de fonctionnement actif
- ⚠️ Binary sensors pour états on/off

## 📦 Installation

### Via HACS (recommandé)

1. Ouvrez **HACS** dans votre interface Home Assistant
2. Ajoutez ce dépôt comme **dépôt personnalisé** :
   - **URL** : `https://github.com/fab5741/hass-vivreco-pac`
   - **Type** : Integration
3. Recherchez puis installez **Vivreco PAC**
4. Redémarrez Home Assistant

### Installation manuelle

1. Téléchargez la [dernière release](https://github.com/fab5741/hass-vivreco-pac/releases/latest)
2. Copiez le dossier `custom_components/hass_vivreco_pac` dans votre dossier `custom_components/`
3. Redémarrez Home Assistant

## ⚙️ Configuration

1. Allez dans **Configuration** > **Intégrations**
2. Cliquez sur **Ajouter une intégration**
3. Recherchez **Vivreco PAC**
4. Entrez vos identifiants Vivreco WebControl :
   - Email
   - Mot de passe
   - Fréquence de mise à jour (5 minutes par défaut)

L'intégration valide vos identifiants avant de créer l'entrée.

### Modifier les paramètres

Vous pouvez modifier la fréquence de mise à jour après installation :
1. **Configuration** > **Intégrations** > **Vivreco PAC**
2. Cliquez sur **Configurer**
3. Ajustez l'intervalle de mise à jour

## 📊 Exemples d'utilisation

### Carte Climate (Thermostat)

```yaml
type: thermostat
entity: climate.vivreco_pac_climatisation
```

### Carte Water Heater (ECS)

```yaml
type: thermostat
entity: water_heater.vivreco_pac_ecs
```

### Carte énergie avec COP

```yaml
type: entities
entities:
  - entity: sensor.vivreco_pac_chauffage
    name: Consommation chauffage
  - entity: sensor.vivreco_pac_ch_duration
    name: Durée fonctionnement
  - entity: sensor.vivreco_pac_cop_coefficient_de_performance
    name: COP (efficacité)
```

### Dashboard personnalisé

```yaml
type: vertical-stack
cards:
  - type: entities
    title: Températures
    entities:
      - entity: sensor.vivreco_pac_temperature_exterieure
      - entity: sensor.vivreco_pac_temperature_interieure
      - entity: sensor.vivreco_pac_temperature_ecs

  - type: entities
    title: Contrôles
    entities:
      - entity: switch.vivreco_pac_mode_chauffage
      - entity: switch.vivreco_pac_mode_ecs
      - entity: select.vivreco_pac_mode_zone_principale

  - type: entities
    title: Performance
    entities:
      - entity: sensor.vivreco_pac_cop_coefficient_de_performance
      - entity: sensor.vivreco_pac_ch_duration
      - entity: sensor.vivreco_pac_chauffage
```

## 🔧 Développement

Ce projet utilise des outils modernes pour garantir la qualité du code :

### Qualité et tests ✅
- **26 tests unitaires** avec pytest (API, Coordinateur, Config Flow)
- **GitHub Actions** pour CI/CD (tests automatiques sur Python 3.11 & 3.12)
- **Pre-commit hooks** pour validation automatique du code
- **Linting** avec Ruff, Black, et isort
- **Type hints** complets pour une meilleure maintenabilité

### Prérequis
```bash
pip install -r requirements_test.txt
pip install pre-commit black ruff isort
```

### Tests
```bash
# Lancer tous les tests
pytest

# Tests avec couverture
pytest --cov=custom_components.hass_vivreco_pac --cov-report=html

# Tests spécifiques
pytest tests/test_api.py -v
```

### Pre-commit hooks
```bash
pre-commit install
pre-commit run --all-files
```

### Structure du projet
```
custom_components/hass_vivreco_pac/
├── __init__.py          # Initialisation de l'intégration
├── api.py               # Client API Vivreco
├── coordinator.py       # Coordinateur de données
├── config_flow.py       # Flux de configuration
├── const.py             # Constantes
├── entity.py            # Classe de base des entités
├── binary_sensor.py     # Capteurs binaires
├── climate.py           # Entité Climate
├── number.py            # Entités Number
├── select.py            # Entités Select
├── sensor.py            # Capteurs
├── switch.py            # Switches
└── water_heater.py      # Entité Water Heater
```

## 📝 Changelog

Voir [CHANGELOG.md](CHANGELOG.md) pour l'historique complet des versions.

## 🤝 Contribuer

Les contributions sont les bienvenues ! Voir [CONTRIBUTING.md](CONTRIBUTING.md) pour les guidelines.

## 🐛 Signaler un bug

Si vous rencontrez un problème :
1. Vérifiez vos identifiants Vivreco WebControl
2. Consultez les [issues existantes](https://github.com/fab5741/hass-vivreco-pac/issues)
3. Créez une nouvelle issue avec :
   - Version de Home Assistant
   - Version de l'intégration
   - Logs détaillés

## ⚖️ License

Ce projet est distribué sous la licence MIT. Consultez le fichier [LICENSE](LICENSE) pour plus d'informations.

## ⚠️ Avertissement

Ce projet est **non officiel** et n'est pas affilié à [Vivreco][vivreco].
Les données dépendent de l'API officielle et peuvent changer si celle-ci évolue.
Utilisez cette intégration à vos propres risques.

---

**⭐ Si cette intégration vous est utile, n'hésitez pas à mettre une étoile au projet !**

<!-- Links -->
[home-assistant]: https://www.home-assistant.io/
[vivreco]: https://www.vivreco.fr/
