"""
ConfigFlow for EnergyScore
Inspiration from Aaron Godfrey's custom component tutorial, part 3
"""

from typing import Any

from homeassistant import config_entries
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.const import CONF_NAME, CONF_UNIQUE_ID
from homeassistant.helpers import selector
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from .const import CONF_ENERGY_ENTITY, CONF_PRICE_ENTITY, DOMAIN

import logging

_LOGGER: logging.Logger = logging.getLogger(__package__)

# Use entityselector, see minmax
CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): selector.TextSelector(),
        vol.Required(CONF_ENERGY_ENTITY): selector.EntitySelector(
            selector.EntitySelectorConfig(
                domain=[SENSOR_DOMAIN],
            ),
        ),
        vol.Required(CONF_PRICE_ENTITY): selector.EntitySelector(
            selector.EntitySelectorConfig(
                domain=[SENSOR_DOMAIN],
            ),
        ),
    }
)


class EnergyScoreConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """EnergyScore config flow."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Invoked when a user initiates a flow via the user interface."""

        if user_input is not None:
            self.data = user_input

            # Create a unique ID:
            _LOGGER.warning("SELF DATA before: %s", self.data)
            _unique_id = (
                f"ES_{self.data['energy_entity']}_{self.data['price_entity']}".replace(
                    "sensor.", ""
                )
            )

            self.data["unique_id"] = _unique_id
            _LOGGER.warning("SELF DATA after: %s", self.data)

            # await self.async_set_unique_id(_unique_id)
            # virker ikke? alternativt bare sette self.data[unique_id]?
            # self._abort_if_unique_id_configured()

            return self.async_create_entry(title="EnergyScore", data=self.data)

        return self.async_show_form(step_id="user", data_schema=CONFIG_SCHEMA)
