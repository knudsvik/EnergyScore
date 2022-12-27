"""Sensor platform for energyscore."""
import datetime
from datetime import timedelta
import logging
from typing import Any, Callable

from homeassistant.components.sensor import (
    PLATFORM_SCHEMA,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import (
    CONF_NAME,
    CONF_UNIQUE_ID,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType, Optional
from homeassistant.util import dt
import numpy as np
import voluptuous as vol

from .const import (
    CONF_ENERGY_ENTITY,
    CONF_PRICE_ENTITY,
    ENERGY,
    ICON,
    LAST_UPDATED,
    PRICES,
    QUALITY,
)

_LOGGER: logging.Logger = logging.getLogger(__package__)

# Time between updating data
SCAN_INTERVAL = timedelta(minutes=10)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_ENERGY_ENTITY): cv.entity_id,
        vol.Required(CONF_PRICE_ENTITY): cv.entity_id,
        vol.Required(CONF_UNIQUE_ID): cv.string,
    }
)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    """Set up the sensors from YAML config"""
    async_add_entities([EnergyScore(hass, config)], update_before_add=False)


def normalise_price(price_dict) -> dict:
    """Normalises price dict"""
    if price_dict == {}:
        return {}
    max_value = max(price_dict.values())
    min_value = min(price_dict.values())
    if max_value == min_value:
        return {key: 1 for key, value in price_dict.items()}
    return {
        key: (max_value - value) / (max_value - min_value)
        for key, value in price_dict.items()
    }


def normalise_energy(energy_dict) -> dict:
    """Normalises energy dict to sum up to 1"""
    if energy_dict == {}:
        return {}
    sum_values = sum(energy_dict.values())
    return {key: value / sum_values for key, value in energy_dict.items()}


class EnergyScore(SensorEntity, RestoreEntity):
    """EnergyScore Sensor class."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "%"

    def __init__(self, hass, config):
        self._attr_icon: str = ICON
        self._attr_unique_id = config[CONF_UNIQUE_ID]
        self._energy = None
        self._energy_entity = config[CONF_ENERGY_ENTITY]
        self._name = config[CONF_NAME]
        self._nordpool = None
        self._norm_energy = np.array(None)
        self._norm_prices = np.array(None)
        self._price = None
        self._price_entity = config[CONF_PRICE_ENTITY]
        self._rolling_hours = 24
        self._state = 100
        self.attr = {
            CONF_ENERGY_ENTITY: self._energy_entity,
            CONF_PRICE_ENTITY: self._price_entity,
            QUALITY: 0,
            ENERGY: {},
            PRICES: {},
            LAST_UPDATED: None,
        }

        self.hass = hass

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self) -> Any:
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        return self.attr

    async def async_added_to_hass(self) -> None:
        """ "Restore last state." """
        _LOGGER.debug("Trying to restore: %s", self._name)
        await super().async_added_to_hass()
        if (
            last_state := await self.async_get_last_state()
        ) and last_state.state not in (STATE_UNKNOWN, STATE_UNAVAILABLE):
            self._state = last_state.state

            for attribute in [ENERGY, PRICES]:
                if attribute in last_state.attributes:
                    att = last_state.attributes[attribute]
                    self.attr[attribute] = {
                        dt.parse_datetime(key): value for key, value in att.items()
                    }
            if LAST_UPDATED in last_state.attributes:
                self.attr[LAST_UPDATED] = dt.parse_datetime(
                    last_state.attributes[LAST_UPDATED]
                )
            if QUALITY in last_state.attributes:
                self.attr[QUALITY] = last_state.attributes[QUALITY]

            _LOGGER.debug("Restored %s", self._name)
        else:
            _LOGGER.debug("Was not able to restore %s", self._name)

    def process_new_data(self):
        """Processes the update data"""
        now = dt.now().replace(
            minute=0, second=0, microsecond=0
        )  # TZ aware based on user settings

        # Add new data:
        self.attr[ENERGY][now] = self._energy.state
        self.attr[PRICES][now] = self._price.state

        # Clean out old data:
        cutoff = now - timedelta(hours=self._rolling_hours)
        self.attr[PRICES] = {
            time: value for (time, value) in self.attr[PRICES].items() if time > cutoff
        }
        self.attr[ENERGY] = {
            time: value for (time, value) in self.attr[ENERGY].items() if time > cutoff
        }

        # Calculate quality and break out if applicable
        q = min(len(self.attr[PRICES]), len(self.attr[ENERGY])) / self._rolling_hours
        self.attr[QUALITY] = round(q, 2)
        _LOGGER.debug("%s - Quality: %s", self._name, self.attr[QUALITY])
        if self.attr[QUALITY] == 0 or len(set(self.attr[ENERGY].values())) == 1:
            _LOGGER.debug(
                "%s - No energy use in the last %s hours",
                self._name,
                self._rolling_hours,
            )
            # TODO: Check if it is actually possible to have quality = 0
            # and if so, should the return really be 100?
            return 100

        # Calculate energy data per hour from total:
        _energy_usage = {}
        for key, value in self.attr[ENERGY].items():
            if key - datetime.timedelta(hours=1) in self.attr[ENERGY]:
                _energy_usage[key] = (
                    value - self.attr[ENERGY][key - datetime.timedelta(hours=1)]
                )
        _LOGGER.debug(
            "%s - Calc. energy usage: %s", self._name, np.round(_energy_usage, 2)
        )

        # Normalise and intersect the data
        _norm_prices = normalise_price(self.attr[PRICES])
        _norm_energies = normalise_energy(_energy_usage)
        _intersection = _norm_prices.keys() & _norm_energies.keys()
        _price_array = np.array([_norm_prices[x] for x in _intersection])
        _energy_array = np.array([_norm_energies[x] for x in _intersection])
        _LOGGER.debug("%s - Norm prices: %s", self._name, np.round(_price_array, 2))
        _LOGGER.debug("%s - Norm energy: %s", self._name, np.round(_energy_array, 2))

        # Calculate the energyscore
        _score = np.dot(_price_array, _energy_array)
        _LOGGER.debug("%s - Score: %s", self._name, _score)

        return int(_score * 100)

    async def async_update(self):
        """Updates the sensor"""
        try:
            self._price = self.hass.states.get(self._price_entity)
            self._energy = self.hass.states.get(self._energy_entity)

            if self._price.state in (
                STATE_UNAVAILABLE,
                STATE_UNKNOWN,
            ) or self._energy.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
                _LOGGER.info("%s - Price and/or energy data is unavailable", self._name)
                return
            else:
                self._price.state = round(float(self._price.state), 2)
                self._energy.state = round(float(self._energy.state), 2)

        except:
            _LOGGER.exception("%s - Could not fetch price and energy data", self._name)
        else:
            try:
                self._state = self.process_new_data()
            except:
                _LOGGER.exception(
                    "%s - Could not process the updated data and produce the new EnergyScore",
                    self._name,
                )
            else:
                self.attr[LAST_UPDATED] = dt.now()
