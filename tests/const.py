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

# Configs
VALID_CONFIG = {
    "sensor": {
        "platform": "energyscore",
        "name": "My Mock ES",
        "energy_entity": "sensor.energy",
        "price_entity": "sensor.electricity_price",
    }
}

VALID_UI_CONFIG = {
    "name": "UI EnergyScore",
    "energy_entity": "sensor.energy_ui",
    "price_entity": "sensor.price_ui",
}

# Common energy and price lists
ENERGY_LIST = [
    1,
    2,
    3,
    3.4,
    3.5,
    3.7,
    4.1,
    5.6,
    5.7,
    6.7,
    6.8,
    6.9,
    7.1,
    7.3,
    7.7,
    9.2,
    9.4,
    9.8,
    9.9,
    10.3,
    10.8,
    11.9,
    14,
    15.2,
    16,
    16.1,
    16.4,
    16.9,
    17,
    17.4,
    18,
    18.2,
    19.3,
    20.5,
    21.6,
    24.2,
    26.6,
    28,
    32.2,
    33.3,
]
