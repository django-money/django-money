from decimal import Decimal

from django.core.exceptions import ImproperlyConfigured

import pytest

from djmoney.contrib.exchange.exceptions import MissingRate
from djmoney.contrib.exchange.models import Rate, convert_money, get_rate
from djmoney.money import Money


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize('source, target, expected', (
    ('USD', 'USD', 1),
    ('USD', 'EUR', 2),
    ('EUR', 'USD', Decimal('0.5')),
))
def test_get_rate(backend, source, target, expected):
    Rate.objects.create(currency='EUR', value=2, backend=backend)
    assert get_rate(source, target) == expected


def test_unknown_currency():
    with pytest.raises(MissingRate, matches='Rate USD -> EUR does not exist'):
        get_rate('USD', 'EUR')


def test_bad_configuration(settings):
    settings.INSTALLED_APPS.remove('djmoney.contrib.exchange')
    with pytest.raises(ImproperlyConfigured):
        convert_money(Money(1, 'USD'), 'EUR')
