"""
Sensor tests for EnergyScore
"""

import copy
import datetime
import pytest

from freezegun import freeze_time
from homeassistant.components import sensor
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import HomeAssistant, State
import homeassistant.helpers.entity_registry as er
from homeassistant.helpers.restore_state import (
    DATA_RESTORE_STATE_TASK,
    RestoreStateData,
    StoredState,
)
from homeassistant.setup import async_setup_component
from homeassistant.util import dt
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from custom_components.energyscore.const import QUALITY, PRICES, ENERGY
from custom_components.energyscore.sensor import (
    SCAN_INTERVAL,
    normalise_energy,
    normalise_price,
)

from .const import (
    EMPTY_DICT,
    ENERGY_DICT,
    PRICE_DICT,
    SAME_PRICE_DICT,
    VALID_CONFIG,
    ENERGY_LIST,
)


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


async def test_unique_id(hass: HomeAssistant) -> None:
    """Testing a default setup with unique_id"""

    CONFIG = copy.deepcopy(VALID_CONFIG)
    CONFIG["sensor"]["unique_id"] = "Testing123"

    assert await async_setup_component(hass, "sensor", CONFIG)
    await hass.async_block_till_done()

    entity_reg = er.async_get(hass)
    assert entity_reg.async_get("sensor.my_mock_es").unique_id == "Testing123"


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
    QUALITIES = [0, 0.04, 0.08]
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
                assert (
                    "My Mock ES - Not able to calculate energy use in the last 24 hours"
                    in caplog.text
                )
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
        assert "2022-09-18T13:00:00-0700" not in state.attributes.get("price")
        # 1 extra hour of energy data is kept to be able to calculate energy usage
        frozen_datetime.tick(delta=datetime.timedelta(hours=1))
        hass.states.async_set("sensor.energy", 190)
        hass.states.async_set("sensor.electricity_price", 1)
        async_fire_time_changed(hass, dt.now() + SCAN_INTERVAL)
        await hass.async_block_till_done()
        state = hass.states.get("sensor.my_mock_es")
        assert "2022-09-18T13:00:00-0700" not in state.attributes.get("total_energy")


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


async def test_restore(hass: HomeAssistant, caplog) -> None:
    """Testing restoring sensor state and attributes
    Inspired by code in core/tests/helpers/test_restore_state.py
    """
    stored_state = StoredState(
        State(
            "sensor.my_mock_es",
            38,
            attributes={
                "energy_entity": "sensor.restored_energy",
                "price_entity": "sensor.restored_price",
                "quality": 0.12,
                "total_energy": {"2022-09-18T13:00:00-0700": 122.39},
                "price": {"2022-09-18T13:00:00-0700": 0.99},
                "icon": "mdi:home-assistant",
                "friendly_name": "New fancy name",
                "last_updated": "2020-12-01T20:50:53.131803+01:00",
            },
        ),
        None,
        dt.now(),
    )

    data = await RestoreStateData.async_get_instance(hass)
    await hass.async_block_till_done()
    await data.store.async_save([stored_state.as_dict()])

    # Emulate a fresh load
    hass.data.pop(DATA_RESTORE_STATE_TASK)

    assert await async_setup_component(hass, "sensor", VALID_CONFIG)
    await hass.async_block_till_done()
    assert "Restored My Mock ES" in caplog.text

    # Assert restored data
    state = hass.states.get("sensor.my_mock_es")
    assert state.state == "38"
    assert state.attributes.get("quality") == 0.12
    assert state.attributes.get("total_energy") == {"2022-09-18T13:00:00-0700": 122.39}
    assert state.attributes.get("price") == {"2022-09-18T13:00:00-0700": 0.99}
    assert state.attributes.get("last_updated") == "2020-12-01T20:50:53.131803+01:00"

    # Following attributes are saved, but not restored, so should still be the default
    assert state.attributes.get("energy_entity") == "sensor.energy"
    assert state.attributes.get("price_entity") == "sensor.electricity_price"
    assert state.attributes.get("friendly_name") == "My Mock ES"
    assert state.attributes.get("icon") == "mdi:speedometer"


