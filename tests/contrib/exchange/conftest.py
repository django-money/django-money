import json
from contextlib import contextmanager
from decimal import Decimal
from unittest.mock import Mock, patch

from django.core.cache import cache

import pytest

from djmoney.contrib.exchange.backends import FixerBackend, OpenExchangeRatesBackend
from djmoney.contrib.exchange.backends.base import BaseExchangeBackend
from djmoney.contrib.exchange.models import ExchangeBackend, Rate


pytestmarks = pytest.mark.django_db


OPEN_EXCHANGE_RATES_RESPONSE = """{
    "disclaimer": "Usage subject to terms: https://openexchangerates.org/terms",
    "license": "https://openexchangerates.org/license",
    "timestamp": 1522749600,
    "base": "USD",
    "rates": {"EUR": 0.812511, "NOK": 7.847505, "SEK": 8.379037}
}"""
OPEN_EXCHANGE_RATES_EXPECTED = json.loads(OPEN_EXCHANGE_RATES_RESPONSE, parse_float=Decimal)["rates"]

FIXER_RESPONSE = """{
    "success":true,
    "timestamp":1522788248,
    "base":"EUR",
    "date":"2018-04-03",
    "rates":{"USD":1.227439,"NOK":9.624334,"SEK":10.300293}
}"""
FIXER_EXPECTED = json.loads(FIXER_RESPONSE, parse_float=Decimal)["rates"]


@contextmanager
def mock_backend(value):
    response = Mock()
    response.read.return_value = value
    with patch("djmoney.contrib.exchange.backends.base.urlopen", return_value=response):
        yield


class ExchangeTest:
    @pytest.fixture(
        autouse=True,
        params=(
            (OpenExchangeRatesBackend, OPEN_EXCHANGE_RATES_RESPONSE, OPEN_EXCHANGE_RATES_EXPECTED),
            (FixerBackend, FIXER_RESPONSE, FIXER_EXPECTED),
        ),
    )
    def setup(self, request):
        klass, response_value, expected = request.param
        self.backend = klass()
        self.expected = expected
        with mock_backend(response_value):
            yield

    def assert_rates(self):
        backend = ExchangeBackend.objects.get()
        assert Rate.objects.count() == len(self.expected)
        for currency, rate in self.expected.items():
            assert Rate.objects.filter(currency=currency, value=rate, backend=backend)


class FixedOneBackend(BaseExchangeBackend):
    name = "first"

    def get_rates(self, **params):
        return {"EUR": 1}


class FixedTwoBackend(BaseExchangeBackend):
    name = "second"

    def get_rates(self, **params):
        return {"EUR": 2}


@pytest.fixture
def two_backends_data():
    FixedOneBackend().update_rates()
    FixedTwoBackend().update_rates()


@pytest.fixture
def simple_rates(backend):
    Rate.objects.create(currency="EUR", value=2, backend=backend)


@pytest.fixture
def default_openexchange_rates():
    with mock_backend(OPEN_EXCHANGE_RATES_RESPONSE):
        OpenExchangeRatesBackend().update_rates()


@pytest.fixture(autouse=True)
def django_cache():
    cache.clear()
    yield
