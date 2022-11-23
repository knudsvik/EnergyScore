"""Sensor platform for integration_blueprint."""
from datetime import timedelta
from typing import Callable
import logging
import numpy as np
import voluptuous as vol

from homeassistant.components.sensor import SensorEntity, PLATFORM_SCHEMA
from homeassistant.const import CONF_NAME

import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import (
    CONF_POWER_ENTITY,
    CONF_PRICE_ENTITY,
    DEFAULT_NAME,
    DOMAIN,
    ICON,
    SENSOR,
)

_LOGGER: logging.Logger = logging.getLogger(__package__)

# Time between updating data TODO: Set to be triggered by a new data point (every whole hour?)
SCAN_INTERVAL = timedelta(minutes=1)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_POWER_ENTITY): cv.string,
        vol.Required(CONF_PRICE_ENTITY): cv.string,
    }
)  # TODO: Add unique ID? Need to add as a sensor class property


async def async_setup_platform(
    config: ConfigType, async_add_entities: Callable
) -> None:
    """Set up the sensor platform"""
    sensors = [PowerScore(sensor) for sensor in config[CONF_NAME]]
    async_add_entities(sensors)


class PowerScore(SensorEntity):
    """PowerScore Sensor class."""

    def __init__(self):
        self._name = f"{DEFAULT_NAME}_{SENSOR}"  # TODO: Get name from yaml in here
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        return self._state

    # @property
    # def device_state_attributes(self) -> Dict[str, Any]:
    #    return self.attrs

    async def async_update(self):
        try:
            self._state = np.random.random()
        except:
            _LOGGER.exception("Could not update the PowerScore")
