from pytest_homeassistant_custom_component.common import MockConfigEntry
from custom_components.energyscore.const import DOMAIN, LAST_UPDATED
from custom_components.energyscore.sensor import EnergyScore, async_setup_platform

from .const import MOCK_CONFIG_DATA


async def test_energyscore(hass):
    """Test EnergyScore config."""
    config = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG_DATA, entry_id="test")

    assert await async_setup_platform(hass, config, async_add_entities)
    await hass.async_block_till_done()

    assert "energyscore" in hass.config.components

    #state = hass.states.get("sensor.example_temperature")

    #assert state
    #assert state.state == "23"