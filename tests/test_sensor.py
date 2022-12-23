from homeassistant.components import sensor
from homeassistant.core import HomeAssistant
from .const import VALID_CONFIG

from custom_components.energyscore.sensor import normalise_energy, normalise_price

from .common import create_energyscore_sensor
from .const import EMPTY_DICT, ENERGY_DICT, PRICE_DICT, SAME_PRICE_DICT


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
    assert state.attributes.get("last_hour_energy") == {}
    assert state.attributes.get("energy") == {}
    assert state.attributes.get("price") == {}
    assert state.attributes.get("last_updated") == None
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
