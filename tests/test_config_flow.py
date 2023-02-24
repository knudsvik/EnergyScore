"""
ConfigFlow tests for EnergyScore
Inspiration from
- Aaron Godfrey's custom component tutorial, parts 3 and 4
- MinMax ConfigEntry tests
"""
from unittest import mock

from homeassistant.data_entry_flow import FlowResultType
from homeassistant.components.sensor import SensorStateClass
from pytest_homeassistant_custom_component.common import MockConfigEntry
from homeassistant.helpers import device_registry as dr, entity_registry as er

from custom_components.energyscore import config_flow
from custom_components.energyscore.const import DOMAIN

from .const import VALID_UI_CONFIG


async def test_flow_user_init(hass):
    """Test the initialization of the form in the sensor setup config flow"""
    result = await hass.config_entries.flow.async_init(
        config_flow.DOMAIN, context={"source": "user"}
    )

    expected = {
        "data_schema": config_flow.CONFIG_SCHEMA,
        "description_placeholders": None,
        "errors": None,
        "flow_id": mock.ANY,
        "handler": "energyscore",
        "last_step": None,
        "step_id": "user",
        "type": "form",
    }
    assert expected == result


async def test_flow_creates_config_entry(hass):
    """Test the config entry is successfully created (sensor created)"""

    _result = await hass.config_entries.flow.async_init(
        config_flow.DOMAIN, context={"source": "user"}
    )
    result = await hass.config_entries.flow.async_configure(
        _result["flow_id"], VALID_UI_CONFIG
    )

    await hass.async_block_till_done()

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "UI"
    assert result["data"] == {
        "name": "UI",
        "energy_entity": "sensor.energy_ui",
        "price_entity": "sensor.price_ui",
        "unique_id": "ES_energy_ui_price_ui",
    }
    assert result["context"]["unique_id"] == "ES_energy_ui_price_ui"

    # EnergyScore
    state = hass.states.get("sensor.ui_energyscore")
    assert state
    assert state.state == "100"
    assert len(state.attributes) == 10
    assert state.attributes.get("unit_of_measurement") == "%"
    assert state.attributes.get("state_class") == SensorStateClass.MEASUREMENT
    assert state.attributes.get("energy_entity") == "sensor.energy_ui"
    assert state.attributes.get("price_entity") == "sensor.price_ui"
    assert state.attributes.get("quality") == 0
    assert state.attributes.get("total_energy") == {}
    assert state.attributes.get("price") == {}
    assert state.attributes.get("last_updated") is None
    assert state.attributes.get("icon") == "mdi:speedometer"
    assert state.attributes.get("friendly_name") == "UI EnergyScore"

    # Cost sensor
    state = hass.states.get("sensor.ui_cost")
    assert state
    assert state.state == "unknown"
    assert len(state.attributes) == 5
    assert state.attributes.get("state_class") == SensorStateClass.TOTAL_INCREASING
    assert state.attributes.get("last_updated_energy") == {}
    assert state.attributes.get("friendly_name") == "UI Cost"
    assert state.attributes.get("last_updated") is None
    assert state.attributes.get("icon") == "mdi:currency-eur"

    # Potential savings sensor
    state = hass.states.get("sensor.ui_potential_savings")
    assert state
    assert state.state == "unknown"  # init: None
    assert len(state.attributes) == 11
    assert state.attributes.get("state_class") == SensorStateClass.MEASUREMENT
    assert state.attributes.get("friendly_name") == "UI Potential Savings"
    assert state.attributes.get("icon") == "mdi:piggy-bank"
    assert state.attributes.get("average_cost") == None
    assert state.attributes.get("maximum_cost") == None
    assert state.attributes.get("minimum_cost") == None
    assert state.attributes.get("energy_today") == None
    assert state.attributes.get("last_updated_energy") == {}
    assert state.attributes.get("last_updated") is None
    assert state.attributes.get("price") == {}
    assert state.attributes.get("quality") is None

    # Test all sensors are added to same device
    entity_reg = er.async_get(hass)
    score = entity_reg.async_get_or_create("sensor", DOMAIN, "ES_energy_ui_price_ui")
    cost = entity_reg.async_get_or_create(
        "sensor", DOMAIN, "ES_energy_ui_price_ui_cost"
    )
    save = entity_reg.async_get_or_create(
        "sensor", DOMAIN, "ES_energy_ui_price_ui_potential_savings"
    )
    assert score.device_id == cost.device_id == save.device_id


async def test_options_flow_add_treshold(hass):
    """Test that added treshold in options flow is saved to config"""

    config_entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id="blablabla",
        data=VALID_UI_CONFIG,
    )
    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    # show initial form
    result = await hass.config_entries.options.async_init(config_entry.entry_id)
    # submit form with options
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={"energy_treshold": 2.3},
    )

    energy_treshold = config_entry.options.get("energy_treshold")
    assert energy_treshold == 2.3
