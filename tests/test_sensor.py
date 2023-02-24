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
    TEST_PARAMS,
)


async def test_new_config(hass: HomeAssistant) -> None:
    """Testing a default setup of an energyscore sensor"""
    assert await async_setup_component(hass, "sensor", VALID_CONFIG)
    await hass.async_block_till_done()

    # EnergyScore
    state = hass.states.get("sensor.my_mock_es_energyscore")
    assert state
    assert state.state == "100"
    assert len(state.attributes) == 10
    assert state.attributes.get("unit_of_measurement") == "%"
    assert state.attributes.get("state_class") == sensor.SensorStateClass.MEASUREMENT
    assert state.attributes.get("energy_entity") == "sensor.energy"
    assert state.attributes.get("price_entity") == "sensor.electricity_price"
    assert state.attributes.get("quality") == 0
    assert state.attributes.get("total_energy") == {}
    assert state.attributes.get("price") == {}
    assert state.attributes.get("last_updated") is None
    assert state.attributes.get("icon") == "mdi:speedometer"
    assert state.attributes.get("friendly_name") == "My Mock ES EnergyScore"

    # Cost sensor
    state = hass.states.get("sensor.my_mock_es_cost")
    assert state
    assert state.state == "unknown"  # Init None
    assert len(state.attributes) == 5
    assert (
        state.attributes.get("state_class") == sensor.SensorStateClass.TOTAL_INCREASING
    )
    assert state.attributes.get("last_updated_energy") == {}
    assert state.attributes.get("icon") == "mdi:currency-eur"
    assert state.attributes.get("last_updated") is None
    assert state.attributes.get("friendly_name") == "My Mock ES Cost"

    # Potential sensor
    state = hass.states.get("sensor.my_mock_es_potential_savings")
    assert state
    assert state.state == "unknown"
    assert len(state.attributes) == 11
    assert state.attributes.get("state_class") == sensor.SensorStateClass.MEASUREMENT
    assert state.attributes.get("icon") == "mdi:piggy-bank"
    assert state.attributes.get("average_cost") == None
    assert state.attributes.get("maximum_cost") == None
    assert state.attributes.get("minimum_cost") == None
    assert state.attributes.get("energy_today") == None
    assert state.attributes.get("last_updated_energy") == {}
    assert state.attributes.get("last_updated") is None
    assert state.attributes.get("price") == {}
    assert state.attributes.get("quality") is None
    assert state.attributes.get("friendly_name") == "My Mock ES Potential Savings"


async def test_unique_id(hass: HomeAssistant) -> None:
    """Testing a default setup with unique_id"""

    CONFIG = copy.deepcopy(VALID_CONFIG)
    CONFIG["sensor"]["unique_id"] = "Testing123"

    assert await async_setup_component(hass, "sensor", CONFIG)
    await hass.async_block_till_done()

    entity_reg = er.async_get(hass)
    assert (
        entity_reg.async_get("sensor.my_mock_es_energyscore").unique_id == "Testing123"
    )
    assert entity_reg.async_get("sensor.my_mock_es_cost").unique_id == "Testing123_cost"
    assert (
        entity_reg.async_get("sensor.my_mock_es_potential_savings").unique_id
        == "Testing123_potential_savings"
    )


def test_normalisation() -> None:
    """Test the normalisation function"""
    assert normalise_price(PRICE_DICT[0]) == PRICE_DICT[1]
    assert normalise_price(EMPTY_DICT[0]) == EMPTY_DICT[1]
    assert normalise_price(SAME_PRICE_DICT[0]) == SAME_PRICE_DICT[1]
    assert normalise_energy(ENERGY_DICT[0]) == ENERGY_DICT[1]
    assert normalise_energy(EMPTY_DICT[0]) == EMPTY_DICT[1]


# TODO: Test energy_calc functions


