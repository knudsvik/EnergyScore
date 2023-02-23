<img src="https://raw.githubusercontent.com/knudsvik/EnergyScore/master/resources/logo.png" title="EnergyScore"/>

[![hacs_badge]](https://github.com/hacs/integration)
![analytics_badge]
[![GitHub Activity][commits-shield]][commits]
[![codecov_badge]](https://codecov.io/gh/knudsvik/EnergyScore)
[![License][license-shield]](LICENSE)
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

An EnergyScore integration provides three sensors; EnergyScore, Cost and Potential Savings.

EnergyScore is a metric that scores how well you are utilizing changing energy prices throughout the last 24 hours. The EnergyScore will be 0% if you use all of your energy in the most expensive hour, 100% in the cheapest hour, but most likely somewhere in between depending on how well you are able to match your energy use with cheap prices. This integration will not try to optimize your energy use, but is complementary to those like [PowerSaver](https://powersaver.no) or [PriceAnalyzer](https://github.com/erlendsellie/priceanalyzer).

<img src="https://raw.githubusercontent.com/knudsvik/EnergyScore/master/resources/energyScore_gauge.png" title="EnergyScore Gauge"/>

The cost sensor provides the current day cost while the potential savings sensor compares actual current day cost with what the cost would be if all energy was consumed in the cheapes hour of the day. This is thus the potential savings that can be achieved if energy usage is optimised.

You can set up several EnergyScore integrations,e.g. one on your total energy usage, another for EV charging or maybe one for your boiler or dishwasher. EnergyScore and Potential Savings sensors both have a quality attribute with a score from 0 to 1 depending on the available data. If a sensor has price and energy data for 18 hours of the last 24, the quality will be 0.75. The higher the quality is, the more you can trust the sensors.

# Get started

## Installation

Install EnergyScore via HACS by using the My Button below or alternatively search for it in HACS integrations. Remember to restart Home Assistant afterwards.

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=knudsvik&repository=energyscore&category=integration)

## Configuration

EnergyScore sensors can be added directly from the user interface by using the My Button below or alternatively by browsing to your integrations page and adding it manually. It may take up to two hours to get enough data to calculate the EnergyScore.

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=energyscore)

Attribute | Description
--------- | -----------
Name | The name of the integration. You can change it again later.
Energy entity | A total (cumulative) energy entity, e.g. from Tibber or PowerCalc integrations or a state from a device. It can be both an entity that resets at given intervals or one that keeps increasing indefinetely.
Price entity | A price entity which provides the current hourly energy price as the state, e.g. from Nordpool or Tibber integrations.

### Advanced configuration
Some more options are available for advanced use and can be set up after initial setup by clicking the configure button in the integration.

Attribute | Description | Default
--------- | ----------- | -------
Energy Treshold | Energy less than the treshold (during one hour) will not contribute to the EnergyScore | 0
Rolling Hours | The period of time an EnergyScore should be scored on | 24


## YAML Configuration

Alternatively, this integration can be configured and set up manually via YAML instead. To enable the Integration sensor in your installation, add the following to your `configuration.yaml` file:

```yaml
sensor:
  - platform: energyscore
    name: Heater Energy Score
    energy_entity: sensor.heater_energy
    price_entity: sensor.nordpool_electricity_price
```

### Configuration variables

Attribute | Data type | Type | Description
--------- | --------- | ---- | -----------
name | string | Required | Name of the sensors to use in the frontend.
energy_entity | string | Required | A total (cumulative) energy entity, e.g. from Tibber or PowerCalc integrations or a state from a device. It can be both an entity that resets at given intervals or one that keeps increasing indefinetely.
price_entity | string | Required | TA price entity which provides the current hourly energy price as the state, e.g. from Nordpool or Tibber integrations.
unique_id | string | Optional | Unique id to be able to configure the entity in the UI.
energy_treshold | float | Optional | Energy less than the treshold (during one hour) will not contribute to the EnergyScore (default = 0).
rolling_hours | int | Optional | The number of hours the EnergyScore should be calculated from (default=24, min=2, max=168).


## Debugging

The integration can be debugged in several ways.

### From user interface
Go to your integrations dashboard (My Button below), choose an EnergyScore sensor to be debugged, click the three dots and then Enable debug logging.

[![Open your Home Assistant instance and show your integrations.](https://my.home-assistant.io/badges/integrations.svg)](https://my.home-assistant.io/redirect/integrations/)

### Always-on by use of YAML
The following code in your `configuration.yaml` will provide continuous information on EnergyScore sensor updates in the Home Assistant log.

```yaml
logger:
  logs:
    custom_components.energyscore: debug
```


### Service call

You can start debugging with a service call:

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
