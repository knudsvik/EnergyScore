"""Common functions for helping test functions"""
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import mock_registry
from homeassistant.helpers import entity_registry as er
from homeassistant.setup import async_setup_component
from homeassistant.components import sensor
from .const import VALID_CONFIG


async def create_energyscore_sensor(hass: HomeAssistant):
    """Creates a general purpose energyscore sensor"""

    # Setting up a registry entry to pass a (nordpool) electricity_price sensor to the EnergyScore sensor.
    mock_registry(
        hass,
        {
            "sensor.electricity_price": er.RegistryEntry(
                entity_id="sensor.electricity_price",
                unique_id="1234",
                platform="nordpool",
                name="Hello World",
            ),
        },
    )

    registry = er.async_get(hass)
    assert registry.async_get("sensor.electricity_price").platform == "nordpool"

    assert await async_setup_component(hass, sensor.DOMAIN, {"sensor": VALID_CONFIG})
    await hass.async_block_till_done()
