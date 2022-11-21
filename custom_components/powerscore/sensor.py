"""Sensor platform for integration_blueprint."""
import logging
import numpy as np
from typing import Callable, Optional
import voluptuous as vol

from homeassistant.components.sensor import SensorEntity, PLATFORM_SCHEMA
from homeassistant.const import CONF_ENTITY_ID, CONF_NAME

import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType,
)

from .const import (
    DEFAULT_NAME,
    DOMAIN,
    ICON,
    SENSOR,
)

_LOGGER: logging.Logger = logging.getLogger(__package__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {vol.Required(CONF_NAME): cv.string, vol.Required(CONF_ENTITY_ID): cv.string}
)

""" async def async_setup_entry(hass, entry, async_add_devices):
    "Setup sensor platform."
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices([PowerScore(coordinator, entry)]) """


async def async_setup_platform(
    hass: HomeAssistantType,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    """Set up the sensor platform"""
    sensors = config[CONF_NAME]
    async_add_entities(sensors, update_before_add=True)


class PowerScore(SensorEntity):
    """PowerScore Sensor class."""

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{DEFAULT_NAME}_{SENSOR}"

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        return self.coordinator.data.get("body")

    # @property
    # def state(self):
    #    return np.random.random()

    @property
    def native_unit_of_measurement(self):
        """Return the UoM of the sensor."""
        return "%"

    @property
    def state_class(self):
        """Return the state class of the sensor."""
        return "measurement"

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return ICON

    async def async_update(self):
        try:
            self._state = np.random.random()
        except:
            _LOGGER.exception("Could not update the PowerScore")
