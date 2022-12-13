from pytest_homeassistant_custom_component.common import MockPlatform
from custom_components.energyscore.const import DOMAIN
from custom_components.energyscore.sensor import async_setup_platform

from .const import FAKE_CONFIG_DATA


async def test_energyscore(hass):
    """Test EnergyScore config."""
    entry = MockPlatform(async_setup_platform=async_setup_platform)
    await hass.async_block_till_done()

    assert "energyscore" in hass.config.components

    #state = hass.states.get("sensor.example_temperature")

    #assert state
    #assert state.state == "23"