async def test_update_energyscore_sensor(hass: HomeAssistant, caplog) -> None:
    """Test the update of energyscore by moving time"""

    initial_datetime = dt.parse_datetime("2022-09-18 21:08:44+01:00")

    STATES = [100, 100, 90]
    QUALITIES = [0, 0.04, 0.08]

    with freeze_time(initial_datetime) as frozen_datetime:
        assert await async_setup_component(hass, "sensor", VALID_CONFIG)
        await hass.async_block_till_done()

        for hour in range(0, 3):
            hass.states.async_set("sensor.energy", TEST_PARAMS[hour]["energy"])
            hass.states.async_set(
                "sensor.electricity_price", TEST_PARAMS[hour]["price"]
            )
            async_fire_time_changed(hass, dt.now() + SCAN_INTERVAL)
            await hass.async_block_till_done()
            state = hass.states.get("sensor.my_mock_es_energyscore")
            assert state.state == str(STATES[hour])
            assert state.attributes[QUALITY] == QUALITIES[hour]
            if hour == 0:
                assert (
                    "My Mock ES EnergyScore - Not able to calculate energy use in the last 24 hours"
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
        state = hass.states.get("sensor.my_mock_es_energyscore")
        assert "2022-09-18T13:00:00-0700" not in state.attributes.get("price")
        # 1 extra hour of energy data is kept to be able to calculate energy usage
        frozen_datetime.tick(delta=datetime.timedelta(hours=1))
        hass.states.async_set("sensor.energy", 190)
        hass.states.async_set("sensor.electricity_price", 1)
        async_fire_time_changed(hass, dt.now() + SCAN_INTERVAL)
        await hass.async_block_till_done()
        state = hass.states.get("sensor.my_mock_es_energyscore")
        assert "2022-09-18T13:00:00-0700" not in state.attributes.get("total_energy")


async def test_update_cost_sensor(hass: HomeAssistant) -> None:
    """Test the update of cost sensor by moving time"""

    initial_datetime = dt.parse_datetime("2022-09-18 21:08:44-07:00")

    # The cost should reset at midnight
    COST = ["unknown", 0.08, 0.23, 0.0, 0.22, 5.64, 7.27, 8.19]

    with freeze_time(initial_datetime) as frozen_datetime:
        assert await async_setup_component(hass, "sensor", VALID_CONFIG)
        await hass.async_block_till_done()

        for hour in range(0, 5):
            hass.states.async_set("sensor.energy", TEST_PARAMS[hour]["energy"])
            hass.states.async_set(
                "sensor.electricity_price", TEST_PARAMS[hour]["price"]
            )
            async_fire_time_changed(hass, dt.now() + SCAN_INTERVAL)
            await hass.async_block_till_done()
            state = hass.states.get("sensor.my_mock_es_cost")
            assert state.state == str(COST[hour])
            frozen_datetime.tick(delta=datetime.timedelta(hours=1))

        # Testing resetting energy sensors (hour 30 is resetting):
        for hour in [5, 6, 7]:
            hass.states.async_set("sensor.energy", TEST_PARAMS[hour + 24]["energy"])
            hass.states.async_set(
                "sensor.electricity_price", TEST_PARAMS[hour + 24]["price"]
            )
            async_fire_time_changed(hass, dt.now() + SCAN_INTERVAL)
            await hass.async_block_till_done()
            state = hass.states.get("sensor.my_mock_es_cost")
            assert state.state == str(COST[hour])
            frozen_datetime.tick(delta=datetime.timedelta(hours=1))


async def test_update_savings_sensor(hass: HomeAssistant) -> None:
    """Test the update of potential savings sensor by moving time"""

    initial_datetime = dt.parse_datetime("2022-09-18 19:08:44-07:00")

    # Since they are async, can't know which sensor updates first, so hardcoding cost
    # Last reading after midnight to check reseting
    COST = [0, 0.08, 0.23, 0.23, 0.45, 0.18, 5.44, 7.08, 7.99]

    # The savings should reset at midnight (hour 5)
    RESULT = [
        {"avg": None, "max": None, "min": None, "potential": "unknown"},
        {"avg": 0.2, "max": 0.32, "min": 0.08, "potential": 0.0},
        {"avg": 0.39, "max": 0.72, "min": 0.18, "potential": 0.05},
        {"avg": 0.43, "max": 0.72, "min": 0.18, "potential": 0.05},
        {"avg": 0.66, "max": 1.12, "min": 0.28, "potential": 0.17},
        {"avg": 0.18, "max": 0.18, "min": 0.18, "potential": 0.0},
        {"avg": 5.77, "max": 6.12, "min": 5.42, "potential": 0.02},
        {"avg": 10.94, "max": 20.26, "min": 5.9, "potential": 1.18},
        {"avg": 15.37, "max": 27.53, "min": 6.1, "potential": 1.89},
    ]

    with freeze_time(initial_datetime) as frozen_datetime:
        assert await async_setup_component(hass, "sensor", VALID_CONFIG)
        await hass.async_block_till_done()

        for hour in range(0, 6):
            hass.states.async_set("sensor.energy", TEST_PARAMS[hour]["energy"])
            hass.states.async_set(
                "sensor.electricity_price", TEST_PARAMS[hour]["price"]
            )
            hass.states.async_set("sensor.my_mock_es_cost", COST[hour])
            async_fire_time_changed(hass, dt.now() + SCAN_INTERVAL)
            await hass.async_block_till_done()
            state = hass.states.get("sensor.my_mock_es_potential_savings")
            assert state.state == str(RESULT[hour]["potential"])
            assert state.attributes.get("average_cost") == RESULT[hour]["avg"]
            assert state.attributes.get("maximum_cost") == RESULT[hour]["max"]
            assert state.attributes.get("minimum_cost") == RESULT[hour]["min"]
            frozen_datetime.tick(delta=datetime.timedelta(hours=1))

        # Testing resetting energy sensors (hour 30 is resetting):
        for hour in [6, 7, 8]:
            hass.states.async_set("sensor.energy", TEST_PARAMS[hour + 23]["energy"])
            hass.states.async_set(
                "sensor.electricity_price", TEST_PARAMS[hour + 23]["price"]
            )
            hass.states.async_set("sensor.my_mock_es_cost", COST[hour])
            async_fire_time_changed(hass, dt.now() + SCAN_INTERVAL)
            await hass.async_block_till_done()
            state = hass.states.get("sensor.my_mock_es_potential_savings")
            assert state.state == str(RESULT[hour]["potential"])
            assert state.attributes.get("average_cost") == RESULT[hour]["avg"]
            assert state.attributes.get("maximum_cost") == RESULT[hour]["max"]
            assert state.attributes.get("minimum_cost") == RESULT[hour]["min"]
            frozen_datetime.tick(delta=datetime.timedelta(hours=1))


async def test_unavailable_sources(hass: HomeAssistant, caplog) -> None:
    """Testing unavailable or unknown price or energy sensors"""
    assert await async_setup_component(hass, "sensor", VALID_CONFIG)
    await hass.async_block_till_done()

    for state in [STATE_UNAVAILABLE, STATE_UNKNOWN]:
        hass.states.async_set("sensor.energy", 24321.4)
        hass.states.async_set("sensor.electricity_price", state)
        hass.states.async_set("sensor.my_mock_es_cost", 23.2)
        async_fire_time_changed(hass, dt.now() + SCAN_INTERVAL)
        await hass.async_block_till_done()
        assert f"My Mock ES EnergyScore - Price data is {state}" in caplog.text
        assert f"My Mock ES Cost - Price data is {state}" in caplog.text
        assert f"Potential data cannot be updated, state is {state}" in caplog.text

        hass.states.async_set("sensor.energy", state)
        hass.states.async_set("sensor.electricity_price", 0.42)
        hass.states.async_set("sensor.my_mock_es_cost", 23.2)
        async_fire_time_changed(hass, dt.now() + SCAN_INTERVAL)
        await hass.async_block_till_done()
        assert f"My Mock ES EnergyScore - Energy data is {state}" in caplog.text
        assert f"My Mock ES Cost - Energy data is {state}" in caplog.text
        assert f"Potential data cannot be updated, state is {state}" in caplog.text

        hass.states.async_set("sensor.energy", 24321.4)
        hass.states.async_set("sensor.electricity_price", 0.42)
        hass.states.async_set("sensor.my_mock_es_cost", state)
        async_fire_time_changed(hass, dt.now() + SCAN_INTERVAL)
        await hass.async_block_till_done()
        assert f"Potential data cannot be updated, state is {state}" in caplog.text


async def test_all_sources_unavailable(hass: HomeAssistant, caplog) -> None:
    """Testing if both sources are unavailable or unknown (new caplog)"""
    assert await async_setup_component(hass, "sensor", VALID_CONFIG)
    await hass.async_block_till_done()

    for state in [STATE_UNAVAILABLE, STATE_UNKNOWN]:
        hass.states.async_set("sensor.energy", state)
        hass.states.async_set("sensor.electricity_price", state)
        hass.states.async_set("sensor.my_mock_es_cost", state)
        async_fire_time_changed(hass, dt.now() + SCAN_INTERVAL)
        await hass.async_block_till_done()
        assert f"My Mock ES EnergyScore - Energy data is {state}" in caplog.text
        assert f"My Mock ES EnergyScore - Price data is {state}" in caplog.text
        assert f"My Mock ES Cost - Energy data is {state}" in caplog.text
        assert f"My Mock ES Cost - Price data is {state}" in caplog.text
        assert f"Potential data cannot be updated, state is {state}" in caplog.text


async def test_no_sources(hass: HomeAssistant, caplog) -> None:
    """Testing to catch no source excpetion"""
    assert await async_setup_component(hass, "sensor", VALID_CONFIG)
    await hass.async_block_till_done()
    async_fire_time_changed(hass, dt.now() + SCAN_INTERVAL)
    await hass.async_block_till_done()
    assert (
        f"My Mock ES EnergyScore - Could not fetch price and energy data" in caplog.text
    )
    assert f"My Mock ES Cost - Could not fetch price and energy data" in caplog.text


async def test_non_numeric_source_state(hass: HomeAssistant, caplog) -> None:
    """Testing to catch non-numeric excpetion"""
    assert await async_setup_component(hass, "sensor", VALID_CONFIG)
    await hass.async_block_till_done()
    hass.states.async_set("sensor.energy", 123.4)
    hass.states.async_set("sensor.electricity_price", "text")
    hass.states.async_set("sensor.my_mock_es_cost", 12.2)
    await hass.async_block_till_done()
    async_fire_time_changed(hass, dt.now() + SCAN_INTERVAL)
    await hass.async_block_till_done()
    for i in ["EnergyScore", "Cost", "Potential Savings"]:
        assert f"My Mock ES {i} - Possibly non-numeric source state" in caplog.text


async def test_restore_energyscore(hass: HomeAssistant, caplog) -> None:
    """Testing restoring EnergyScore sensor state and attributes
    Inspired by code in core/tests/helpers/test_restore_state.py
    """
    stored_state = StoredState(
        State(
            "sensor.my_mock_es_energyscore",
            "38",  # HA restores states as strings
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
    assert "Restored My Mock ES EnergyScore" in caplog.text

    # Assert restored data
    state = hass.states.get("sensor.my_mock_es_energyscore")
    assert state.state == "38"
    assert state.attributes.get("quality") == 0.12
    assert state.attributes.get("total_energy") == {"2022-09-18T13:00:00-0700": 122.39}
    assert state.attributes.get("price") == {"2022-09-18T13:00:00-0700": 0.99}
    assert state.attributes.get("last_updated") == "2020-12-01T20:50:53.131803+01:00"

    # Following attributes are saved, but not restored, so should still be the default
    assert state.attributes.get("energy_entity") == "sensor.energy"
    assert state.attributes.get("price_entity") == "sensor.electricity_price"
    assert state.attributes.get("friendly_name") == "My Mock ES EnergyScore"
    assert state.attributes.get("icon") == "mdi:speedometer"


@pytest.mark.parametrize("restore_day", ["same day", "another day"])
async def test_restore_cost(hass: HomeAssistant, caplog, restore_day) -> None:
    """Testing restoring cost sensor state and attributes"""
    if restore_day == "same day":
        initial_datetime = dt.parse_datetime("2022-09-18 21:08:44+01:00")
    elif restore_day == "another day":
        initial_datetime = dt.parse_datetime("2022-09-23 04:23:24+01:00")

    stored_state = StoredState(
        State(
            "sensor.my_mock_es_cost",
            "2.33",  # HA restores states as strings
            attributes={
                "last_updated_energy": {"2022-09-18 11:10:44-07:00": 4.2},
                "last_updated": "2022-09-18 11:10:44-07:00",
            },
        ),
        None,
        "2022-09-18 11:10:44-07:00",
    )

    with freeze_time(initial_datetime) as frozen_datetime:
        data = await RestoreStateData.async_get_instance(hass)
        await hass.async_block_till_done()
        await data.store.async_save([stored_state.as_dict()])

        # Emulate a fresh load
        hass.data.pop(DATA_RESTORE_STATE_TASK)

        assert await async_setup_component(hass, "sensor", VALID_CONFIG)
        await hass.async_block_till_done()

        # Assert restored data
        state = hass.states.get("sensor.my_mock_es_cost")
        assert state.attributes.get("last_updated_energy") == {
            "2022-09-18 11:10:44-07:00": 4.2
        }
        assert state.attributes.get("last_updated") == dt.parse_datetime(
            "2022-09-18 11:10:44-07:00"
        )
        if restore_day == "same day":
            assert "Restored My Mock ES Cost" in caplog.text
            assert state.state == "2.33"
        elif restore_day == "another day":
            assert "Restored My Mock ES Cost" not in caplog.text
            assert state.state == "0"


@pytest.mark.parametrize("restore_day", ["same day", "another day"])
async def test_restore_potential(hass: HomeAssistant, caplog, restore_day) -> None:
    """Testing restoring potential sensor state and attributes"""
    if restore_day == "same day":
        initial_datetime = dt.parse_datetime("2022-09-18 21:08:44+01:00")
    elif restore_day == "another day":
        initial_datetime = dt.parse_datetime("2022-09-23 04:23:24+01:00")

    # now = dt.now()
    # now_str = now.strftime("%Y-%m-%dT%H:%M:%S%z")
    stored_state = StoredState(
        State(
            "sensor.my_mock_es_potential_savings",
            "3.33",  # HA restores states as strings
            attributes={
                "average_cost": 1.13,
                "maximum_cost": 5.34,
                "minimum_cost": 0.23,
                "energy_today": 13.1,
                "last_updated_energy": {"2022-09-18T11:10:44-07:00": 4.2},
                "last_updated": dt.parse_datetime("2022-09-18 11:10:44-07:00"),
                "price": {"2022-09-18T13:00:00-0700": 0.99},
                "quality": 0.76,
            },
        ),
        None,
        "2022-09-18 11:10:44-07:00",
    )

    with freeze_time(initial_datetime) as frozen_datetime:
        data = await RestoreStateData.async_get_instance(hass)
        await hass.async_block_till_done()
        await data.store.async_save([stored_state.as_dict()])

        # Emulate a fresh load
        hass.data.pop(DATA_RESTORE_STATE_TASK)

        assert await async_setup_component(hass, "sensor", VALID_CONFIG)
        await hass.async_block_till_done()
        assert "Restored My Mock ES Potential Savings" in caplog.text

        # Assert restored data
        state = hass.states.get("sensor.my_mock_es_potential_savings")
        assert state.attributes.get("last_updated") == dt.parse_datetime(
            "2022-09-18 11:10:44-07:00"
        )
        if restore_day == "same day":
            assert state.state == "3.33"
            assert state.attributes.get("average_cost") == 1.13
            assert state.attributes.get("maximum_cost") == 5.34
            assert state.attributes.get("minimum_cost") == 0.23
            assert state.attributes.get("energy_today") == 13.1
            assert state.attributes.get("quality") == 0.76

            assert state.attributes.get("last_updated_energy") == {
                "2022-09-18T11:10:44-07:00": 4.2
            }
            assert state.attributes.get("price") == {"2022-09-18T13:00:00-0700": 0.99}
        elif restore_day == "another day":
            assert state.state == "0"
            assert state.attributes.get("average_cost") is None
            assert state.attributes.get("maximum_cost") is None
            assert state.attributes.get("minimum_cost") is None
            assert state.attributes.get("energy_today") is None
            assert state.attributes.get("quality") is None
            assert state.attributes.get("last_updated_energy") == {}
            assert state.attributes.get("price") == {}


async def test_declining_energy_energyscore(hass, caplog):
    """Testing that energyscore handles energy sensors that declines"""

    initial_datetime = dt.parse_datetime("2021-12-31 22:08:44-08:00")

    with freeze_time(initial_datetime) as frozen_datetime:
        assert await async_setup_component(hass, "sensor", VALID_CONFIG)
        await hass.async_block_till_done()

        # Initial setup with three hours to get real score
        for hour in [27, 28, 29]:
            hass.states.async_set(
                "sensor.electricity_price", TEST_PARAMS[hour]["price"]
            )
            hass.states.async_set("sensor.energy", TEST_PARAMS[hour]["energy"])
            async_fire_time_changed(hass, dt.now() + SCAN_INTERVAL)
            await hass.async_block_till_done()
            frozen_datetime.tick(delta=datetime.timedelta(hours=1))
        state = hass.states.get("sensor.my_mock_es_energyscore")
        assert state.state == "62"
        assert state.attributes.get("quality") == 0.08

        # Case state_class measurement
        hass.states.async_set(
            "sensor.energy",
            TEST_PARAMS[30]["energy"],
            attributes={
                "state_class": sensor.SensorStateClass.MEASUREMENT,
            },
        )
        hass.states.async_set("sensor.electricity_price", TEST_PARAMS[30]["price"])
        async_fire_time_changed(hass, dt.now() + SCAN_INTERVAL)
        await hass.async_block_till_done()
        state = hass.states.get("sensor.my_mock_es_energyscore")
        assert state.state == "81"
        assert state.attributes.get("quality") == 0.08
        assert (
            "My Mock ES EnergyScore - The energy entity's state class is measurement. Please change energy entity to a total/total_increasing, or fix the current energy entity state class."
            in caplog.text
        )

        # Case state_class None, replacing data without state class first
        hass.states.async_set("sensor.energy", TEST_PARAMS[30]["energy"])
        async_fire_time_changed(hass, dt.now() + SCAN_INTERVAL)
        await hass.async_block_till_done()
        state = hass.states.get("sensor.my_mock_es_energyscore")
        assert state.state == "81"
        assert (
            "My Mock ES EnergyScore - The energy entity's state class is None. Please change energy entity to a total/total_increasing, or fix the current energy entity state class."
            in caplog.text
        )

        # Case state_class total but no reset
        hass.states.async_set(
            "sensor.energy",
            TEST_PARAMS[30]["energy"],
            attributes={
                "state_class": sensor.SensorStateClass.TOTAL,
            },
        )
        async_fire_time_changed(hass, dt.now() + SCAN_INTERVAL)
        await hass.async_block_till_done()
        state = hass.states.get("sensor.my_mock_es_energyscore")
        assert state.state == "81"
        assert state.attributes.get("quality") == 0.08
        assert (
            "My Mock ES EnergyScore - The energy entity's state class is total, but there is no last_reset attribute to confirm that the sensor is expected to decline the value."
            in caplog.text
        )

        # Case state_class: total_increasing
        hass.states.async_set(
            "sensor.energy",
            TEST_PARAMS[30]["energy"],
            attributes={"state_class": sensor.SensorStateClass.TOTAL_INCREASING},
        )
        async_fire_time_changed(hass, dt.now() + SCAN_INTERVAL)
        await hass.async_block_till_done()
        state = hass.states.get("sensor.my_mock_es_energyscore")
        assert state.state == "32"
        assert state.attributes.get("quality") == 0.12

        # Case state_class: total and last_reset
        hass.states.async_set(
            "sensor.energy",
            TEST_PARAMS[30]["energy"],
            attributes={
                "state_class": sensor.SensorStateClass.TOTAL,
                "last_reset": "2022-01-01 00:00:53-08:00",
            },
        )
        async_fire_time_changed(hass, dt.now() + SCAN_INTERVAL)
        await hass.async_block_till_done()
        state = hass.states.get("sensor.my_mock_es_energyscore")
        assert state.state == "32"
        assert state.attributes.get("quality") == 0.12


async def test_quality_energyscore(hass: HomeAssistant) -> None:
    """Test that the quality attribute is behaving correctly for EnergyScore"""

    initial_datetime = dt.parse_datetime("2022-09-18 21:08:44+01:00")

    with freeze_time(initial_datetime) as frozen_datetime:
        assert await async_setup_component(hass, "sensor", VALID_CONFIG)
        await hass.async_block_till_done()

        for hour in range(1, 27):
            hass.states.async_set("sensor.energy", TEST_PARAMS[hour]["energy"])
            hass.states.async_set(
                "sensor.electricity_price", TEST_PARAMS[hour]["price"]
            )
            async_fire_time_changed(hass, dt.now() + SCAN_INTERVAL)
            await hass.async_block_till_done()
            state = hass.states.get("sensor.my_mock_es_energyscore")
            if hour >= 25:
                assert state.attributes[QUALITY] == 1
            else:
                assert state.attributes[QUALITY] == round((hour - 1) / 24, 2)
            frozen_datetime.tick(delta=datetime.timedelta(hours=1))

        # Advance 10 minute slots to verify all parts of an hour:
        for part_hour in range(1, 6):
            frozen_datetime.tick(delta=datetime.timedelta(minutes=10))
            hass.states.async_set(
                "sensor.energy", TEST_PARAMS[hour]["energy"] + part_hour
            )
            hass.states.async_set("sensor.electricity_price", part_hour)
            async_fire_time_changed(hass, dt.now() + SCAN_INTERVAL)
            await hass.async_block_till_done()
            state = hass.states.get("sensor.my_mock_es_energyscore")
            assert state.attributes[QUALITY] == 1


async def test_quality_potential_savings(hass: HomeAssistant) -> None:
    """Test that the quality attribute is behaving correctly for Potential sensor"""

    initial_datetime = dt.parse_datetime("2022-09-18 20:08:44-07:00")

    with freeze_time(initial_datetime) as frozen_datetime:
        assert await async_setup_component(hass, "sensor", VALID_CONFIG)
        await hass.async_block_till_done()

        for hour in range(0, 30):
            hass.states.async_set("sensor.energy", TEST_PARAMS[hour]["energy"])
            hass.states.async_set(
                "sensor.electricity_price", TEST_PARAMS[hour]["price"]
            )
            hass.states.async_set("sensor.my_mock_es_cost", hour)
            async_fire_time_changed(hass, dt.now() + SCAN_INTERVAL)
            await hass.async_block_till_done()
            state = hass.states.get("sensor.my_mock_es_potential_savings")
            if hour == 0:
                assert state.attributes[QUALITY] == None
            elif 1 <= hour < 4:  # To midnight
                assert state.attributes[QUALITY] == round(
                    (hour + 1) / (dt.now().hour + 1), 2
                )
            else:
                assert state.attributes[QUALITY] == 1
            frozen_datetime.tick(delta=datetime.timedelta(hours=1))


async def test_energy_treshold(hass: HomeAssistant) -> None:
    """Test that the treshold function is working as intended"""

    CONFIG = copy.deepcopy(VALID_CONFIG)
    CONFIG["sensor"]["energy_treshold"] = 0.14

    initial_datetime = dt.parse_datetime("2022-09-18 21:08:44+01:00")
    with freeze_time(initial_datetime) as frozen_datetime:
        assert await async_setup_component(hass, "sensor", CONFIG)
        await hass.async_block_till_done()

        for hour in range(0, 7):
            hass.states.async_set("sensor.energy", TEST_PARAMS[hour]["energy"])
            hass.states.async_set(
                "sensor.electricity_price", TEST_PARAMS[hour]["price"]
            )
            async_fire_time_changed(hass, dt.now() + SCAN_INTERVAL)
            await hass.async_block_till_done()
            frozen_datetime.tick(delta=datetime.timedelta(hours=1))

        state = hass.states.get("sensor.my_mock_es_energyscore")
        assert state.state == "71"
        assert state.attributes[QUALITY] == 0.17


rolling_parameters = [(3, 5, 76), (4, 10, 18), (37, 40, 60)]


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
            hass.states.async_set(
                "sensor.energy",
                TEST_PARAMS[hour]["energy"],
                attributes={"state_class": sensor.SensorStateClass.TOTAL_INCREASING},
            )
            hass.states.async_set(
                "sensor.electricity_price", TEST_PARAMS[hour]["price"]
            )
            async_fire_time_changed(hass, dt.now() + SCAN_INTERVAL)
            await hass.async_block_till_done()
            frozen_datetime.tick(delta=datetime.timedelta(hours=1))

        state = hass.states.get("sensor.my_mock_es_energyscore")
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
            hass.states.async_set(
                "sensor.energy",
                TEST_PARAMS[hour]["energy"],
                attributes={"state_class": sensor.SensorStateClass.TOTAL_INCREASING},
            )
            hass.states.async_set(
                "sensor.electricity_price", TEST_PARAMS[hour]["price"]
            )
            async_fire_time_changed(hass, dt.now() + SCAN_INTERVAL)
            await hass.async_block_till_done()
            frozen_datetime.tick(delta=datetime.timedelta(hours=1))

        state = hass.states.get("sensor.my_mock_es_energyscore")
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


async def test_negative_potential(hass: HomeAssistant) -> None:
    """Tests that potential cannot become negative"""

    initial_datetime = dt.parse_datetime("2022-09-18 21:08:44+01:00")

    with freeze_time(initial_datetime) as frozen_datetime:
        assert await async_setup_component(hass, "sensor", VALID_CONFIG)
        await hass.async_block_till_done()

        # Setting up a potential that would give negative potential (since cost = 0)
        hass.states.async_set("sensor.energy", 1.2)
        hass.states.async_set("sensor.electricity_price", 0.5)
        hass.states.async_set("sensor.my_mock_es_cost", 0)
        async_fire_time_changed(hass, dt.now() + SCAN_INTERVAL)
        await hass.async_block_till_done()

        frozen_datetime.tick(delta=datetime.timedelta(hours=1))
        hass.states.async_set("sensor.energy", 2.8)
        hass.states.async_set("sensor.electricity_price", 1.0)
        hass.states.async_set("sensor.my_mock_es_cost", 0)
        async_fire_time_changed(hass, dt.now() + SCAN_INTERVAL)
        await hass.async_block_till_done()

        state = hass.states.get("sensor.my_mock_es_potential_savings")
        assert float(state.state) == 0
