"""Sensor platform for energyscore."""
import datetime
import logging
from typing import Any, Callable

from homeassistant.components.sensor import (
    PLATFORM_SCHEMA,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_NAME,
    CONF_UNIQUE_ID,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.util import dt
import numpy as np
import voluptuous as vol

from .const import (
    CONF_ENERGY_ENTITY,
    CONF_PRICE_ENTITY,
    CONF_ROLLING_HOURS,
    CONF_TRESHOLD,
    DOMAIN,
    ENERGY,
    ICON,
    ICON_COST,
    ICON_SAVINGS,
    LAST_UPDATED,
    PRICES,
    QUALITY,
)

_LOGGER: logging.Logger = logging.getLogger(__package__)

# Time between updating data
SCAN_INTERVAL = datetime.timedelta(minutes=10)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_ENERGY_ENTITY): cv.entity_id,
        vol.Required(CONF_PRICE_ENTITY): cv.entity_id,
        vol.Optional(CONF_UNIQUE_ID): cv.string,
        vol.Optional(CONF_TRESHOLD, default=0): vol.Coerce(float),
        vol.Optional(CONF_ROLLING_HOURS, default=24): vol.All(
            int, vol.Range(min=2, max=168)
        ),
    }
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities,
):
    """Setup sensors from a config entry created in the integrations UI"""

    # Reading the config from UI
    config = hass.data[DOMAIN][config_entry.entry_id]
    energy_treshold = config_entry.options.get(CONF_TRESHOLD)
    rolling_hours = config_entry.options.get(CONF_ROLLING_HOURS)
    _LOGGER.debug("Config: %s", config)
    _LOGGER.debug("Options: %s", config_entry.options)

    sensors = [
        EnergyScore(hass, config, energy_treshold, rolling_hours),
        Cost(config),
        PotentialSavings(config),
    ]
    async_add_entities(sensors, update_before_add=False)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up sensors from YAML config"""
    energy_treshold = config[CONF_TRESHOLD]
    rolling_hours = config[CONF_ROLLING_HOURS]
    _LOGGER.debug("Config: %s", config)
    async_add_entities(
        [EnergyScore(hass, config, energy_treshold, rolling_hours)],
        update_before_add=False,
    )


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
    """EnergyScore Sensor class"""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "%"

    def __init__(self, hass, config, energy_treshold, rolling_hours):
        self._attr_icon: str = ICON
        self._attr_unique_id = config.get(CONF_UNIQUE_ID)

        self._energy = None
        self._energy_entity = config[CONF_ENERGY_ENTITY]
        self.hass = hass  # TODO: needed?
        self._name = config[CONF_NAME]
        self._norm_energy = np.array(None)
        self._norm_prices = np.array(None)
        self._price = None
        self._price_entity = config[CONF_PRICE_ENTITY]
        self._rolling_hours = rolling_hours
        self._state = 100
        self._treshold = energy_treshold
        self.attr = {
            CONF_ENERGY_ENTITY: self._energy_entity,
            CONF_PRICE_ENTITY: self._price_entity,
            QUALITY: 0,
            ENERGY: {},
            PRICES: {},
            LAST_UPDATED: None,
        }

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info accosiated with the entity"""
        return DeviceInfo(
            identifiers={(DOMAIN, self._attr_unique_id)},
            name=self.name,
            manufacturer=DOMAIN,
        )

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
            for attribute in [ENERGY, PRICES, LAST_UPDATED, QUALITY]:
                if attribute in last_state.attributes:
                    self.attr[attribute] = last_state.attributes[attribute]
            _LOGGER.debug("Restored %s", self._name)
        else:
            _LOGGER.debug("Was not able to restore %s", self._name)

    def process_new_data(self):
        """Processes the update data"""
        now = dt.now().replace(
            minute=0, second=0, microsecond=0
        )  # TZ aware datetime obj based on user settings

        # Parse datetimes from strings
        for i in [ENERGY, PRICES]:
            self.attr[i] = {
                dt.parse_datetime(key): value
                for key, value in self.attr[i].items()
                if isinstance(key, str)
            }

        # Add new data, need to check declining energy first
        previous = now - datetime.timedelta(hours=1)
        if (
            previous in self.attr[ENERGY]
            and self.attr[ENERGY][previous] is not None
            and self._energy.state < self.attr[ENERGY][previous]
        ):
            _state_class = self._energy.attributes.get("state_class")
            _last_reset = self._energy.attributes.get("last_reset")
            if _last_reset is not None:
                _last_reset = dt.parse_datetime(_last_reset).replace(
                    minute=0, second=0, microsecond=0
                )

            # Check state classes:
            if _state_class == "total_increasing" or (
                _state_class == "total" and _last_reset is not None
            ):
                self.attr[ENERGY][now] = self._energy.state
            else:
                if _state_class == "total":
                    _warn_text = """, but there is no last_reset attribute to confirm that the sensor is expected to decline the value."""
                else:
                    _warn_text = """. Please change energy entity to a total/total_increasing, or fix the current energy entity state class."""
                _LOGGER.warning(
                    "%s - The energy entity's state class is %s%s",
                    self._name,
                    _state_class,
                    _warn_text,
                )
                self.attr[ENERGY][now] = None
        else:
            self.attr[ENERGY][now] = self._energy.state
        self.attr[PRICES][now] = self._price.state

        # Calculate energy data per hour from total:
        _energy_usage = {}
        for key, value in self.attr[ENERGY].items():
            previous = key - datetime.timedelta(hours=1)
            if previous in self.attr[ENERGY] and self.attr[ENERGY][key] is not None:

                # Check if the energy sensor is resetting
                if self.attr[ENERGY][previous] is None or (
                    value < self.attr[ENERGY][previous]
                ):
                    _energy_usage[key] = value
                else:
                    _energy_usage[key] = value - self.attr[ENERGY][previous]
            elif previous in self.attr[ENERGY] and self.attr[ENERGY][key] is not None:
                _energy_usage[key] = value

        # Remove all energy usage below treshold:
        _energy_usage = {k: v for k, v in _energy_usage.items() if v >= self._treshold}

        # Clean out old data:
        def cutoff(data: dict, hours: int) -> dict:
            """Cuts off old energy and price data"""
            cut_hours = now - datetime.timedelta(hours=hours)
            return {time: value for (time, value) in data.items() if time > cut_hours}

        _energy_usage = cutoff(_energy_usage, self._rolling_hours)
        self.attr[PRICES] = cutoff(self.attr[PRICES], self._rolling_hours)
        self.attr[ENERGY] = cutoff(self.attr[ENERGY], self._rolling_hours + 1)

        _LOGGER.debug(
            "%s - Calculated energy usage: %s",
            self._name,
            [round(val, 2) for key, val in _energy_usage.items()],
        )

        # Calculate quality and break out if applicable
        q = min(len(self.attr[PRICES]), len(_energy_usage)) / self._rolling_hours
        self.attr[QUALITY] = round(q, 2)
        _LOGGER.debug("%s - Quality: %s", self._name, self.attr[QUALITY])
        if self.attr[QUALITY] == 0 or len(set(self.attr[ENERGY].values())) == 1:
            _LOGGER.debug(
                "%s - Not able to calculate energy use in the last %s hours",
                self._name,
                self._rolling_hours,
            )
            # TODO: Check if it is actually possible to have quality = 0
            # and if so, should the return really be 100?
            return 100

        # Normalise and intersect the data
        _norm_prices = normalise_price(self.attr[PRICES])
        _norm_energies = normalise_energy(_energy_usage)
        _intersection = self.attr[PRICES].keys() & _energy_usage.keys()
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

            if self._price.state in [STATE_UNAVAILABLE, STATE_UNKNOWN]:
                _LOGGER.info("%s - Price data is %s", self._name, self._price.state)
                self._price = False
            if self._energy.state in [STATE_UNAVAILABLE, STATE_UNKNOWN]:
                _LOGGER.info("%s - Energy data is %s", self._name, self._energy.state)
                self._energy = False
            if not self._price or not self._energy:
                return

            self._price.state = round(float(self._price.state), 2)
            self._energy.state = round(float(self._energy.state), 2)

        except ValueError:
            _LOGGER.exception("%s - Possibly non-numeric source state", self._name)
        except Exception:
            _LOGGER.exception("%s - Could not fetch price and energy data", self._name)
        else:
            try:
                self._state = self.process_new_data()
            except Exception:
                _LOGGER.exception(
                    "%s - Could not process the updated data and produce the new EnergyScore",
                    self._name,
                )
            else:
                self.attr[LAST_UPDATED] = dt.now()

                # Datatimes needs to be converted to strings in state attributes
                self.attr[PRICES] = {
                    key.strftime("%Y-%m-%dT%H:%M:%S%z"): val
                    for key, val in self.attr[PRICES].items()
                }
                self.attr[ENERGY] = {
                    key.strftime("%Y-%m-%dT%H:%M:%S%z"): val
                    for key, val in self.attr[ENERGY].items()
                }


