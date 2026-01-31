# Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

## [2.0.0] - 2026-01-31

### 🎉 Release majeure - Refactor complet "AI-Ready"

Cette version marque un refactor complet du plugin avec des standards professionnels,
une documentation exhaustive, et des outils modernes pour le développement.

### Ajouté

**Fonctionnalités:**
- Capteur COP (Coefficient de Performance) avec historique par période
- 4 capteurs de durée de fonctionnement (chauffage, ECS, rafraîchissement, autre)
- Validation des credentials lors de la configuration initiale
- Options Flow pour modifier les paramètres après installation
- Session aiohttp réutilisable (bonnes pratiques Home Assistant)

**Tests & Qualité:**
- 26 tests unitaires (API, Coordinateur, Config Flow)
- GitHub Actions pour tests automatiques (Python 3.11 & 3.12)
- GitHub Actions pour linting (Ruff, Black, isort)
- Pre-commit hooks pour validation automatique du code
- Configuration pytest centralisée dans pyproject.toml
- Couverture de code avec Codecov

**Documentation:**
- CHANGELOG.md complet avec historique des versions
- README.md enrichi avec badges, exemples Lovelace, guide développement
- CONTRIBUTING.md avec guide complet pour contributeurs
- CLAUDE.md pour développement assisté par IA
- Templates GitHub (Bug Report, Feature Request, Pull Request)
- Documentation de la structure du projet

**Configuration:**
- pyproject.toml pour Black, Ruff, isort, pytest
- .pre-commit-config.yaml avec hooks de validation
- requirements_test.txt avec dépendances de test

### Changé
- Amélioration majeure de la gestion d'erreurs (aiohttp.ClientError)
- Détection automatique des tokens expirés (HTTP 401)
- Logs optimisés (formatage %s au lieu de f-strings)
- Type hints complets sur switch.py et select.py

### Corrigé
- Issue #8: Parsing des capteurs d'énergie (tableau au lieu de dictionnaire)
- Bug ligne dupliquée dans VivrecoEcsConsignesNumber
- Valeurs par défaut config.get() (False au lieu de True)

### Infrastructure
- CI/CD complet avec 3 workflows GitHub Actions
- Standards de code appliqués (PEP 8, Black, Ruff)
- Documentation complète pour contributeurs
- Templates standardisés pour issues et PR

**Migration depuis 1.x:**
Aucune action requise. La migration est transparente.
Tous les capteurs existants continueront de fonctionner.
Les nouveaux capteurs (COP, durées) seront ajoutés automatiquement.

## [1.10] - 2026-01-31

### Ajouté
- Suite complète de 26 tests unitaires (API, Coordinateur, Config Flow)
- Fixtures pour mocker les réponses API
- Configuration pytest
- Documentation des tests dans tests/README.md

## [1.9] - 2026-01-31

### Ajouté
- Capteur COP (Coefficient de Performance) montrant l'efficacité de la PAC
- Attributs par période (jour, semaine, mois, année) pour le COP
- Device class POWER_FACTOR pour le capteur COP

### Changé
- Bump version manifest 1.8 → 1.9

## [1.8] - 2026-01-31

### Ajouté
- Options Flow permettant de modifier scan_interval sans reconfigurer
- Interface UI pour modifier les paramètres de l'intégration
- Traductions FR/EN pour le flux d'options

## [1.7] - 2026-01-31

### Corrigé
- Suppression de ligne dupliquée dans VivrecoEcsConsignesNumber (has_entity_name)

### Ajouté
- Validation des credentials lors de la configuration initiale
- Tentative de connexion API avant création de l'entrée
- Message d'erreur clair si identifiants invalides
- Traductions du message d'erreur (FR/EN)

## [1.6] - 2026-01-31

### Ajouté
- 4 nouveaux capteurs de durée de fonctionnement (ch, ecs, raf, other)
- Device class DURATION avec unité HOURS
- State class TOTAL_INCREASING pour cumul
- Récupération des timeValues depuis l'API

### Changé
- Utilisation d'une session aiohttp réutilisable (bonnes pratiques Home Assistant)
- Amélioration de la gestion d'erreurs (aiohttp.ClientError au lieu de Exception)
- Détection automatique des tokens expirés (code 401)
- Correction des logs (remplacement f-strings par formatage %s)

### Corrigé
- **Issue #8** : Capteurs d'énergie retournant N/A
  - Correction du parsing energyValues.total (tableau au lieu de dictionnaire)
  - Ajout de vérifications de type pour energy_data
  - Retour de None au lieu de "N/A" pour valeurs manquantes
  - Correction config.get() avec False par défaut

### Documentation
- Ajout de CLAUDE.md pour guider le développement avec Claude Code
- Documentation de l'architecture et des patterns
- Documentation des endpoints API

## [1.5 et antérieurs]

### Fonctionnalités existantes
- Intégration Home Assistant pour PAC Vivreco
- Entité Climate pour chauffage/rafraîchissement
- Entité Water Heater pour ballon ECS
- Capteurs de température (extérieure, intérieure, ECS)
- Binary sensors pour états (compresseur, modes)
- Switches pour activer/désactiver modes
- Numbers pour régler consignes de température
- Selects pour choisir modes (ambiance, ECS)
- Configuration via UI avec scan_interval personnalisable
- Support HACS
- Traductions FR/EN

---

## Types de changements

- `Ajouté` pour les nouvelles fonctionnalités
- `Changé` pour les modifications de fonctionnalités existantes
- `Déprécié` pour les fonctionnalités bientôt supprimées
- `Supprimé` pour les fonctionnalités supprimées
- `Corrigé` pour les corrections de bugs
- `Sécurité` pour les failles de sécurité
