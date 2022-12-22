"""Constants for EnergyScore testing"""

# Normalisation functions
PRICE_DICT = [
    {"a": 2, "b": 4, "c": 3.15, "d": 2.22},
    {"a": 1.0, "b": 0.0, "c": 0.42500000000000004, "d": 0.8899999999999999},
]
ENERGY_DICT = [
    {"a": 3, "b": 0, "c": 4, "d": 3},
    {"a": 0.3, "b": 0.0, "c": 0.4, "d": 0.3},
]
EMPTY_DICT = [{}, {}]

VALID_CONFIG = {
    "platform": "energyscore",
    "name": "My Mock ES",
    "energy_entity": "sensor.energy",
    "price_entity": "sensor.electricity_price",
    "unique_id": "CA0C3E3-38D3-4A79-91CC-129121AA3828",
}
