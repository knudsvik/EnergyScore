"""
Custom integration to integrate EnergyScore with Home Assistant.
Inspiration from
- Aaron Godfrey's custom component tutorial, part 3
- https://developers.home-assistant.io/docs/config_entries_index/
"""

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up platform from a ConfigEntry."""

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # Forward the setup to the sensor platform.
    await hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    return True


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the EnergyScore integration from yaml configuration."""
    hass.data.setdefault(DOMAIN, {})
    return True
