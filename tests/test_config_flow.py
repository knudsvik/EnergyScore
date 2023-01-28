"""
ConfigFlow tests for EnergyScore
Inspiration from
- Aaron Godfrey's custom component tutorial, parts 3 and 4
- MinMax ConfigEntry tests
"""
from unittest import mock

from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

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
    assert result["title"] == "UI EnergyScore"
    assert result["data"] == {
        "name": "UI EnergyScore",
        "energy_entity": "sensor.energy_ui",
        "price_entity": "sensor.price_ui",
        "unique_id": "ES_energy_ui_price_ui",
    }
    assert result["context"]["unique_id"] == "ES_energy_ui_price_ui"

    state = hass.states.get("sensor.ui_energyscore")
    assert state.state == "100"
    assert state.attributes.get("energy_entity") == "sensor.energy_ui"
    assert state.attributes.get("price_entity") == "sensor.price_ui"
    assert state.attributes.get("friendly_name") == "UI EnergyScore"
    assert state.attributes.get("icon") == "mdi:speedometer"


async def test_options_flow_add_treshold(hass):
    """Test that added treshold in options flow is saved to config"""

    config_entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id="blablabla",
        data=VALID_UI_CONFIG,
        options={"energy_treshold": 0},
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
