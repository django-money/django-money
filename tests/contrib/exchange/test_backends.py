import sys

from django.core.exceptions import ImproperlyConfigured

import pytest

from djmoney.contrib.exchange.backends import FixerBackend, OpenExchangeRatesBackend
from djmoney.contrib.exchange.models import ExchangeBackend, Rate, get_rate

from .conftest import ExchangeTest, FixedOneBackend, FixedTwoBackend


pytestmark = pytest.mark.django_db


class TestBackends(ExchangeTest):
    def test_get_rates(self):
        assert self.backend.get_rates() == self.expected

    def test_initial_update_rates(self):
        self.backend.update_rates()
        self.assert_rates()

    def test_second_update_rates(self):
        self.backend.update_rates()
        backend = ExchangeBackend.objects.get(name=self.backend.name)
        last_update = backend.last_update
        self.backend.update_rates()
        backend.refresh_from_db()
        assert last_update < backend.last_update


@pytest.mark.parametrize("backend", (FixerBackend, OpenExchangeRatesBackend))
def test_missing_settings(backend):
    with pytest.raises(ImproperlyConfigured):
        backend(access_key=None)


@pytest.mark.usefixtures("two_backends_data")
def test_two_backends():
    """
    Two different backends should not interfere with each other.
    """
    for backend in (FixedOneBackend, FixedTwoBackend):
        assert Rate.objects.filter(backend__name=backend.name).count() == 1
    assert get_rate("USD", "EUR", backend=FixedOneBackend.name) == 1
    assert get_rate("USD", "EUR", backend=FixedTwoBackend.name) == 2


@pytest.fixture
def no_certifi():
    certifi = sys.modules["certifi"]
    sys.modules["certifi"] = None
    base = sys.modules.pop("djmoney.contrib.exchange.backends.base")
    yield
    sys.modules["certifi"] = certifi
    # Return the old module to keep all existing mocks in other tests
    sys.modules["djmoney.contrib.exchange.backends.base"] = base


@pytest.mark.usefixtures("no_certifi")
def test_certifi_not_installed():
    with pytest.raises(ImportError, match="Please install dependency certifi - pip install certifi"):
        __import__("djmoney.contrib.exchange.backends.base")
