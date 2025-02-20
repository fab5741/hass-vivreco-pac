import logging
import aiohttp
import base64
from datetime import timedelta
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.exceptions import ConfigEntryNotReady

_LOGGER = logging.getLogger(__name__)

# Constantes pour les URLs de l'API
API_BASE_URL = "https://vivrecocontrol.com/api/v1"
API_LOGIN_URL = f"{API_BASE_URL}/herja/login"
API_USER_URL = f"{API_BASE_URL}/herja/user/me"
API_CHART_URL_TEMPLATE = f"{API_BASE_URL}/charts/{{hp_id}}/dashboard"
API_ENERGY_URL_TEMPLATE = f"{API_BASE_URL}/commands/{{hp_id}}/values/energy_meters"

# Intervalle de récupération des données (en minutes)
DEFAULT_UPDATE_INTERVAL = 5

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Initialisation de la plateforme des capteurs."""
    # Récupérer les identifiants de connexion depuis la configuration
    username = config.get("username")
    password = config.get("password")
    update_interval = config.get('interval', DEFAULT_UPDATE_INTERVAL)
    
    # Créer le coordinateur et récupérer l'identifiant de la PAC
    coordinator = VivrecoDataUpdateCoordinator(hass, username, password, update_interval)
    try:
        await coordinator.async_refresh()  # Rafraîchit les données initiales
    except ConfigEntryNotReady:
        _LOGGER.error("Impossible de récupérer les données initiales.")
        return

    # Vérifiez si des données sont disponibles avant de configurer les capteurs
    if not coordinator.data or "values" not in coordinator.data:
        _LOGGER.error("Aucune donnée disponible pour configurer les capteurs.")
        return

    # Créer les capteurs à partir des données
    sensors = []
    for sensor_key in coordinator.data["values"]:
        label = coordinator.data["labels"].get(sensor_key, sensor_key)
        
        if sensor_key == "state":
            sensors.append(VivrecoStateSensor(coordinator, sensor_key, label))
        elif sensor_key == "comp_one":
            sensors.append(VivrecoCompSensor(coordinator, sensor_key, label))
        elif sensor_key in ["t_ecs", "cons_t_int", "t_int", "cons_t_ecs", "t_ext"]:
            sensors.append(VivrecoTemperatureSensor(coordinator, sensor_key, label, SensorDeviceClass.TEMPERATURE))

    sensors.append(VivrecoConsumptionSensor(coordinator, 'ch_wh', 'ch_wh'))    
    sensors.append(VivrecoConsumptionSensor(coordinator, 'ecs_wh', 'ecs_wh'))    
    sensors.append(VivrecoConsumptionSensor(coordinator, 'other_wh', 'other_wh'))    
    
    async_add_entities(sensors)

class VivrecoDataUpdateCoordinator(DataUpdateCoordinator):
    """Gère la récupération et la mise à jour des données depuis l'API."""

    def __init__(self, hass, username, password, update_interval):
        """Initialise le coordinateur et récupère l'identifiant de la PAC."""
        self.username = username
        self.password = password
        self.api_token = None
        self.hp_id = None
        
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
        }

    async def _async_update_data(self):
        """Récupère les données depuis l'API."""
        # Si le token n'est pas encore récupéré, essayer de se connecter
        if not self.api_token:
            await self._async_login()

        # Si l'identifiant de la PAC n'est pas encore récupéré, essayer de le récupérer
        if not self.hp_id:
            await self._async_fetch_hp_id()

        # Construire l'URL de l'API avec l'identifiant de la PAC
        api_chart_url = API_CHART_URL_TEMPLATE.format(hp_id=self.hp_id)
        api_energy_url = API_ENERGY_URL_TEMPLATE.format(hp_id=self.hp_id)

        headers = {"Authorization": f"Bearer {self.api_token}"}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_chart_url, headers=headers) as response:
                    if response.status != 200:
                        _LOGGER.error(f"Erreur API : {response.status}")
                        return self.data
                    
                    # Tentative de récupération des données JSON
                    api_data = await response.json()
                    if "elements" not in api_data:
                        _LOGGER.error("Aucune donnée 'elements' trouvée dans la réponse de l'API.")
                        return self.data
                    
                    _LOGGER.debug(f"Données API récupérées : {api_data}")  # Log des données récupérées
                    self.data = api_data["elements"]
        
        except aiohttp.ClientError as e:
            _LOGGER.error(f"Erreur lors de la communication avec l'API : {e}")
        except Exception as e:
            _LOGGER.error(f"Erreur lors de la conversion de la réponse JSON : {e}")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_energy_url, headers=headers) as response:
                    if response.status != 200:
                        _LOGGER.error(f"Erreur API : {response.status}")
                        return self.data
                    
                    # Tentative de récupération des données JSON
                    api_data = await response.json()
                    if "elements" not in api_data:
                        _LOGGER.error("Aucune donnée 'elements' trouvée dans la réponse de l'API.")
                        return self.data
                    
                    _LOGGER.debug(f"Données API récupérées : {api_data}")  # Log des données récupérées
                    self.data['energy'] = api_data["values"]["values"]["energyValues"]["total"]
        
        except aiohttp.ClientError as e:
            _LOGGER.error(f"Erreur lors de la communication avec l'API : {e}")
        except Exception as e:
            _LOGGER.error(f"Erreur lors de la conversion de la réponse JSON : {e}")

        return self.data

    async def _async_login(self):
        """Effectue la connexion via Basic Auth et récupère le token API."""
        headers = {"Authorization": self._generate_basic_auth_header()}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(API_LOGIN_URL, headers=headers) as response:
                    if response.status != 200:
                        _LOGGER.error(f"Erreur lors de la connexion : {response.status}")
                        raise ConfigEntryNotReady("Impossible de se connecter à l'API.")
                    
                    login_data = await response.json()
                    self.api_token = login_data.get("token")
                    if not self.api_token:
                        _LOGGER.error("Aucun token API trouvé dans la réponse.")
                        raise ConfigEntryNotReady("Aucun token API trouvé.")
                    _LOGGER.debug(f"Token API récupéré : {self.api_token}")
        except aiohttp.ClientError as e:
            _LOGGER.error(f"Erreur lors de la tentative de connexion : {e}")
            raise ConfigEntryNotReady("Erreur de connexion à l'API.")
        except Exception as e:
            _LOGGER.error(f"Erreur inconnue lors de la connexion : {e}")
            raise ConfigEntryNotReady("Erreur inconnue lors de la connexion à l'API.")

    async def _async_fetch_hp_id(self):
        """Récupère l'identifiant de la PAC via l'API utilisateur."""
        headers = {"Authorization": f"Bearer {self.api_token}"}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(API_USER_URL, headers=headers) as response:
                    if response.status != 200:
                        _LOGGER.error(f"Erreur lors de la récupération de l'utilisateur : {response.status} - {headers}")
                        raise ConfigEntryNotReady("Impossible de récupérer l'identifiant de la PAC.")
                    
                    user_data = await response.json()
                    hp_ids = user_data.get("hp_id", [])
                    if not hp_ids:
                        _LOGGER.error("Aucun identifiant de PAC trouvé dans la réponse utilisateur.")
                        raise ConfigEntryNotReady("Aucun identifiant de PAC trouvé.")
                    
                    self.hp_id = hp_ids[0]  # Utilise le premier identifiant trouvé
                    _LOGGER.debug(f"Identifiant de la PAC récupéré : {self.hp_id}")
        except aiohttp.ClientError as e:
            _LOGGER.error(f"Erreur lors de la récupération de l'identifiant de la PAC : {e}")
            raise ConfigEntryNotReady("Erreur de récupération de l'identifiant de la PAC.")
        except Exception as e:
            _LOGGER.error(f"Erreur inconnue lors de la récupération de l'identifiant de la PAC : {e}")
            raise ConfigEntryNotReady("Erreur inconnue lors de la récupération de l'identifiant de la PAC.")

    def _generate_basic_auth_header(self):
        """Génère l'en-tête Basic Auth pour la connexion."""
        credentials = f"{self.username}:{self.password}"
        encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
        return f"Basic {encoded_credentials}"

