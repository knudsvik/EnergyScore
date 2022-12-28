import datetime

from freezegun import freeze_time
from homeassistant.components import sensor
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from homeassistant.util import dt
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from custom_components.energyscore.const import QUALITY
from custom_components.energyscore.sensor import (
    SCAN_INTERVAL,
    normalise_energy,
    normalise_price,
)

from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN

from .const import EMPTY_DICT, ENERGY_DICT, PRICE_DICT, SAME_PRICE_DICT, VALID_CONFIG


async def test_new_config(hass: HomeAssistant) -> None:
    """Testing a default setup of an energyscore sensor"""
    assert await async_setup_component(hass, "sensor", VALID_CONFIG)
    await hass.async_block_till_done()

    state = hass.states.get("sensor.my_mock_es")
    assert state.state == "100"
    assert state.attributes.get("unit_of_measurement") == "%"
    assert state.attributes.get("state_class") == sensor.SensorStateClass.MEASUREMENT
    assert state.attributes.get("energy_entity") == "sensor.energy"
    assert state.attributes.get("price_entity") == "sensor.electricity_price"
    assert state.attributes.get("quality") == 0
    assert state.attributes.get("total_energy") == {}
    assert state.attributes.get("price") == {}
    assert state.attributes.get("last_updated") is None
    assert state.attributes.get("unit_of_measurement") == "%"
    assert state.attributes.get("icon") == "mdi:speedometer"
    assert state.attributes.get("friendly_name") == "My Mock ES"


def test_normalisation() -> None:
    """Test the normalisation function"""
    assert normalise_price(PRICE_DICT[0]) == PRICE_DICT[1]
    assert normalise_price(EMPTY_DICT[0]) == EMPTY_DICT[1]
    assert normalise_price(SAME_PRICE_DICT[0]) == SAME_PRICE_DICT[1]
    assert normalise_energy(ENERGY_DICT[0]) == ENERGY_DICT[1]
    assert normalise_energy(EMPTY_DICT[0]) == EMPTY_DICT[1]


async def test_update_sensor(hass: HomeAssistant, caplog) -> None:
    """Test the update of energyscore by moving time"""

    initial_datetime = dt.parse_datetime("2022-09-18 21:08:44+01:00")

    STATES = [100, 100, 42]
    QUALITIES = [0.04, 0.08, 0.12]
    ENERGY = [122.39, 124.49, 127.32]
    PRICE = [0.99, 0.78, 1.54]

    with freeze_time(initial_datetime) as frozen_datetime:
        assert await async_setup_component(hass, "sensor", VALID_CONFIG)
        await hass.async_block_till_done()

        for hour in range(0, 3):
            hass.states.async_set("sensor.energy", ENERGY[hour])
            hass.states.async_set("sensor.electricity_price", PRICE[hour])
            async_fire_time_changed(hass, dt.now() + SCAN_INTERVAL)
            await hass.async_block_till_done()
            state = hass.states.get("sensor.my_mock_es")
            assert state.state == str(STATES[hour])
            assert state.attributes[QUALITY] == QUALITIES[hour]
            if hour == 0:
                assert "My Mock ES - No energy use in the last 24 hours" in caplog.text
            frozen_datetime.tick(delta=datetime.timedelta(hours=1))

        # Check that old data is purged:
        assert "2022-09-18T13:00:00-0700" in state.attributes.get("total_energy")
        assert "2022-09-18T13:00:00-0700" in state.attributes.get("price")
        frozen_datetime.tick(delta=datetime.timedelta(hours=21))
        hass.states.async_set("sensor.energy", 178.3)
        hass.states.async_set("sensor.electricity_price", 1.32)
        async_fire_time_changed(hass, dt.now() + SCAN_INTERVAL)
        await hass.async_block_till_done()
        state = hass.states.get("sensor.my_mock_es")
        assert "2022-09-18T13:00:00-0700" not in state.attributes.get("total_energy")
        assert "2022-09-18T13:00:00-0700" not in state.attributes.get("price")


async def test_unavailable_sources(hass: HomeAssistant, caplog) -> None:
    """Testing unavailable or unknown price or energy sensors"""
    assert await async_setup_component(hass, "sensor", VALID_CONFIG)
    await hass.async_block_till_done()

    for state in [STATE_UNAVAILABLE, STATE_UNKNOWN]:
        hass.states.async_set("sensor.energy", 24321.4)
        hass.states.async_set("sensor.electricity_price", state)
        async_fire_time_changed(hass, dt.now() + SCAN_INTERVAL)
        await hass.async_block_till_done()
        assert f"My Mock ES - Price data is {state}" in caplog.text

        hass.states.async_set("sensor.energy", state)
        hass.states.async_set("sensor.electricity_price", 0.42)
        async_fire_time_changed(hass, dt.now() + SCAN_INTERVAL)
        await hass.async_block_till_done()
        assert f"My Mock ES - Energy data is {state}" in caplog.text


async def test_both_sources_unavailable(hass: HomeAssistant, caplog) -> None:
    """Testing if both sources are unavailable or unknown (new caplog)"""
    assert await async_setup_component(hass, "sensor", VALID_CONFIG)
    await hass.async_block_till_done()

    for state in [STATE_UNAVAILABLE, STATE_UNKNOWN]:
        hass.states.async_set("sensor.energy", state)
        hass.states.async_set("sensor.electricity_price", state)
        async_fire_time_changed(hass, dt.now() + SCAN_INTERVAL)
        await hass.async_block_till_done()
        assert f"My Mock ES - Energy data is {state}" in caplog.text
        assert f"My Mock ES - Price data is {state}" in caplog.text


async def test_no_sources(hass: HomeAssistant, caplog) -> None:
    """Testing to catch no source excpetion"""
    assert await async_setup_component(hass, "sensor", VALID_CONFIG)
    await hass.async_block_till_done()
    async_fire_time_changed(hass, dt.now() + SCAN_INTERVAL)
    await hass.async_block_till_done()
    assert "My Mock ES - Could not fetch price and energy data" in caplog.text


async def test_non_numeric_source_state(hass: HomeAssistant, caplog) -> None:
    """Testing to catch non-numeric excpetion"""
    assert await async_setup_component(hass, "sensor", VALID_CONFIG)
    await hass.async_block_till_done()
    hass.states.async_set("sensor.energy", 123.4)
    hass.states.async_set("sensor.electricity_price", "text")
    await hass.async_block_till_done()
    async_fire_time_changed(hass, dt.now() + SCAN_INTERVAL)
    await hass.async_block_till_done()
    assert "My Mock ES - Possibly non-numeric source state" in caplog.text
