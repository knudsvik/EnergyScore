<img src="https://raw.githubusercontent.com/knudsvik/EnergyScore/master/resources/logo.png" title="EnergyScore"/>

[![hacs_badge]](https://github.com/hacs/integration)
![analytics_badge]
[![GitHub Activity][commits-shield]][commits]
[![codecov_badge]](https://codecov.io/gh/knudsvik/EnergyScore)
[![License][license-shield]](LICENSE)
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]


EnergyScore is a metric that scores how well you are utilizing changing energy prices throughout the last 24 hours. The EnergyScore will be 0% if you use all of your energy in the most expensive hour, 100% in the cheapest hour, but most likely somewhere in between depending on how well you are able to match your energy use with cheap prices. This integration will not try to optimize your energy use, but is complementary to those like [PowerSaver](https://powersaver.no) or [PriceAnalyzer](https://github.com/erlendsellie/priceanalyzer).

<img src="https://raw.githubusercontent.com/knudsvik/EnergyScore/master/resources/energyScore_gauge.png" title="EnergyScore Gauge"/>

You can set up several EnergyScore sensors,e.g. one on your total energy usage, another for EV charging or maybe one for your boiler. Each sensor has a quality attribute with a score from 0 to 1 depending on the available data. If a sensor has price and energy data for 18 hours of the last 24, the quality will be 0.75. The higher the quality is, the more you can trust the EnergyScore.

## Installation

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=knudsvik&repository=energyscore&category=integration)

### Part 1 (HACS - preferred)

1. Click on the My link above *OR* open HACS, click on Integrations, then Explore and Download repositories and search for EnergyScore
2. click Download in the bottom and then follow instructions
3. Restart Home Assistant

### Part 1 (Manual alternative)

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `energyscore`.
4. Download _all_ the files from the `custom_components/energyscore/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant

### Part 2 (UI - preferred)

1. Open the integrations page
2. Click on the + to add a new integration
3. Search for and choose EnergyScore
4. Choose a name and the sensors to use.
It may take up to two hours to get enough data to calculate the EnergyScore.

### Part 2 (YAML alternative)

1. Add following to your `configuration.yaml`
    ```yaml
    sensor:
      - platform: energyscore
        name: Heater Energy Score
        unique_id: AC816DB0-868A-431C-92AE-CBD46A864DC5
        price_entity: sensor.nordpool_electricity_price
        energy_entity: sensor.heater_energy
    ```
2. Customise the configuration with your own entities and unique_id's
3. Restart Home Assistant.
It may take up to two hours to get enough data to calculate the EnergyScore.

### Configuration variables

Attribute | Data type | Type | Description
--------- | --------- | ---- | -----------
name | string | Required | Name for the platform entity which must be unique within the platform.
unique_id | string | Required | An ID that uniquely identifies this sensor. If two sensors have the same unique ID, Home Assistant will raise an exception.
price_entity | string | Required | The entity_id of an entity which provides the current hourly energy price as the state, e.g. from Nordpool or Tibber integrations.
energy_entity | string | Required | The entity_id of an entity which provides the total increasing energy use as the state, e.g. from Tibber or PowerCalc integrations or a state from a device. The energy entity can also be a total that resets at given intervals.


### Debugging

The integration can be debugged with following code in your `configuration.yaml` which will provide information on sensor updates in the Home Assistant log.

```yaml
logger:
  logs:
    custom_components.energyscore: debug
```

You can also start debugging with a service call:

```yaml
service: logger.set_level
data:
  custom_components.energyscore: debug
```

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

***

[buymecoffee]: https://www.buymeacoffee.com/knudsvik
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=flat
[commits-shield]: https://img.shields.io/github/commit-activity/y/knudsvik/energyscore
[commits]: https://github.com/knudsvik/energyscore/commits/master
[hacs_badge]: https://img.shields.io/badge/HACS-Default-41BDF5.svg
[license-shield]: https://img.shields.io/github/license/knudsvik/energyscore
[analytics_badge]: https://img.shields.io/badge/dynamic/json?color=41BDF5&logo=home-assistant&label=integration%20usage&suffix=%20installs&cacheSeconds=15600&url=https://analytics.home-assistant.io/custom_integrations.json&query=$.energyscore.total
[codecov_badge]: https://codecov.io/gh/knudsvik/EnergyScore/branch/master/graph/badge.svg?token=9MFR3PDZ8D