async def test_declining_energy_unsupported_state_classes(hass, caplog):
    """Testing that energyscore handles energy sensors that declines with unsupported state classes"""

    initial_datetime = dt.parse_datetime("2021-12-31 22:08:44-08:00")

    with freeze_time(initial_datetime) as frozen_datetime:
        assert await async_setup_component(hass, "sensor", VALID_CONFIG)
        await hass.async_block_till_done()

        # Initial update
        hass.states.async_set("sensor.electricity_price", 1.2)
        hass.states.async_set("sensor.energy", 30)
        async_fire_time_changed(hass, dt.now() + SCAN_INTERVAL)
        await hass.async_block_till_done()

        # Advance the time by one hour to get first score, ready for next hour
        frozen_datetime.tick(delta=datetime.timedelta(hours=1))
        hass.states.async_set("sensor.energy", 32)
        hass.states.async_set("sensor.electricity_price", 1.6)
        async_fire_time_changed(hass, dt.now() + SCAN_INTERVAL)
        await hass.async_block_till_done()
        state = hass.states.get("sensor.my_mock_es")
        assert state.state == "0"  # Intersection in most expensive hour
        assert state.attributes.get("quality") == 0.04
        frozen_datetime.tick(delta=datetime.timedelta(hours=1))

        # Case state_class measurement
        hass.states.async_set(
            "sensor.energy",
            2.2,
            attributes={
                "state_class": sensor.SensorStateClass.MEASUREMENT,
            },
        )
        hass.states.async_set("sensor.electricity_price", 2.6)
        async_fire_time_changed(hass, dt.now() + SCAN_INTERVAL)
        await hass.async_block_till_done()
        state = hass.states.get("sensor.my_mock_es")
        assert state.state == "71"
        assert state.attributes.get("quality") == 0.04
        assert (
            "My Mock ES - The energy entity's state class is measurement. Please change energy entity to a total/total_increasing, or fix the current energy entity state class."
            in caplog.text
        )
        frozen_datetime.tick(delta=datetime.timedelta(hours=1))

        # Case state_class None, adding a fresh hour first (last was None)
        hass.states.async_set("sensor.energy", 1.8)
        async_fire_time_changed(hass, dt.now() + SCAN_INTERVAL)
        await hass.async_block_till_done()
        state = hass.states.get("sensor.my_mock_es")
        assert state.state == "37"
        frozen_datetime.tick(delta=datetime.timedelta(hours=1))

        hass.states.async_set("sensor.energy", 1.6)
        async_fire_time_changed(hass, dt.now() + SCAN_INTERVAL)
        await hass.async_block_till_done()
        state = hass.states.get("sensor.my_mock_es")
        assert state.state == "37"
        assert state.attributes.get("quality") == 0.08
        assert (
            "My Mock ES - The energy entity's state class is None. Please change energy entity to a total/total_increasing, or fix the current energy entity state class."
            in caplog.text
        )
        frozen_datetime.tick(delta=datetime.timedelta(hours=1))

        # Case state_class total but no reset
        # Adding a couple of fresh hours first (last was None)
        hass.states.async_set("sensor.electricity_price", 0.18)
        hour = 0
        while True:
            hass.states.async_set("sensor.energy", 10.12 + hour)
            async_fire_time_changed(hass, dt.now() + SCAN_INTERVAL)
            await hass.async_block_till_done()
            frozen_datetime.tick(delta=datetime.timedelta(hours=1))
            hour += 1
            if hour == 2:
                break
        state = hass.states.get("sensor.my_mock_es")
        assert state.attributes.get("quality") == 0.17
        assert state.state == "80"
        # Now with total state_class but no reset
        hass.states.async_set(
            "sensor.energy",
            2.2,
            attributes={
                "state_class": sensor.SensorStateClass.TOTAL,
            },
        )
        async_fire_time_changed(hass, dt.now() + SCAN_INTERVAL)
        await hass.async_block_till_done()
        state = hass.states.get("sensor.my_mock_es")
        assert state.state == "80"
        assert state.attributes.get("quality") == 0.17
        assert (
            "My Mock ES - The energy entity's state class is total, but there is no last_reset attribute to confirm that the sensor is expected to decline the value."
            in caplog.text
        )


