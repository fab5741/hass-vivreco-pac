"""Les constantes pour l'intégration Vivreco PAC."""

from homeassistant.const import Platform

DOMAIN = "hass_vivreco_pac"

PLATFORMS: list[Platform] = [Platform.BINARY_SENSOR, Platform.SENSOR]

# Constantes pour les URLs de l'API
API_BASE_URL = "https://vivrecocontrol.com/api/v1"
API_LOGIN_URL = f"{API_BASE_URL}/herja/login"
API_USER_URL = f"{API_BASE_URL}/herja/user/me"
API_CHART_URL_TEMPLATE = f"{API_BASE_URL}/charts/{{hp_id}}/dashboard"
API_ENERGY_URL_TEMPLATE = f"{API_BASE_URL}/commands/{{hp_id}}/values/energy_meters"
API_SETTINGS_URL_TEMPLATE = (
    f"{API_BASE_URL}/commands/{{hp_id}}/values/customer_settings"
)

# Mode de fonctionnement de la PAC
MODE = {
    "auth_p/etat_glob/aut_app_elec": "mode_appoint_elec",
    "auth_p/etat_glob/aut_ch": "mode_ch",
    "auth_p/etat_glob/aut_ecs": "mode_ecs",
    "auth_p/etat_glob/aut_raf": "mode_raf",
}

MODE_ICON_MAPPING = {
    "mode_appoint_elec": "mdi:flash",
    "mode_ch": "mdi:fire",
    "mode_ecs": "mdi:shower",
    "mode_raf": "mdi:snowflake",
}


# Intervalle de récupération des données (en minutes)
DEFAULT_UPDATE_INTERVAL = 5
