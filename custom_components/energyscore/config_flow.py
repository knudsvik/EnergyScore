"""
ConfigFlow for EnergyScore
Inspiration from Aaron Godfrey's custom component tutorial, part 3
"""


from homeassistant import config_entries
import voluptuous as vol
from typing import Any
from .const import CONF_ENERGY_ENTITY, CONF_PRICE_ENTITY, DOMAIN
import homeassistant.helpers.config_validation as cv
from homeassistant.const import CONF_NAME, CONF_UNIQUE_ID


# Use entityselector, see minmax
CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_ENERGY_ENTITY): cv.string,
        vol.Required(CONF_PRICE_ENTITY): cv.string,
        vol.Required(CONF_UNIQUE_ID): cv.string,
    }
)


class EnergyScoreConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """EnergyScore config flow."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Invoked when a user initiates a flow via the user interface."""
        if user_input is not None:
            self.data = user_input
            # This is probably where I would create a UUID, see:
            # https://developers.home-assistant.io/docs/config_entries_config_flow_handler/#unique-ids
            # combine name, and sensors..? this way same sensor will not be set up twice, but what about reconfig?

            self.async_create_entry(title="EnergyScore", data=self.data)

        return self.async_show_form(step_id="user", data_schema=CONFIG_SCHEMA)