async def test_declining_energy_supported_state_classes(hass):
    """Testing that energyscore handles energy sensors that declines with supported state_classes"""

    initial_datetime = dt.parse_datetime("2021-12-31 22:08:44-08:00")

    with freeze_time(initial_datetime) as frozen_datetime:
        assert await async_setup_component(hass, "sensor", VALID_CONFIG)
        await hass.async_block_till_done()

        # Initial update
        hass.states.async_set("sensor.electricity_price", 1.2)
        hass.states.async_set("sensor.energy", 30)
        async_fire_time_changed(hass, dt.now() + SCAN_INTERVAL)
        await hass.async_block_till_done()

        # Advance the time by one hour to get first score, ready for next hour
        frozen_datetime.tick(delta=datetime.timedelta(hours=1))
        hass.states.async_set("sensor.energy", 32)
        hass.states.async_set("sensor.electricity_price", 1.6)
        async_fire_time_changed(hass, dt.now() + SCAN_INTERVAL)
        await hass.async_block_till_done()
        state = hass.states.get("sensor.my_mock_es")
        assert state.state == "0"  # Intersection in most expensive hour
        assert state.attributes.get("quality") == 0.04
        frozen_datetime.tick(delta=datetime.timedelta(hours=1))

        # Case state_class: total_increasing
        hass.states.async_set("sensor.electricity_price", 1.4)
        hass.states.async_set(
            "sensor.energy",
            3.2,
            attributes={"state_class": sensor.SensorStateClass.TOTAL_INCREASING},
        )
        async_fire_time_changed(hass, dt.now() + SCAN_INTERVAL)
        await hass.async_block_till_done()
        state = hass.states.get("sensor.my_mock_es")
        assert state.state == "30"
        frozen_datetime.tick(delta=datetime.timedelta(hours=1))

        # Case state_class: total and last_reset
        hass.states.async_set(
            "sensor.energy",
            0.8,
            attributes={
                "state_class": sensor.SensorStateClass.TOTAL,
                "last_reset": "2022-01-01 00:00:53-08:00",
            },
        )
        async_fire_time_changed(hass, dt.now() + SCAN_INTERVAL)
        await hass.async_block_till_done()
        state = hass.states.get("sensor.my_mock_es")
        assert state.state == "33"


async def test_quality(hass: HomeAssistant) -> None:
    """Test that the quality attribute is behaving correctly"""

    initial_datetime = dt.parse_datetime("2022-09-18 21:08:44+01:00")

    with freeze_time(initial_datetime) as frozen_datetime:
        assert await async_setup_component(hass, "sensor", VALID_CONFIG)
        await hass.async_block_till_done()

        for hour in range(1, 27):
            hass.states.async_set("sensor.energy", hour**2)
            hass.states.async_set("sensor.electricity_price", 1 / hour)
            async_fire_time_changed(hass, dt.now() + SCAN_INTERVAL)
            await hass.async_block_till_done()
            state = hass.states.get("sensor.my_mock_es")
            if hour >= 25:
                assert state.attributes[QUALITY] == 1
            else:
                assert state.attributes[QUALITY] == round((hour - 1) / 24, 2)
            frozen_datetime.tick(delta=datetime.timedelta(hours=1))

        # Advance 10 minute slots to verify all parts of an hour:
        for part_hour in range(1, 6):
            frozen_datetime.tick(delta=datetime.timedelta(minutes=10))
            hass.states.async_set("sensor.energy", 700 + part_hour)
            hass.states.async_set("sensor.electricity_price", part_hour)
            async_fire_time_changed(hass, dt.now() + SCAN_INTERVAL)
            await hass.async_block_till_done()
            state = hass.states.get("sensor.my_mock_es")
            assert state.attributes[QUALITY] == 1


