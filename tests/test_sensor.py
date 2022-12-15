from custom_components.energyscore.const import CONF_ENERGY_ENTITY, CONF_PRICE_ENTITY
from homeassistant.setup import async_setup_component
from homeassistant.const import CONF_NAME, CONF_UNIQUE_ID

# from .const import MOCK_CONFIG_DATA

# config = MockConfigEntry(domain=DOMAIN, entry_id="test")

async def test_config(hass):
    """Test EnergyScore config."""
    config = {
    "sensor": {
        "platform": "energyscore",
        CONF_NAME: "My Mock ES",
        CONF_ENERGY_ENTITY: "sensor.energy",
        CONF_PRICE_ENTITY: "sensor.electricity_price",
        CONF_UNIQUE_ID: "CA0C3E3-38D3-4A79-91CC-129121AA3828",
        }
    }
    
    assert await async_setup_component(hass, "sensor", config)
    # Can not change "sensor" with "energyscore" over here for some reason. That also means
    # I cannot assert "energyscore" in hass.config.components.

    await hass.async_block_till_done()
    assert 'sensor.energyscore' in hass.config.components