"""
ConfigFlow for EnergyScore
Inspiration from Aaron Godfrey's custom component tutorial, part 3
"""


import logging
from typing import Any

from homeassistant import config_entries
from homeassistant.const import CONF_NAME, CONF_UNIQUE_ID
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from .const import CONF_ENERGY_ENTITY, CONF_PRICE_ENTITY, DOMAIN

_LOGGER: logging.Logger = logging.getLogger(__package__)


# Use entityselector, see minmax
CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_ENERGY_ENTITY): cv.string,
        vol.Required(CONF_PRICE_ENTITY): cv.string,
        vol.Required(CONF_UNIQUE_ID): cv.string,
    }
)

_LOGGER.warning(" - - - - - - - - Configflow file is read")
DOMAIN = "energyscore"


class EnergyScoreConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """EnergyScore config flow."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Invoked when a user initiates a flow via the user interface."""
        _LOGGER.warning(" - - - - - - - - Start step")
        if user_input is not None:
            self.data = user_input
            _LOGGER.warning(" - - - - - - - - User input: %s", user_input)
            # This is probably where I would create a UUID, see:
            # https://developers.home-assistant.io/docs/config_entries_config_flow_handler/#unique-ids
            # combine name, and sensors..? this way same sensor will not be set up twice, but what about reconfig?

            self.async_create_entry(title="EnergyScore", data=self.data)
            _LOGGER.warning(" - - - - - - - - Entry has been created")

        return self.async_show_form(step_id="user", data_schema=CONFIG_SCHEMA)
