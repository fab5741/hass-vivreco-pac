# Intégration Vivreco Pompe à chaleur pour Home Assistant

[![GitHub release](https://img.shields.io/github/v/release/fab5741/hass-vivreco-pac.svg?include_prereleases=&sort=semver&color=blue)](https://github.com/fab5741/hass-vivreco-pac/releases/)
[![GH-code-size](https://img.shields.io/github/languages/code-size/fab5741/hass-vivreco-pac?color=red)](https://github.com/fab5741/hass-vivreco-pac)
[![issues](https://img.shields.io/github/issues/fab5741/hass-vivreco-pac)](https://github.com/fab5741/hass-vivreco-pac/issues)
[![GH-last-commit](https://img.shields.io/github/last-commit/fab5741/hass-vivreco-pac?style=flat-square)](https://github.com/fab5741/hass-vivreco-pac/commits/main)

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![HACS validation](https://github.com/fab5741/hass-vivreco-pac/workflows/HACS%20validation/badge.svg)](https://github.com/fab5741/hass-vivreco-pac/actions?query=workflow:"HACS+validation")
[![Validate with hassfest](https://github.com/fab5741/hass-vivreco-pac/workflows/Validate%20with%20hassfest/badge.svg)](https://github.com/fab5741/hass-vivreco-pac/actions?query=workflow:"Validate+with+hassfest")

Intégration non officielle pour [Home Assistant][home-assistant] permettant de connecter et superviser les pompes à chaleur [Vivreco][vivreco].  
Cette intégration récupère les données de fonctionnement et de température via l’API officielle de [Vivreco][vivreco].

## Fonctionnalités
- Suivi en temps réel de votre pompe à chaleur.
- Capteurs:
  - Consigne de température.
  - Température mesurée.
  - État du compresseur.
  - Mode de fonctionnement.
  - Consomation énergétique.
- Contrôle de votre pompe à chaleur :
  - Paramétrage des consignes de température
  - Sélection du type d'ambiance pour la zone principale (confort, normal, réduit, hors-gel)
  - Activer/Désactiver les modes chauffages, rafraîchissement, ECS.
- Configuration simple avec intervalle de mise à jour personnalisable.
- Fourniture d'une intégration type "climate" utilisable avec des cards type :
  - Simple Thermostat
  - Mushroom Climate
  - Thermostat
- Fourniture d'une intégration type "water_heater" pour le ballon d'eau chaude.

## Installation

### Installation manuelle

1. Clonez ce dépôt dans le dossier `custom_components` de votre installation Home Assistant.
   ```bash
   git clone https://github.com/fab5741/hass-vivreco-pac.git custom_components/hass_vivreco_pac
2. Redémarrez Home Assistant pour détecter l’intégration.

### Installation via HACS

1. Ouvrez **HACS** dans votre interface Home Assistant.  
2. Ajoutez ce dépôt comme **dépôt personnalisé / custom repository** :  
   - **URL** : https://github.com/fab5741/hass-vivreco-pac  
   - **Type** : Integration  
3. Recherchez puis installez l’intégration. 

## Exemple de capteurs disponibles

Une fois l’intégration configurée, vous pourrez voir apparaître différents capteurs, tels que :

- Température extérieure  
- Température intérieure
- Température de l’eau chaude sanitaire
- Consignes de température
- État de fonctionnement du compresseur
- Mode de fonctionnement activé
- Entité climate pour gérer le chauffage / rafraîchissement
- Entité water_heater pour gérer le ballon d'eau chaude

## Remarques importantes

- Ce projet est **non officiel** et n’est pas affilié à [Vivreco][vivreco].  
- Les données dépendent de l’API officielle et peuvent changer si celle-ci évolue.  
- Utilisez cette intégration à vos propres risques.  

## Contribuer

Les contributions sont les bienvenues !  
Pour signaler un problème ou proposer une amélioration, ouvrez une issue.  

> Actuellement, seules les informations de base sont récupérées.  
> L’API permet d’aller plus loin : n’hésitez pas à créer une pull request si vous souhaitez contribuer.  

## Dépannage
* Si vous rencontrez des problèmes de connexion, vérifiez vos identifiants [Vivreco][vivreco].
* Si les mises à jour ne se font pas, assurez-vous que l’intervalle de mise à jour est correctement défini et que l’intégration est bien activée dans Home Assistant.   

## License

Ce projet est distribué sous la licence MIT. Consultez le fichier LICENSE pour plus d’informations.

<!-- Badges -->

[hacs-url]: https://github.com/hacs/integration
[hacs-badge]: https://img.shields.io/badge/hacs-default-orange.svg?style=flat-square
[release-badge]: https://img.shields.io/github/v/release/fab5741/hass-vivreco-pac?style=flat-square
[downloads-badge]: https://img.shields.io/github/downloads/fab5741/hass-vivreco-pac/total?style=flat-square
[build-badge]: https://img.shields.io/github/actions/workflow/status/fab5741/hass-vivreco-pac/build.yml?branch=main&style=flat-square

<!-- Links -->
[home-assistant]: https://www.home-assistant.io/
[vivreco]: https://www.vivreco.fr/