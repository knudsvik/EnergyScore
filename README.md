# EnergyScore for Home Assistant

[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

EnergyScore is a metric that scores how well you are utilizing changing energy prices throughout a day. If you use all of your energy in the most expensive hour it will score 0%, while if you use all your energy in the cheapest hour it will score 100%. This integration will not try to optimize your energy use, but is complementary to those like [PowerSaver](https://powersaver.no) or [PriceAnalyzer](https://github.com/erlendsellie/priceanalyzer).

You can set up several EnergyScore sensors,e.g. one on your total energy usage, another for EV charging or maybe one for your boiler.

Each sensor has a quality attribute with a score from 0 (no data this day) to 1 (data for all hours of this day).

## Installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `energyscore`.
4. Download _all_ the files from the `custom_components/energyscore/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Add following to your `configuration.yaml` (and customise with your entities and unique_id):
    ```yaml
    sensor:
      - platform: energyscore
        name: Heater Energy Score
        unique_id: AC816DB0-868A-431C-92AE-CBD46A864DC5
        price_entity: sensor.electricity_price
        energy_entity: sensor.home_total_energy
    ```
7. Restart Home Assistant. It may take up to an hour to get enough data to calculate the EnergyScore.

### Configuration variables

**name** *string* REQUIRED <br>
Name for the platform entity which must be unique within the platform.

**unique_id** *string* REQUIRED <br>
An ID that uniquely identifies this sensor. If two sensors have the same unique ID, Home Assistant will raise an exception.

**price_entity** *string* REQUIRED <br>
The entity_id of an entity which provides the current hourly energy price as the state, e.g. from Nordpool or Tibber integrations.

**energy_entity** *string* REQUIRED <br>
The entity_id of an entity which provides the total increasing energy use as the state, e.g. from Tibber or PowerCalc integrations or a state from a device.

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

***

[buymecoffee]: https://www.buymeacoffee.com/knudsvik
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=flat
[commits-shield]: https://img.shields.io/github/commit-activity/y/knudsvik/energyscore
[commits]: https://github.com/knudsvik/energyscore/commits/master
[license-shield]: https://img.shields.io/github/license/knudsvik/energyscore