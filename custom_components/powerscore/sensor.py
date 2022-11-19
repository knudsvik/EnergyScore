"""Sensor platform for integration_blueprint."""
from homeassistant.components.sensor import SensorEntity

from .const import DEFAULT_NAME, DOMAIN, ICON, SENSOR
from .entity import IntegrationBlueprintEntity


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices([PowerScore(coordinator, entry)])


class PowerScore(IntegrationBlueprintEntity, SensorEntity):
    """PowerScore Sensor class."""

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{DEFAULT_NAME}_{SENSOR}"

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        # return self.coordinator.data.get("body")
        return 42

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
