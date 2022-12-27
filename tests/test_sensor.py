import datetime

from freezegun import freeze_time
from homeassistant.components import sensor
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from homeassistant.util import dt
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from custom_components.energyscore.const import QUALITY
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
    assert state.attributes.get("last_updated") is None
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

    initial_datetime = dt.parse_datetime("2022-09-18 21:08:44+01:00")
    config = {
        "sensor": {
            "platform": "energyscore",
            "name": "My Mock ES",
            "energy_entity": "sensor.energy",
            "price_entity": "sensor.electricity_price",
            "unique_id": "CA0C3E3-38D3-4A79-91CC-1291dwAA3828",
        }
    }

    STATES = [100, 100, 42]
    QUALITIES = [0.04, 0.08, 0.12]
    ENERGY = [122.39, 124.49, 127.32]
    PRICE = [0.99, 0.78, 1.54]

    with freeze_time(initial_datetime) as frozen_datetime:
        assert await async_setup_component(hass, "sensor", config)
        await hass.async_block_till_done()

        for hour in range(0, 3):
            hass.states.async_set("sensor.energy", ENERGY[hour])
            hass.states.async_set("sensor.electricity_price", PRICE[hour])
            async_fire_time_changed(hass, dt.now() + datetime.timedelta(minutes=10))
            await hass.async_block_till_done()
            state = hass.states.get("sensor.my_mock_es")
            assert state.state == str(STATES[hour])
            assert state.attributes[QUALITY] == QUALITIES[hour]
            frozen_datetime.tick(delta=datetime.timedelta(hours=1))

        # Check that old data is purged:
        assert "2022-09-18T13:00:00-0700" in state.attributes.get("energy")
        frozen_datetime.tick(delta=datetime.timedelta(hours=21))
        hass.states.async_set("sensor.energy", 178.3)
        hass.states.async_set("sensor.electricity_price", 1.32)
        async_fire_time_changed(hass, dt.now() + datetime.timedelta(minutes=10))
        await hass.async_block_till_done()
        state = hass.states.get("sensor.my_mock_es")
        assert "2022-09-18T13:00:00-0700" not in state.attributes.get("energy")
        print("----- s t a t e", state)
