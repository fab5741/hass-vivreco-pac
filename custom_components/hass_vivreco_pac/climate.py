"""Plateforme Climate pour Vivreco PAC."""

import logging

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant

from .const import CHAUFFAGE_SETPOINTS, DOMAIN
from .entity import VivrecoBaseEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
):
    """Configurer l’entité Climate Vivreco PAC."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    config = coordinator.data.get("config", {})

    # Si la PAC ne supporte pas CH ou RAF, ne pas créer l'entité
    if not config.get("ch", False) and not config.get("raf", False):
        _LOGGER.info(
            "Climate/Chauffage non supporté, l'entité Climate ne sera pas ajoutée"
        )
        return

    async_add_entities([VivrecoClimate(coordinator)])


class VivrecoClimate(VivrecoBaseEntity, ClimateEntity):
    """Représentation de la PAC Vivreco en tant qu’entité Climate."""

    _attr_has_entity_name = True
    _attr_translation_key = "climatisation"
    _attr_unique_id = "vivreco_climate"
    _attr_temperature_unit = UnitOfTemperature.CELSIUS

    # Modes supportés
    _attr_hvac_modes = [HVACMode.HEAT, HVACMode.COOL, HVACMode.OFF]

    # Fonctionnalités supportées
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.PRESET_MODE
    )

    def __init__(self, coordinator) -> None:
        """Initialisation du Climate."""
        super().__init__(coordinator)
        self.coordinator = coordinator
        self.config = coordinator.data.get("config", {})

    # ---------- Températures ----------

    @property
    def current_temperature(self):
        """Retourne la température ambiante mesurée."""
        return self.coordinator.data["values"].get("t_int")

    @property
    def target_temperature(self):
        """Retourne la consigne correspondant au preset actif."""
        preset = self.preset_mode
        key = CHAUFFAGE_SETPOINTS.get(preset, {}).get("key")
        if key:
            return self.coordinator.data["settings"].get(key)
        return None

    @property
    def min_temp(self):
        """Retourne la température minimale possible pour le preset actif."""
        preset = self.preset_mode
        return CHAUFFAGE_SETPOINTS.get(preset, {}).get("min", 5)

    @property
    def max_temp(self):
        """Retourne la température maximale possible pour le preset actif."""
        preset = self.preset_mode
        return CHAUFFAGE_SETPOINTS.get(preset, {}).get("max", 30)

    # ---------- Modes HVAC ----------

    @property
    def hvac_mode(self) -> HVACMode:
        """Retourne le mode HVAC actuel (chauffage / rafraîchissement / off)."""
        settings = self.coordinator.data.get("settings", {})

        if settings.get("auth_p/etat_glob/aut_ch") and self.config.get("ch", False):
            return HVACMode.HEAT
        if settings.get("auth_p/etat_glob/aut_raf") and self.config.get("raf", False):
            return HVACMode.COOL
        return HVACMode.OFF

    @property
    def hvac_modes(self) -> list[HVACMode]:
        """Liste des modes HVAC disponibles selon les capacités de la PAC."""
        modes = [HVACMode.OFF]
        if self.config.get("ch", False):
            modes.append(HVACMode.HEAT)
        if self.config.get("raf", False):
            modes.append(HVACMode.COOL)
        return modes

    # ---------- Presets ----------

    @property
    def preset_modes(self) -> list[str]:
        """Retourne la liste des presets disponibles (hg, réduit, confort, normal)."""
        return list(CHAUFFAGE_SETPOINTS.keys())

    @property
    def preset_mode(self) -> str:
        """Retourne le preset actuellement actif."""
        return self.coordinator.data.get("settings", {}).get(
            "mode_zone_p/ambiance", "normal"
        )

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Change le preset sélectionné."""
        if preset_mode is None:
            preset_mode = "normal"

        if preset_mode not in CHAUFFAGE_SETPOINTS:
            _LOGGER.warning("Preset invalide : %s", preset_mode)
            return

        await self.coordinator.api.send_command(
            group="customer_settings",
            values={"mode_zone_p/ambiance": preset_mode},
        )
        await self.coordinator.async_request_refresh()

    # ---------- Actions ----------

    async def async_set_temperature(self, **kwargs):
        """Définit une nouvelle température de consigne pour le preset actif."""
        value = kwargs.get("temperature")
        preset = self.preset_mode
        key = CHAUFFAGE_SETPOINTS.get(preset, {}).get("key")

        if value is None or key is None:
            return

        _LOGGER.debug("Mise à jour consigne %s -> %s°C", preset, value)

        await self.coordinator.api.send_command(
            group="customer_settings",
            values={key: value},
        )
        await self.coordinator.async_request_refresh()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Change le mode HVAC (chauffage / rafraîchissement / arrêt)."""
        values = {}

        if hvac_mode == HVACMode.OFF:
            values = {
                "auth_p/etat_glob/aut_ch": False,
                "auth_p/etat_glob/aut_raf": False,
            }

        elif hvac_mode == HVACMode.HEAT:
            values["auth_p/etat_glob/aut_ch"] = True
            values["auth_p/etat_glob/aut_raf"] = False

            # On conserve le preset courant, ou "normal" par défaut
            values["mode_zone_p/ambiance"] = self.preset_mode or "normal"

        elif hvac_mode == HVACMode.COOL:
            values["auth_p/etat_glob/aut_ch"] = False
            values["auth_p/etat_glob/aut_raf"] = True

            # en mode rafraîchissement, on force "normal"
            values["mode_zone_p/ambiance"] = "normal"

        else:
            return

        await self.coordinator.api.send_command(
            group="customer_settings", values=values
        )
        await self.coordinator.async_request_refresh()
