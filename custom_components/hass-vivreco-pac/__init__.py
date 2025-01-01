import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass, config):
    """Set up the vivreco_pac integration."""
    hass.data["hass-vivreco-pac"] = {}
    return True
