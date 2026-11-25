"""Coordinator Vivreco PAC API integration."""

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Minutes par jour (utilisé pour le calcul du pourcentage d'utilisation)
MINUTES_PER_DAY = 1440

# Périodes renvoyées par l'API dans tableValues
PERIODS = ("d", "d1", "w", "w1", "m", "m1", "y", "y1", "total")


def parse_duration_hours(value: Any) -> float | None:
    """Convertit une durée Vivreco en heures décimales.

    Args:
        value: Durée renvoyée par l'API, au format "21366h25", "3h" ou "0h31",
            ou déjà numérique.

    Returns:
        Durée en heures arrondie à 2 décimales, ou None si la valeur est
        absente ou illisible.
    """
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().lower()
    if "h" not in text:
        try:
            return float(text)
        except ValueError:
            return None
    hours, _, minutes = text.partition("h")
    try:
        result = int(hours or 0) + (int(minutes) / 60 if minutes else 0)
    except ValueError:
        return None
    return round(result, 2)


def is_legacy_energy_format(energy_values: Any) -> bool:
    """Détecte le format d'energy_meters de l'ancienne régulation (Comfile).

    L'ancienne régulation (écran bleu) ne renvoie que tableValues.gene,
    sans energyValues ni timeValues.

    Args:
        energy_values: Contenu de values.values de la réponse energy_meters.

    Returns:
        True si la réponse correspond au format de l'ancienne régulation.
    """
    if not isinstance(energy_values, dict):
        return False
    gene = energy_values.get("tableValues", {}).get("gene")
    return (
        "energyValues" not in energy_values
        and isinstance(gene, list)
        and len(gene) >= 2
    )


def parse_legacy_gene(gene: Any) -> dict[str, dict[str, Any]]:
    """Interprète tableValues.gene de l'ancienne régulation.

    Structure attendue (cf. issue #8) :
    - ligne 0 : durée de fonctionnement ("21366h25") ;
    - lignes intermédiaires : consommations en kWh (HP puis HC s'il y en a deux) ;
    - dernière ligne (si au moins 3 lignes) : nombre de démarrages.

    Args:
        gene: Liste tableValues.gene de la réponse energy_meters.

    Returns:
        Dictionnaire avec les clés duration, energy_total, energy_hp, energy_hc
        et starts, chacune associant une période (d, d1, w, w1, m, m1, y, y1,
        total) à sa valeur. Dictionnaire vide si gene est inexploitable.
    """
    if not isinstance(gene, list) or len(gene) < 2:
        return {}

    def row(index: int) -> dict[str, Any]:
        item = gene[index] if index < len(gene) else None
        return item if isinstance(item, dict) else {}

    duration = {p: parse_duration_hours(row(0).get(p)) for p in PERIODS}

    if len(gene) >= 3:
        energy_rows = [row(i) for i in range(1, len(gene) - 1)]
        starts = {p: row(len(gene) - 1).get(p) for p in PERIODS}
    else:
        energy_rows = [row(1)]
        starts = {}

    energy_hp = {p: energy_rows[0].get(p) for p in PERIODS}
    energy_hc = (
        {p: energy_rows[1].get(p) for p in PERIODS} if len(energy_rows) >= 2 else {}
    )

    energy_total = {}
    for p in PERIODS:
        values = [r.get(p) for r in energy_rows if isinstance(r.get(p), (int, float))]
        energy_total[p] = round(sum(values), 3) if values else None

    return {
        "duration": duration,
        "energy_total": energy_total,
        "energy_hp": energy_hp,
        "energy_hc": energy_hc,
        "starts": starts,
    }


class VivrecoDataUpdateCoordinator(DataUpdateCoordinator):
    """Gère la récupération et la mise à jour des données depuis l'API."""

    def __init__(self, hass: HomeAssistant, update_interval) -> None:
        """Initialise le coordinateur."""
        super().__init__(
            hass,
            _LOGGER,
            name="Vivreco PAC",
            update_interval=timedelta(minutes=update_interval),
        )

        self.data = {
            "values": {},
            "labels": {},
            "energy": {},
            "time_values": {},
            "cop": {},
            "legacy": False,
            "legacy_energy": {},
            "humidity": {},
            "settings": {},
            "config": {},
            "usage": {},
        }

    @property
    def api(self):
        """API Vivreco."""
        return self.hass.data[DOMAIN]["api"]

    async def _async_update_data(self):
        """Récupère les données depuis l'API."""

        _LOGGER.debug("Appel de mise à jour de données depuis Vivreco API")
        # Si le token n'est pas encore récupéré, essayer de se connecter
        if not self.api.api_token:
            await self.api.login()

        # Si l'identifiant de la PAC n'est pas encore récupéré, essayer de le récupérer
        if not self.api.hp_id:
            await self.api.fetch_hp_id()

        chart_data = await self.api.get_chart_data()
        chart_data_since1h = await self.api.get_chart_data_since1h()
        usage_data = await self.api.get_usage_data()
        energy_data = await self.api.get_energy_data()
        settings_data = await self.api.get_settings_data()

        if chart_data and "elements" in chart_data:
            self.data = chart_data["elements"]

        # Initialiser les valeurs d'énergie par défaut
        energy_values = energy_data.get("values", {}).get("values", {})

        # Consommation énergétique
        self.data["energy"] = energy_values.get("energyValues", {}).get("total", [])

        # Durées de fonctionnement (en heures)
        self.data["time_values"] = energy_values.get("timeValues", {}).get("total", [])

        table_values = energy_values.get("tableValues", {})
        gene_data = table_values.get("gene", [])

        # Ancienne régulation (type Comfile, écran bleu) : l'API ne renvoie que
        # tableValues.gene, sans energyValues ni timeValues, et sans COP.
        # gene = [Durée, Conso HP, Conso HC, Démarrages] (cf. issue #8)
        self.data["legacy"] = is_legacy_energy_format(energy_values)
        self.data["legacy_energy"] = (
            parse_legacy_gene(gene_data) if self.data["legacy"] else {}
        )

        # COP (Coefficient de Performance)
        # Régulation récente : le COP est toujours la dernière ligne de
        # tableValues.gene (3 lignes : Durée, Conso, COP ; 4 lignes avec HC/HP :
        # Durée, Conso HP, Conso HC, COP). L'ancienne régulation ne fournit pas
        # de COP : sa dernière ligne est le nombre de démarrages.
        if self.data["legacy"]:
            self.data["cop"] = {}
        else:
            self.data["cop"] = gene_data[-1] if gene_data else {}

        # Humidité intérieure
        self.data["humidity"] = None
        if (
            chart_data_since1h
            and "values" in chart_data_since1h
            and "hyg" in chart_data_since1h["values"]
        ):
            hyg_values = chart_data_since1h["values"]["hyg"]
            if hyg_values:
                self.data["humidity"] = hyg_values[-1]

        # Usage data
        if usage_data and "usage" in usage_data:
            self.data["usage"] = {
                item["name"]: round((item["value"] * 100) / MINUTES_PER_DAY, 2)
                for item in usage_data["usage"]
            }

            self.data["usage"]["rate"] = usage_data.get("rate", 0)

        if settings_data and "values" in settings_data:
            settings = settings_data["values"]["values"]
            self.data["settings"] = settings

            # Détection des fonctionnalités disponibles
            self.data["config"] = {
                "app_elec": "auth_p/etat_glob/aut_app_elec" in settings,
                "ch": "auth_p/etat_glob/aut_ch" in settings,
                "ecs": "auth_p/etat_glob/aut_ecs" in settings,
                "raf": "auth_p/etat_glob/aut_raf" in settings,
            }

        return self.data
