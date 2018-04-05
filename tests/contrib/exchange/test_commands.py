from django.core.management import call_command

import pytest

from djmoney.contrib.exchange.backends.base import BaseExchangeBackend
from djmoney.contrib.exchange.models import Rate

from .conftest import ExchangeTest


pytestmark = pytest.mark.django_db


class FixBackend(BaseExchangeBackend):

    def get_rates(self, **params):
        return {'EUR': 1}


class TestCommand(ExchangeTest):

    def test_update_rates(self):
        call_command('update_rates')
        self.assert_rates()


def test_custom_backend():
    call_command('update_rates', backend=FixBackend.__module__ + '.' + FixBackend.__name__)
    assert Rate.objects.filter(currency='EUR', value=1).exists()
