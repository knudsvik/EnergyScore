"""Sensor platform for integration_blueprint."""
from datetime import timedelta
from typing import Callable
import logging
import numpy as np
import voluptuous as vol

from homeassistant.components.sensor import SensorEntity, PLATFORM_SCHEMA
from homeassistant.const import CONF_NAME
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.typing import (
    ConfigType,
    HomeAssistantType,
    Optional,
    DiscoveryInfoType,
)

from .const import CONF_POWER_ENTITY, CONF_PRICE_ENTITY

_LOGGER: logging.Logger = logging.getLogger(__package__)

# Time between updating data TODO: Set to be triggered by a new data point (every whole hour?)
SCAN_INTERVAL = timedelta(minutes=1)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_POWER_ENTITY): cv.entity_id,
        vol.Required(CONF_PRICE_ENTITY): cv.entity_id,
    }
)


async def async_setup_platform(
    hass: HomeAssistantType,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    """Set up the sensors from YAML config"""
    # sensors = [PowerScore(sensor) for sensor in config[CONF_NAME]]
    # async_add_entities(sensors)
    async_add_entities([PowerScore()])


class PowerScore(SensorEntity):
    """PowerScore Sensor class."""

    def __init__(self):
        self._name = CONF_NAME
        self._state = None
        self._power = CONF_POWER_ENTITY
        self._price = CONF_PRICE_ENTITY

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
        """Updates the sensor"""
        try:
            self._state = np.random.random()
        except:
            _LOGGER.exception("Could not update the PowerScore")
