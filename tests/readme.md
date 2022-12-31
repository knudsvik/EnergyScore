# Getting Started

To begin, it is recommended to create a virtual environment to install dependencies, e.g. using [pyenv](https://github.com/pyenv/pyenv). Navigate to the root directory of the component and run following:
```bash
pyenv virtualenv EnergyScoreTests
pyenv activate EnergyScoreTests
```

You can then install the dependencies that will allow you to run tests:
```bash
pip install -r requirements_test.txt.
```

This will install `homeassistant`, `pytest`, and `pytest-homeassistant-custom-component`, a plugin which allows you to leverage helpers that are available in Home Assistant for core integration tests.

# Useful commands

Command | Description
------- | -----------
`pytest tests/` | This will run all tests in `tests/` and tell you how many passed/failed.
`pytest tests/ -s` | This will run all tests in `tests/` and tell you how many passed/failed. The `-s` attribute prints the Home Assistant log.
`pytest tests/ -s -k test_setup` | This will run all tests in `tests/` and tell you how many passed/failed. The `-s` attribute prints the Home Assistant log. The `-k` attrinute tells it to run only one specified test.


# References
Based on the [integration blueprint tests](https://github.com/custom-components/integration_blueprint/tree/master/tests).