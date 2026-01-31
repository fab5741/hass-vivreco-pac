# Guide de contribution

Merci de votre intérêt pour contribuer à l'intégration Vivreco PAC pour Home Assistant ! 🎉

## 📋 Table des matières

- [Code de conduite](#code-de-conduite)
- [Comment contribuer](#comment-contribuer)
- [Environnement de développement](#environnement-de-développement)
- [Standards de code](#standards-de-code)
- [Tests](#tests)
- [Pull Requests](#pull-requests)

## 🤝 Code de conduite

Ce projet adhère au code de conduite de la communauté Home Assistant. En participant, vous vous engagez à respecter ce code.

## 💡 Comment contribuer

### Signaler un bug

1. Vérifiez que le bug n'a pas déjà été signalé dans les [issues](https://github.com/fab5741/hass-vivreco-pac/issues)
2. Créez une nouvelle issue en utilisant le template
3. Incluez :
   - Version de Home Assistant
   - Version de l'intégration
   - Description détaillée du problème
   - Logs pertinents (activez le mode debug si nécessaire)
   - Étapes pour reproduire

### Proposer une fonctionnalité

1. Ouvrez une issue pour discuter de la fonctionnalité
2. Expliquez le cas d'usage et les bénéfices
3. Attendez les retours avant de commencer le développement

### Contribuer du code

1. Forkez le dépôt
2. Créez une branche depuis `main` : `git checkout -b feature/ma-fonctionnalite`
3. Effectuez vos modifications
4. Ajoutez des tests
5. Assurez-vous que tous les tests passent
6. Committez avec des messages clairs
7. Poussez vers votre fork
8. Ouvrez une Pull Request

## 🛠️ Environnement de développement

### Prérequis

- Python 3.11 ou supérieur
- Home Assistant (pour tester l'intégration)
- Git

### Installation

```bash
# Cloner le dépôt
git clone https://github.com/fab5741/hass-vivreco-pac.git
cd hass-vivreco-pac

# Installer les dépendances de développement
pip install -r requirements_test.txt
pip install pre-commit black ruff isort

# Installer les hooks pre-commit
pre-commit install
```

### Lancer les tests

```bash
# Tous les tests
pytest

# Tests spécifiques
pytest tests/test_api.py -v

# Avec couverture
pytest --cov=custom_components.hass_vivreco_pac --cov-report=html
```

### Validation du code

```bash
# Lancer tous les hooks pre-commit
pre-commit run --all-files

# Formatage avec black
black custom_components/

# Linting avec ruff
ruff check custom_components/

# Tri des imports
isort custom_components/
```

## 📏 Standards de code

### Style

- Suivre [PEP 8](https://pep8.org/)
- Utiliser **Black** pour le formatage (line-length=88)
- Utiliser **isort** pour trier les imports (profil black)
- Passer la validation **ruff**

### Type hints

- Ajouter des type hints pour toutes les fonctions publiques
- Utiliser les types modernes (e.g., `list[str]` au lieu de `List[str]`)

```python
def my_function(param: str) -> bool:
    """Docstring."""
    return True
```

### Docstrings

- Toutes les fonctions publiques doivent avoir une docstring
- Format Google ou NumPy

```python
def get_data(self, device_id: str) -> dict:
    """Récupère les données d'un appareil.

    Args:
        device_id: Identifiant de l'appareil

    Returns:
        Dictionnaire contenant les données de l'appareil
    """
    pass
```

### Nommage

- Classes : `PascalCase`
- Fonctions/méthodes : `snake_case`
- Constantes : `UPPER_SNAKE_CASE`
- Privé : préfixer avec `_`

## 🧪 Tests

### Écrire des tests

- Un test par fonctionnalité
- Utiliser des noms de tests descriptifs
- Mocker les appels API
- Couvrir les cas d'erreur

```python
@pytest.mark.asyncio
async def test_login_success(mock_session, mock_response):
    """Test de connexion réussie."""
    api = VivrecoApiClient("email", "password", mock_session)
    # ... test
```

### Couverture

- Viser une couverture > 80%
- Tous les nouveaux fichiers doivent être testés
- Les corrections de bugs doivent inclure un test de régression

## 📝 Pull Requests

### Avant de soumettre

- [ ] Les tests passent (`pytest`)
- [ ] Le linting passe (`ruff check`)
- [ ] Le formatage est correct (`black --check`)
- [ ] Les imports sont triés (`isort --check`)
- [ ] La couverture n'a pas diminué
- [ ] La documentation est à jour (README, CHANGELOG)

### Message de commit

Suivre [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description courte

Description plus détaillée si nécessaire

Fixes #123
```

Types : `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### Description de la PR

- Expliquer **pourquoi** ce changement est nécessaire
- Décrire **comment** le changement résout le problème
- Mentionner les issues liées (`Fixes #123`)
- Ajouter des captures d'écran si pertinent

### Review

- Soyez patient, les reviews prennent du temps
- Répondez aux commentaires de manière constructive
- Effectuez les modifications demandées

## 🔄 Workflow

1. **Issue** : Discussion de la fonctionnalité/bug
2. **Branch** : Créer une branche depuis `main`
3. **Develop** : Coder + tests + documentation
4. **PR** : Ouvrir une pull request
5. **Review** : Répondre aux commentaires
6. **Merge** : Fusion dans `main`
7. **Release** : Publication d'une nouvelle version

## 📚 Ressources

- [Documentation Home Assistant](https://developers.home-assistant.io/)
- [API Vivreco](https://vivrecocontrol.com)
- [Tests Home Assistant](https://developers.home-assistant.io/docs/development_testing)

## ❓ Questions

Si vous avez des questions, n'hésitez pas à :
- Ouvrir une issue
- Consulter les issues existantes
- Contacter les mainteneurs

---

**Merci pour vos contributions ! 🙏**