class Cost(SensorEntity):
    """Savings sensor class"""

    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    def __init__(self, config):
        self._attr_icon: str = ICON_COST
        self._attr_unique_id = f"{config.get(CONF_UNIQUE_ID)}_cost"

        self._energy_entity = config[CONF_ENERGY_ENTITY]
        self._name = f"{config[CONF_NAME]} Cost"
        self._price_entity = config[CONF_PRICE_ENTITY]
        self._state = 0
        self.attr = {QUALITY: 0}
        self.config = config
        self.energy_usage = None
        self.price = None

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info accosiated with the entity"""
        return DeviceInfo(
            identifiers={(DOMAIN, self.config.get(CONF_UNIQUE_ID))},
            name=self.config[CONF_NAME],
            manufacturer=DOMAIN,
        )

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

    async def async_update(self):
        """Updates the sensor"""

        _LOGGER.warning(" - - - The cost for %s are being updated - - -", self._name)

        self.price = self.hass.states.get(self._price_entity)
        self.energy_usage = self.hass.states.get(self._energy_entity)
        if not self.price or not self.energy_usage:
            return

        try:
            self._state = (
                self.price.state * self.energy_usage.state
            )  # denne er bare for første timen. Så skal den adderes.
        except ValueError:
            _LOGGER.exception(
                "%s - Possibly non-numeric source state when calculating price",
                self._name,
            )


class PotentialSavings(SensorEntity):
    """Savings sensor class"""

    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, config):
        self._attr_icon: str = ICON_SAVINGS
        self._attr_unique_id = f"{config.get(CONF_UNIQUE_ID)}_potential_savings"
        self._name = f"{config[CONF_NAME]} Potential Savings"
        self._state = 0
        self.config = config
        self.attr = {QUALITY: 0}

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info accosiated with the entity"""
        return DeviceInfo(
            identifiers={(DOMAIN, self.config.get(CONF_UNIQUE_ID))},
            name=self.config[CONF_NAME],
            manufacturer=DOMAIN,
        )

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

    async def async_update(self):
        """Updates the sensor"""
        _LOGGER.warning(" - - - The savings for %s are being updated - - -", self._name)
