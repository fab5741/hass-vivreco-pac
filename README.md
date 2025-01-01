# hass-vivreco-pac

[![hacs][hacs-badge]][hacs-url]
[![release][release-badge]][release-url]
![downloads][downloads-badge]
![build][build-badge]

Intégration non officielle pour [Home Assistant][home-assistant] permettant de connecter et de superviser les pompes à chaleur [Vivreco][vivreco]. Cette intégration récupère les données de fonctionnement et de température via l'API officielle de [Vivreco][vivreco].

---

## Fonctionnalités
- Suivi en temps réel des données de votre pompe à chaleur.
- Capteurs pour la température, l'état du compresseur, et d'autres valeurs clés.
- Configuration simple et intervalle de mise à jour personnalisable.

---

## Installation

1. Clonez ce dépôt dans le dossier `custom_components` de votre installation Home Assistant.
   ```bash
   git clone https://github.com/votre-utilisateur/hass-vivreco-pac.git custom_components/hass-vivreco-pac
2. Redémarrez Home Assistant pour détecter l'intégration.

---

## Configuration

```yaml
sensor:                    
  - platform: hass-vivreco-pac
    username: "USERNAME"  # Votre email utilisé pour Vivreco
    password: "PASSWORD"  # Votre mot de passe Vivreco
    interval: 5           # (Optionnel) Intervalle de mise à jour des données en minutes (5 par défaut)
```

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