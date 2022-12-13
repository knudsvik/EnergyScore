from pytest_homeassistant_custom_component.common import MockConfigEntry
from custom_components.energyscore.const import DOMAIN

from.const import FAKE_CONFIG_DATA


async def test_energyscore(hass):
    """Test EnergyScore class."""
    entry = MockConfigEntry(domain=DOMAIN, data=FAKE_CONFIG_DATA)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert "energyscore" in hass.config.components

    state = hass.states.get("sensor.example_temperature")

    assert state
    assert state.state == "23"