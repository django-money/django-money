from decimal import Decimal

import pytest

from djmoney.contrib.exchange.exceptions import MissingRate
from djmoney.contrib.exchange.models import Rate, get_rate


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
