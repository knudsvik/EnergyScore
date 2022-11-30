"""Sensor platform for integration_blueprint."""
import datetime
from datetime import timedelta
from typing import Callable, Any
import logging

import numpy as np
import voluptuous as vol

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
    PLATFORM_SCHEMA,
)
from homeassistant.const import CONF_NAME, CONF_UNIQUE_ID
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.typing import (
    ConfigType,
    Optional,
    DiscoveryInfoType,
)
from homeassistant.util import dt

from .const import CONF_ENERGY_ENTITY, CONF_PRICE_ENTITY

_LOGGER: logging.Logger = logging.getLogger(__package__)

# Time between updating data TODO: Set to be triggered by a new data point (every whole hour?)
SCAN_INTERVAL = timedelta(minutes=10)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_ENERGY_ENTITY): cv.entity_id,
        vol.Required(CONF_PRICE_ENTITY): cv.entity_id,
        vol.Optional(CONF_UNIQUE_ID): cv.string,
    }
)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    """Set up the sensors from YAML config"""
    # sensors = [EnergyScore(sensor) for sensor in config[CONF_NAME]]
    # async_add_entities(sensors)
    async_add_entities([EnergyScore(hass, config)], update_before_add=False)


class EnergyScore(SensorEntity):
    """EnergyScore Sensor class."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "%"

    def __init__(self, hass, config):
        self._current_price = None  # TODO: Not needed?
        self._current_energy = None  # TODO: Not needed? or maybe define it with :?
        self._name = config[CONF_NAME]
        self._energy_entity = config[CONF_ENERGY_ENTITY]
        self._last_updated: datetime.datetime | None = None
        self._price_entity = config[CONF_PRICE_ENTITY]
        self._state = None
        self.attr = {
            "energy entity": self._energy_entity,
            "price entity": self._price_entity,
        }
        self.entity_id = f"sensor.{self._name}".replace(" ", "_").lower()
        try:
            self._attr_unique_id = config[CONF_UNIQUE_ID]
        except:
            pass
        self._prices = {}
        self._energy = {}
        self._energy_total = {}

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self) -> Any:
        return self._state

    @property
    def extra_state_attributes(self):
        return self.attr

    async def async_update(self):
        """Updates the sensor"""
        now = dt.now()  # TODO: Check if this is UTC

        try:
            self._current_price = self.hass.states.get(self._price_entity).state
            self._current_energy = self.hass.states.get(self._energy_entity).state

            self._prices[now.hour] = self._current_price
            self._energy_total[now.hour] = self._current_energy

            if now.hour - 1 in self._energy_total:
                self._energy[now.hour] = (
                    self._current_energy - self._energy_total[now.hour - 1]
                )

            _LOGGER.debug(f"EnergyScore price update: {self._prices}")
            _LOGGER.debug(f"EnergyScore total energy update: {self._energy_total}")
            _LOGGER.debug(f"EnergyScore energy update: {self._energy}")

            self._last_updated = now.date()
            self._state = np.random.random() * 100
        except:
            _LOGGER.exception("Could not update the EnergyScore")


# TODO: Need to reset the dicts when new day somehow.
# if self._last_updated is None:
#    self._prices = {}
# elif self._last_updated.date() != now.date():
#    self._prices = {}
