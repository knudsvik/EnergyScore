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

    # hass.data.setdefault(DOMAIN, {})
    # hass.data[DOMAIN][entry.entry_id] = entry.data

    hass_data = dict(entry.data)
    _LOGGER.warning("Hass_data: %s", hass_data)
    # Registers update listener to update config entry when options are updated.
    unsub_options_update_listener = entry.add_update_listener(options_update_listener)
    # Store a reference to the unsubscribe function to cleanup if an entry is unloaded.
    hass_data["unsub_options_update_listener"] = unsub_options_update_listener
    hass.data[DOMAIN][entry.entry_id] = hass_data

    # Forward the setup to the sensor platform.
    await hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    return True


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the EnergyScore integration from yaml configuration."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def options_update_listener(hass: HomeAssistant, config_entry: ConfigEntry):
    """Handle options update."""
    _LOGGER.warning("The update_listener has been called (only upon new data)")
    await hass.config_entries.async_reload(config_entry.entry_id)
