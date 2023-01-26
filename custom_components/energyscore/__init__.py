"""
Custom integration to integrate EnergyScore with Home Assistant.
Inspiration from
- Aaron Godfrey's custom component tutorial, parts 3 and 4
- https://developers.home-assistant.io/docs/config_entries_index/
"""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN

PLATFORMS = [Platform.SENSOR]

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up platform from a ConfigEntry."""

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # Registers update listener to update config entry when options are updated.
    entry.async_on_unload(entry.add_update_listener(update_listener))

    # Forward the setup to the sensor platform.
    await hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    return True


async def update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the EnergyScore integration from yaml configuration."""
    hass.data.setdefault(DOMAIN, {})
    return True
