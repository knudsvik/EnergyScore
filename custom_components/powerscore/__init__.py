"""
Custom integration to integrate PowerScore with Home Assistant.

For more details about this integration, please refer to
https://github.com/knudsvik/powerscore
"""
# import logging

# from homeassistant.core import Config, HomeAssistant

# from homeassistant.helpers.aiohttp_client import async_get_clientsession
# from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

# from .api import IntegrationBlueprintApiClient

"""from .const import (
    DOMAIN,
    PLATFORMS,
    STARTUP_MESSAGE,
)"""

# _LOGGER: logging.Logger = logging.getLogger(__package__)


''' Tar disse vekk iht https://aarongodfrey.dev/home%20automation/building_a_home_assistant_custom_component_part_1/
async def async_setup(hass: HomeAssistant, config: Config):
    # def setup(hass, config):
    """Set up this integration using YAML is not supported."""
    _LOGGER.info(STARTUP_MESSAGE)

    return True
'''

'''
class BlueprintDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(
        self, hass: HomeAssistant, client: IntegrationBlueprintApiClient
    ) -> None:
        """Initialize."""
        self.api = client
        self.platforms = []

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)

    async def _async_update_data(self):
        """Update data via library."""
        try:
            return await self.api.async_get_data()
        except Exception as exception:
            raise UpdateFailed() from exception
'''
