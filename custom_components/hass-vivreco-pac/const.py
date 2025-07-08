"""Les constantes pour l'intégration Vivreco PAC."""

from homeassistant.const import Platform

DOMAIN = "hass-vivreco-pac"

PLATFORMS: list[Platform] = [Platform.SENSOR]

# Constantes pour les URLs de l'API
API_BASE_URL = "https://vivrecocontrol.com/api/v1"
API_LOGIN_URL = f"{API_BASE_URL}/herja/login"
API_USER_URL = f"{API_BASE_URL}/herja/user/me"
API_CHART_URL_TEMPLATE = f"{API_BASE_URL}/charts/{{hp_id}}/dashboard"
API_ENERGY_URL_TEMPLATE = f"{API_BASE_URL}/commands/{{hp_id}}/values/energy_meters"

# Intervalle de récupération des données (en minutes)
DEFAULT_UPDATE_INTERVAL = 5
