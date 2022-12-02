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
        self._energy_total = {}
        self._name = config[CONF_NAME]
        self._energy_entity = config[CONF_ENERGY_ENTITY]
        self._last_updated = None
        self._price_entity = config[CONF_PRICE_ENTITY]
        self._quality = None
        self._state = None
        self._yesterday_energy = None
        self.attr = {
            "energy entity": self._energy_entity,
            "price entity": self._price_entity,
            "quality": self._quality,
        }
        self.entity_id = f"sensor.{self._name}".replace(" ", "_").lower()
        try:
            self._attr_unique_id = config[CONF_UNIQUE_ID]
        except:
            pass

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
        now = dt.now()
        if self._last_updated != now.date():
            self._prices = {}
            self._energy = {}
            if self._last_updated == now.date() - datetime.timedelta(1):
                self._yesterday_energy = max(self._energy_total.values())
            self._energy_total = {}

        try:
            self._current_price = round(
                float(self.hass.states.get(self._price_entity).state), 2
            )
            self._current_energy = round(
                float(self.hass.states.get(self._energy_entity).state), 2
            )

            self._prices[int(now.hour)] = self._current_price
            self._energy_total[int(now.hour)] = self._current_energy

            if (int(now.hour) - int(1)) in self._energy_total:
                self._energy[now.hour] = round(
                    (self._current_energy - self._energy_total[int(now.hour) - 1]), 2
                )
            elif self._yesterday_energy != None:
                self._energy[now.hour] = self._current_energy - self._yesterday_energy

            _LOGGER.debug(f"Price update: {self._prices}")
            _LOGGER.debug(f"Energy update: {self._energy}")
            _LOGGER.debug(f"Total energy update: {self._energy_total}")

            self._last_updated = now.date()
            self._quality = (len(self._prices) + len(self._energy)) / 2 / int(now.hour)

            self._price_array = np.array(list(self._prices.values()))
            self._energy_array = np.array(list(self._energy.values()))
            self._norm_prices = (self._price_array.max() - self._price_array) / (
                self._price_array.max() - self._price_array.min()
            )
            self._norm_energy = self._energy_array / self._energy_array.sum()

            _LOGGER.debug(f"Normalised prices: {self.__norm_prices}")
            _LOGGER.debug(f"Normalised energy: {self._norm_energy}")

            self._state = round(np.dot(self._norm_prices, self._norm_energy), 1)
        except:
            _LOGGER.exception("Could not update the EnergyScore")
