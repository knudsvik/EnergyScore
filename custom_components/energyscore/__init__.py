"""
Custom integration to integrate EnergyScore with Home Assistant.
Inspiration from
- Aaron Godfrey's custom component tutorial, parts 3 and 4
- https://developers.home-assistant.io/docs/config_entries_index/
"""

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN

import logging

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up platform from a ConfigEntry."""

    # Forward the setup to the sensor platform.
    await hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )

    # Registers update listener to update config entry when options are updated.
    entry.async_on_unload(entry.add_update_listener(async_update_entry))

    return True


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the EnergyScore integration from yaml configuration."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_update_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Handle options update."""
    _LOGGER.debug(" -- ES: The update_listener has been called (only upon new data)")
    await hass.config_entries.async_reload(entry.entry_id)
