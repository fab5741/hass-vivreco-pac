# Integration Vivreco Pompe à chaleur pour Home Assistant

[![GitHub release](https://img.shields.io/github/v/release/fab5741/hass-vivreco-pac.svg?include_prereleases=&sort=semver&color=blue)](https://github.com/fab5741/hass-vivreco-pac/releases/)
[![GH-code-size](https://img.shields.io/github/languages/code-size/fab5741/hass-vivreco-pac?color=red)](https://github.com/fab5741/hass-vivreco-pac)
[![issues](https://img.shields.io/github/issues/fab5741/hass-vivreco-pac)](https://github.com/fab5741/hass-vivreco-pac/issues)
[![GH-last-commit](https://img.shields.io/github/last-commit/fab5741/hass-vivreco-pac?style=flat-square)](https://github.com/fab5741/hass-vivreco-pac/commits/main)

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![HACS validation](https://github.com/fab5741/hass-vivreco-pac/workflows/HACS%20validation/badge.svg)](https://github.com/fab5741/hass-vivreco-pac/actions?query=workflow:"HACS+validation")
[![Validate with hassfest](https://github.com/fab5741/hass-vivreco-pac/workflows/Validate%20with%20hassfest/badge.svg)](https://github.com/fab5741/hass-vivreco-pac/actions?query=workflow:"Validate+with+hassfest")

Intégration non officielle pour [Home Assistant][home-assistant] permettant de connecter et de superviser les pompes à chaleur [Vivreco][vivreco]. Cette intégration récupère les données de fonctionnement et de température via l'API officielle de [Vivreco][vivreco].

---

## Fonctionnalités
- Suivi en temps réel des données de votre pompe à chaleur.
- Capteurs pour la température, l'état du compresseur, et d'autres valeurs clés.
- Configuration simple et intervalle de mise à jour personnalisable.

---

## Installation

### Manuelle

1. Clonez ce dépôt dans le dossier `custom_components` de votre installation Home Assistant.
   ```bash
   git clone https://github.com/votre-utilisateur/hass-vivreco-pac.git custom_components/hass-vivreco-pac
2. Redémarrez Home Assistant pour détecter l'intégration.

### HACS

- Installation avec "Dépôts personnalisés / custom repository" via HACS :
   - Dépôt : https://github.com/fab5741/hass-vivreco-pac
   - Type : Integration

### 
---

## Exemple de capteurs disponibles
Une fois l'intégration configurée, voici quelques capteurs que vous pourrez voir apparaître :

- Température extérieure (t_ext)
- Température intérieure (t_int)
- Température de l'eau chaude sanitaire (t_ecs)
- Consigne de température (cons_t_int, cons_t_ecs)
- État de fonctionnement (state)

## Remarques importantes
- Ce projet est non officiel et n'est pas affilié à [Vivreco][vivreco].
- Les données récupérées dépendent de l'API officielle et peuvent changer si celle-ci évolue.
- Utilisez cette intégration à vos propres risques.

## Contribuer
Les contributions sont les bienvenues ! Pour signaler un problème ou proposer une amélioration, ouvrez une issue.
Pour l'intant on ne récupère que les informations de base, mais on pourrai aller plus loin en fouillant un peu l'API, n'hésitez pas à créer une pull request.

## Dépannage
Si vous rencontrez des problèmes de connexion, vérifiez vos identifiants [Vivreco][vivreco].
Si les mises à jour ne se produisent pas, assurez-vous que l'intervalle de mise à jour est correct et que l'intégration est activée dans Home Assistant.    

## License

Ce projet est distribué sous la licence MIT. Consultez le fichier LICENSE pour plus d'informations.

<!-- Badges -->

[hacs-url]: https://github.com/hacs/integration
[hacs-badge]: https://img.shields.io/badge/hacs-default-orange.svg?style=flat-square
[release-badge]: https://img.shields.io/github/v/release/fab5741/hass-vivreco-pac?style=flat-square
[downloads-badge]: https://img.shields.io/github/downloads/fab5741/hass-vivreco-pac/total?style=flat-square
[build-badge]: https://img.shields.io/github/actions/workflow/status/fab5741/hass-vivreco-pac/build.yml?branch=main&style=flat-square

<!-- Links -->
[home-assistant]: https://www.home-assistant.io/
[vivreco]: https://www.vivreco.fr/