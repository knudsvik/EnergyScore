from homeassistant import config_entries
from .const import DOMAIN
import voluptuous as vol


class EnergyScoreConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """EnergyScore config flow."""

    async def async_step_user(self, info):
        """Invoked when a user initiates a flow via the user interface."""
        if info is not None:
            pass  # TODO: process info

        return self.async_show_form(
            step_id="user", data_schema=vol.Schema({vol.Required("password"): str})
        )
