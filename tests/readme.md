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
`pytest tests/` | This will run all tests in `tests/` and tell you how many passed/failed
`pytest --durations=10 --cov-report term-missing --cov=custom_components.integration_blueprint tests` | This tells `pytest` that your target module to test is `custom_components.integration_blueprint` so that it can give you a [code coverage](https://en.wikipedia.org/wiki/Code_coverage) summary, including % of code that was executed and the line numbers of missed executions.
`pytest tests/test_init.py -k test_setup_unload_and_reload_entry` | Runs the `test_setup_unload_and_reload_entry` test function located in `tests/test_init.py`

# References
Based on the [integration blueprint tests](https://github.com/custom-components/integration_blueprint/tree/master/tests).