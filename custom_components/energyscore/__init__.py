"""
Custom integration to integrate EnergyScore with Home Assistant.
Inspiration from
- Aaron Godfrey's custom component tutorial, part 3
- https://developers.home-assistant.io/docs/config_entries_index/
"""

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

import logging

_LOGGER: logging.Logger = logging.getLogger(__package__)

DOMAIN = "energyscore"  # burde kunne importere denne.. men står her: https://developers.home-assistant.io/docs/creating_component_index/

_LOGGER.warning(" - - - - - - - - init file is read")


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up platform from a ConfigEntry."""
    hass.data.setdefault(DOMAIN, {})
    _LOGGER.warning(" - - - - - - - - Default has been set")
    hass.data[DOMAIN][entry.entry_id] = entry.data
    _LOGGER.warning(" - - - - - - - - Entry data: %s", entry.data)

    # Forward the setup to the sensor platform.
    await hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    _LOGGER.warning(" - - - - - - - - Task has been created")
    return True


# TODO: Check what this next function does. Could this be the reason for not showing energyscore intergration name without unique_id in yaml?
# Står om denne her: https://developers.home-assistant.io/docs/creating_component_index/
async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the EnergyScore integration from yaml configuration."""
    hass.data.setdefault(DOMAIN, {})
    return True
