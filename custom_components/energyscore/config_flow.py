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

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Invoked when a user initiates a flow via the user interface."""
        if user_input is not None:
            self.data = user_input

        return self.async_show_form(step_id="setup", data_schema=CONFIG_SCHEMA)
