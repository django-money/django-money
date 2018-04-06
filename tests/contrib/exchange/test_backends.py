from django.core.exceptions import ImproperlyConfigured

import pytest

from djmoney.contrib.exchange.backends import (
    FixerBackend,
    OpenExchangeRatesBackend,
)
from djmoney.contrib.exchange.backends.base import BaseExchangeBackend
from djmoney.contrib.exchange.models import ExchangeBackend, Rate, get_rate

from .conftest import ExchangeTest


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


@pytest.mark.parametrize('backend', (FixerBackend, OpenExchangeRatesBackend))
def test_missing_settings(backend):
    with pytest.raises(ImproperlyConfigured):
        backend(access_key=None)


class FixedOneBackend(BaseExchangeBackend):
    name = 'first'

    def get_rates(self, **params):
        return {'EUR': 1}


class FixedTwoBackend(BaseExchangeBackend):
    name = 'second'

    def get_rates(self, **params):
        return {'EUR': 2}


def test_two_backends():
    """
    Two different backends should not interfere with each other.
    """
    one = FixedOneBackend()
    two = FixedTwoBackend()
    one.update_rates()
    two.update_rates()
    for backend in (one, two):
        assert Rate.objects.filter(backend__name=backend.name).count() == 1
    assert get_rate('USD', 'EUR', backend=one.name) == 1
    assert get_rate('USD', 'EUR', backend=two.name) == 2
