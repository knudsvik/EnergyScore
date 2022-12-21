from homeassistant.const import CONF_NAME, CONF_PLATFORM, CONF_UNIQUE_ID
from homeassistant.helpers import entity_registry as er
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import mock_registry

from custom_components.energyscore.const import (
    CONF_ENERGY_ENTITY,
    CONF_PRICE_ENTITY,
    DOMAIN,
)
from custom_components.energyscore.sensor import normalise_price, normalise_energy
from .const import PRICE_DICT, ENERGY_DICT, EMPTY_DICT


async def test_config(hass):
    """Test EnergyScore config."""
    config = {
        "sensor": {
            CONF_PLATFORM: DOMAIN,
            CONF_NAME: "My Mock ES",
            CONF_ENERGY_ENTITY: "sensor.energy",
            CONF_PRICE_ENTITY: "sensor.electricity_price",
            CONF_UNIQUE_ID: "CA0C3E3-38D3-4A79-91CC-129121AA3828",
        }
    }

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

    # registry = er.async_get(hass)
    # assert registry.async_get("sensor.electricity_price").platform == "nordpool"

    assert await async_setup_component(hass, "sensor", config)
    # Can not change "sensor" with "energyscore" over here for some reason. That also means
    # I cannot assert "energyscore" in hass.config.components.

    await hass.async_block_till_done()


def test_normalisation():
    """Test the normalisation function"""
    assert normalise_price(PRICE_DICT[0]) == PRICE_DICT[1]
    assert normalise_price(EMPTY_DICT[0]) == EMPTY_DICT[1]
    assert normalise_energy(ENERGY_DICT[0]) == ENERGY_DICT[1]
    assert normalise_energy(EMPTY_DICT[0]) == EMPTY_DICT[1]
