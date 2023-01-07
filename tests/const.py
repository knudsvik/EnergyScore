"""Constants for EnergyScore testing"""

# Normalisation functions
PRICE_DICT = [
    {"a": 2, "b": 4, "c": 3.15, "d": 2.22},
    {"a": 1.0, "b": 0.0, "c": 0.42500000000000004, "d": 0.8899999999999999},
]
SAME_PRICE_DICT = [{"a": 2.3, "b": 2.3, "c": 2.3}, {"a": 1, "b": 1, "c": 1}]
ENERGY_DICT = [
    {"a": 3, "b": 0, "c": 4, "d": 3},
    {"a": 0.3, "b": 0.0, "c": 0.4, "d": 0.3},
]
EMPTY_DICT = [{}, {}]

VALID_CONFIG = {
        "sensor": {
            "platform": "energyscore",
            "name": "My Mock ES",
            "energy_entity": "sensor.energy",
            "price_entity": "sensor.electricity_price",
            "unique_id": "CA0C3E3-38D3-4A79-91CC-1291dwAA3828",
        }
    }

VALID_UI_CONFIG = {
    "name": "UI EnergyScore",
    "energy_entity": "sensor.energy_ui",
    "price_entity": "sensor.price_ui",
    "unique_id": "09A8DC4C-7D93-448C-9501-F37AE9212263",
}