class VivrecoSensor(SensorEntity):
    """Représentation d'un capteur Vivreco."""

    def __init__(self, coordinator, sensor_key, name, device_class=None):
        """Initialisation du capteur."""
        self.coordinator = coordinator
        self._sensor_key = sensor_key
        self._name = name
        self._device_class = device_class

    @property
    def name(self):
        """Retourne le nom du capteur."""
        return self._name

    @property
    def state(self):
        """Retourne la valeur actuelle du capteur."""
        return self.coordinator.data["values"].get(self._sensor_key)

    @property
    def unique_id(self):
        """Retourne l'identifiant unique du capteur."""
        return f"vivreco_{self._sensor_key}"

    @property
    def device_class(self):
        """Retourne la classe du capteur (température ici)."""
        return self._device_class

    async def async_update(self):
        """Mise à jour asynchrone du capteur."""
        await self.coordinator.async_request_refresh()

class VivrecoTemperatureSensor(VivrecoSensor):
    """Représentation d'un capteur de température Vivreco."""
    @property
    def unit_of_measurement(self):
        """Retourne l'unité de mesure (°C pour les températures)."""
        return "°C"

class VivrecoStateSensor(SensorEntity):
    """Représentation du capteur d'état de la pompe à chaleur."""

    def __init__(self, coordinator, sensor_key, name):
        """Initialisation du capteur d'état."""
        self.coordinator = coordinator
        self._sensor_key = sensor_key
        self._name = name

    @property
    def name(self):
        """Retourne le nom du capteur."""
        return self._name

    @property
    def state(self):
        """Retourne l'état actuel de la pompe à chaleur."""
        state_value = self.coordinator.data["values"].get(self._sensor_key)
        
        # Gérer les états possibles
        state_mapping = {
            "bt": "Chauffage",
            "degi": "Dégivrage",
            "arret": "Inactive",  
        }
        
        return state_mapping.get(state_value, "Inconnu")

    @property
    def unique_id(self):
        """Retourne l'identifiant unique du capteur."""
        return f"vivreco_{self._sensor_key}"
    
class VivrecoCompSensor(BinarySensorEntity):
    """Représentation d'un capteur binaire pour le compresseur."""

    def __init__(self, coordinator, sensor_key, name):
        """Initialisation du capteur binaire."""
        self.coordinator = coordinator
        self._sensor_key = sensor_key
        self._name = name

    @property
    def is_on(self):
        """Retourne True si le compresseur est en marche (1), False sinon (0)."""
        return bool(self.coordinator.data["values"].get(self._sensor_key))

    @property
    def name(self):
        """Retourne le nom du capteur."""
        return self._name

    @property
    def unique_id(self):
        """Retourne l'identifiant unique du capteur."""
        return f"vivreco_{self._sensor_key}"

class VivrecoConsumptionSensor(VivrecoSensor):
    """Représentation d'un capteur de consommation quotidienne Vivreco."""

    @property
    def unit_of_measurement(self):
        """Retourne l'unité de mesure (kWh pour la consommation)."""
        return "kWh"

    @property
    def state(self):
        """Retourne la consommation quotidienne en kWh."""
        ch_consumption = self.coordinator.data["energy"]["values"]["values"]["energyValues"]["total"]
        return ch_consumption if ch_consumption is not None else "N/A"
