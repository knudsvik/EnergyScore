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
        "unique_id": "Testing123",
    }
}


VALID_CONFIG_2 = {
    "sensor": [
        {
            "platform": "energyscore",
            "name": "My Mock ES",
            "energy_entity": "sensor.energy",
            "price_entity": "sensor.electricity_price",
            "unique_id": "Testing123",
        },
        {
            "platform": "energyscore",
            "name": "My Alternative ES",
            "energy_entity": "sensor.alternative_energy",
            "price_entity": "sensor.electricity_price",
            "unique_id": "Testing456",
        },
    ],
}

VALID_UI_CONFIG = {
    "name": "UI",
    "energy_entity": "sensor.energy_ui",
    "price_entity": "sensor.price_ui",
}


# Common energy and price test parameters
TEST_PARAMS = {
    0: {"energy": 0.2, "price": 0.4},
    1: {"energy": 1, "price": 0.1},
    2: {"energy": 2, "price": 0.15},
    3: {"energy": 2, "price": 0.3},
    4: {"energy": 3, "price": 0.22},
    5: {"energy": 3.4, "price": 0.44},
    6: {"energy": 3.5, "price": 0.32},
    7: {"energy": 3.7, "price": 1.34},
    8: {"energy": 4.1, "price": 2.33},
    9: {"energy": 5.6, "price": 3.88},
    10: {"energy": 5.7, "price": 3.56},
    11: {"energy": 6.7, "price": 2.45},
    12: {"energy": 6.8, "price": 1.23},
    13: {"energy": 6.9, "price": 0.55},
    14: {"energy": 7.1, "price": 1.22},
    15: {"energy": 7.3, "price": 0.1},
    16: {"energy": 7.7, "price": 0.13},
    17: {"energy": 9.2, "price": 0},  # Test case price = 0
    18: {"energy": 9.4, "price": 0.99},
    19: {"energy": 9.8, "price": 0.12},
    20: {"energy": 9.9, "price": 1.34},
    21: {"energy": 10.3, "price": 2.32},
    22: {"energy": 10.8, "price": 2.98},
    23: {"energy": 11.9, "price": 2.96},
    24: {"energy": 14, "price": 2.43},
    25: {"energy": 15.2, "price": 1.01},
    26: {"energy": 16, "price": 0.23},
    27: {"energy": 16.1, "price": 0.56},
    28: {"energy": 16.4, "price": 0.87},
    29: {"energy": 16.9, "price": 0.39},
    30: {"energy": 1.22, "price": 1.34},  # Test case resetting
    31: {"energy": 1.74, "price": 1.76},
    32: {"energy": 1.8, "price": 1.73},
    33: {"energy": 2.34, "price": 1.8},
    34: {"energy": 3.43, "price": 1.93},
    35: {"energy": 3.56, "price": 2.3},
    36: {"energy": 4.21, "price": 2.2},
    37: {"energy": 4.29, "price": 1.2},
    38: {"energy": 5.34, "price": 1.11},
    39: {"energy": 6.2, "price": 0.2},
    40: {"energy": 8, "price": 1.11},
}
