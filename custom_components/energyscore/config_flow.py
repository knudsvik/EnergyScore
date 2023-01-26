"""
ConfigFlow for EnergyScore
Inspiration from Aaron Godfrey's custom component tutorial, parts 3 and 4
"""

import logging
from typing import Any

from homeassistant import config_entries
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.const import CONF_NAME, CONF_UNIQUE_ID
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_registry import (
    async_entries_for_config_entry,
    async_get_registry,
)
import voluptuous as vol

from .const import CONF_ENERGY_ENTITY, CONF_PRICE_ENTITY, CONF_TRESHOLD, DOMAIN

_LOGGER: logging.Logger = logging.getLogger(__package__)

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
            _unique_id = (
                f"ES_{self.data['energy_entity']}_{self.data['price_entity']}".replace(
                    "sensor.", ""
                )
            )
            self.data["unique_id"] = _unique_id

            return self.async_create_entry(title=self.data["name"], data=self.data)

        return self.async_show_form(step_id="user", data_schema=CONFIG_SCHEMA)

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """EnergyScore options flow."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry
        self.current_config: dict = dict(config_entry.data)
        self.current_options = dict(config_entry.options)
        _LOGGER.debug(" -- ES: The current config is: %s", self.current_config)
        _LOGGER.debug(
            " -- ES: The current config options are: %s", self.current_options
        )

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""

        if user_input is not None:
            # _LOGGER.debug(" -- ES: The user input: %s", user_input)
            # Following DOES NOT STICK! WHY? maybe not needed
            # self.current_config.update({CONF_TRESHOLD: user_input[CONF_TRESHOLD]})
            return self.async_create_entry(title="", data=user_input)

        options_schema = vol.Schema(
            {
                vol.Optional(
                    "energy_treshold",
                    default=self.current_options[CONF_TRESHOLD],
                ): vol.Coerce(float)
            }
        )

        return self.async_show_form(step_id="init", data_schema=options_schema)
