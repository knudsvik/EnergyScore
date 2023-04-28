"""pytest fixtures."""
import pytest


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations defined in the test dir."""
    yield


@pytest.fixture(autouse=True)
def expected_lingering_timers() -> bool:
    """Temporary ability to bypass test failures.
    Parametrize to True to bypass the pytest failure.
    @pytest.mark.parametrize("expected_lingering_timers", [True])
    This should be removed when all lingering timers have been cleaned up.
    See https://github.com/MatthewFlamm/pytest-homeassistant-custom-component/issues/153
    """
    return True