async def test_energy_treshold(hass: HomeAssistant) -> None:
    """Test that the treshold function is working as intended"""

    CONFIG = copy.deepcopy(VALID_CONFIG)
    CONFIG["sensor"]["energy_treshold"] = 0.8

    energy = [1, 2, 3, 3.4, 3.5, 3.7, 4.1]

    initial_datetime = dt.parse_datetime("2022-09-18 21:08:44+01:00")
    with freeze_time(initial_datetime) as frozen_datetime:
        assert await async_setup_component(hass, "sensor", CONFIG)
        await hass.async_block_till_done()

        for hour in range(0, 7):
            hass.states.async_set("sensor.energy", energy[hour])
            hass.states.async_set("sensor.electricity_price", hour)
            async_fire_time_changed(hass, dt.now() + SCAN_INTERVAL)
            await hass.async_block_till_done()
            frozen_datetime.tick(delta=datetime.timedelta(hours=1))

        state = hass.states.get("sensor.my_mock_es")
        assert state.state == "75"
        assert state.attributes[QUALITY] == 0.08


rolling_parameters = [(2, 5, 79), (4, 5, 72), (37, 40, 33)]


@pytest.mark.parametrize("rolling_hours, hours, score", rolling_parameters)
async def test_rolling_hours(hass: HomeAssistant, rolling_hours, hours, score) -> None:
    """Test that the rolling hours functiton is working as intended"""

    CONFIG = copy.deepcopy(VALID_CONFIG)
    CONFIG["sensor"]["rolling_hours"] = rolling_hours

    initial_datetime = dt.parse_datetime("2022-09-18 21:08:44+01:00")
    with freeze_time(initial_datetime) as frozen_datetime:
        assert await async_setup_component(hass, "sensor", CONFIG)
        await hass.async_block_till_done()

        for hour in range(0, hours):
            hass.states.async_set("sensor.energy", ENERGY_LIST[hour])
            hass.states.async_set("sensor.electricity_price", hour)
            async_fire_time_changed(hass, dt.now() + SCAN_INTERVAL)
            await hass.async_block_till_done()
            frozen_datetime.tick(delta=datetime.timedelta(hours=1))

        state = hass.states.get("sensor.my_mock_es")
        assert len(state.attributes[PRICES]) == rolling_hours
        assert len(state.attributes[ENERGY]) == rolling_hours + 1
        assert state.state == str(score)


async def test_rolling_hours_default(hass: HomeAssistant) -> None:
    """Test that the default rolling hours is 24"""

    CONFIG = copy.deepcopy(VALID_CONFIG)

    initial_datetime = dt.parse_datetime("2022-09-18 21:08:44+01:00")
    with freeze_time(initial_datetime) as frozen_datetime:
        assert await async_setup_component(hass, "sensor", CONFIG)
        await hass.async_block_till_done()

        for hour in range(0, 36):
            hass.states.async_set("sensor.energy", ENERGY_LIST[hour])
            hass.states.async_set("sensor.electricity_price", hour)
            async_fire_time_changed(hass, dt.now() + SCAN_INTERVAL)
            await hass.async_block_till_done()
            frozen_datetime.tick(delta=datetime.timedelta(hours=1))

        state = hass.states.get("sensor.my_mock_es")
        assert len(state.attributes[PRICES]) == 24


async def test_rolling_hours_range_low(hass: HomeAssistant, caplog) -> None:
    """Test rolling hours outside range"""

    CONFIG = copy.deepcopy(VALID_CONFIG)
    CONFIG["sensor"]["rolling_hours"] = 1
    assert await async_setup_component(hass, "sensor", CONFIG)
    assert (
        "value must be at least 2 for dictionary value @ data['rolling_hours']. Got 1"
        in caplog.text
    )


async def test_rolling_hours_range_high(hass: HomeAssistant, caplog) -> None:
    """Test rolling hours outside range"""

    CONFIG = copy.deepcopy(VALID_CONFIG)
    CONFIG["sensor"]["rolling_hours"] = 170
    assert await async_setup_component(hass, "sensor", CONFIG)
    assert (
        "value must be at most 168 for dictionary value @ data['rolling_hours']. Got 170"
        in caplog.text
    )
