from datetime import timedelta

from homeassistant.components import sensor
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from homeassistant.util import dt
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from custom_components.energyscore.sensor import normalise_energy, normalise_price

from .common import create_energyscore_sensor
from .const import EMPTY_DICT, ENERGY_DICT, PRICE_DICT, SAME_PRICE_DICT, VALID_CONFIG


async def test_new_config(hass: HomeAssistant):
    """Testing a default setup of an energyscore sensor"""
    await create_energyscore_sensor(hass)

    state = hass.states.get("sensor.my_mock_es")
    assert state.state == "100"
    assert state.attributes.get("unit_of_measurement") == "%"
    assert state.attributes.get("state_class") == sensor.SensorStateClass.MEASUREMENT
    assert state.attributes.get("energy_entity") == VALID_CONFIG["energy_entity"]
    assert state.attributes.get("price_entity") == VALID_CONFIG["price_entity"]
    assert state.attributes.get("quality") == 0
    assert state.attributes.get("energy") == {}
    assert state.attributes.get("price") == {}
    assert state.attributes.get("last_updated") == None
    assert state.attributes.get("unit_of_measurement") == "%"
    assert state.attributes.get("icon") == "mdi:speedometer"
    assert state.attributes.get("friendly_name") == "My Mock ES"


def test_normalisation():
    """Test the normalisation function"""
    assert normalise_price(PRICE_DICT[0]) == PRICE_DICT[1]
    assert normalise_price(EMPTY_DICT[0]) == EMPTY_DICT[1]
    assert normalise_price(SAME_PRICE_DICT[0]) == SAME_PRICE_DICT[1]
    assert normalise_energy(ENERGY_DICT[0]) == ENERGY_DICT[1]
    assert normalise_energy(EMPTY_DICT[0]) == EMPTY_DICT[1]


async def test_update_sensor(hass: HomeAssistant) -> None:
    """Test based on the min max sensor"""

    config = {
        "sensor": {
            "platform": "energyscore",
            "name": "My Mock ES",
            "energy_entity": "sensor.energy",
            "price_entity": "sensor.electricity_price",
            "unique_id": "CA0C3E3-38D3-4A79-91CC-1291dwAA3828",
        }
    }

    assert await async_setup_component(hass, "sensor", config)
    await hass.async_block_till_done()

    hass.states.async_set("sensor.energy", 2.39)
    hass.states.async_set("sensor.electricity_price", 0.99)
    await hass.async_block_till_done()

    async_fire_time_changed(hass, dt.now() + timedelta(minutes=11))
    await hass.async_block_till_done()

    state = hass.states.get("sensor.my_mock_es")
    print(state)
