import json
from decimal import Decimal

import pytest

from djmoney.contrib.exchange.models import ExchangeBackend, Rate
from tests._compat import Mock, patch


pytestmarks = pytest.mark.django_db


@pytest.fixture()
def backend():
    return ExchangeBackend.objects.create(name='Test', base_currency='USD')


OPENEXCHANGERATES_RESPONSE = '''{
    "disclaimer": "Usage subject to terms: https://openexchangerates.org/terms",
    "license": "https://openexchangerates.org/license",
    "timestamp": 1522749600,
    "base": "USD",
    "rates": {"EUR": 0.812511, "NOK": 7.847505, "SEK": 8.379037}
}'''
EXPECTED_RATES = json.loads(OPENEXCHANGERATES_RESPONSE, parse_float=Decimal)['rates']

FIXER_IO_RESPONSE = '''{
    "success":true,
    "timestamp":1522788248,
    "base":"EUR",
    "date":"2018-04-03",
    "rates":{"USD":1.227439,"NOK":9.624334,"SEK":10.300293}
}'''


@pytest.fixture()
def rates_response():
    response = Mock()
    response.read.return_value = OPENEXCHANGERATES_RESPONSE
    with patch('djmoney.contrib.exchange.backends.base.urlopen', return_value=response):
        yield


@pytest.mark.usefixtures('rates_response')
class ExchangeTest:

    def assert_rates(self):
        backend = ExchangeBackend.objects.get()
        assert Rate.objects.count() == len(EXPECTED_RATES)
        for currency, rate in EXPECTED_RATES.items():
            assert Rate.objects.filter(currency=currency, value=rate, backend=backend)
