# EnergyScore

[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

## Installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `energyscore`.
4. Download _all_ the files from the `custom_components/energyscore/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Add following to your `configuration.yaml`:
    ```yaml
    sensor:
      - platform: energyscore
        name: Heater Energy Score
        price_entity: sensor.x
        energy_entity: sensor.y
    ```
7. Restart Home Assistant

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

***

[buymecoffee]: https://www.buymeacoffee.com/knudsvik
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=flat
[commits-shield]: https://img.shields.io/github/commit-activity/y/knudsvik/energyscore
[commits]: https://github.com/knudsvik/energyscore/commits/master
[license-shield]: https://img.shields.io/github/license/knudsvik/energyscore