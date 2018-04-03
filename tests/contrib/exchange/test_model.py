import pytest

from djmoney.contrib.exchange.exceptions import MissingRate
from djmoney.contrib.exchange.models import Rate, convert


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize('source, target, expected', (
    ('USD', 'USD', 50),
    ('USD', 'EUR', 100),
    ('EUR', 'USD', 25),
))
def test_convert(backend, source, target, expected):
    Rate.objects.create(currency='EUR', value=2, backend=backend)
    assert convert(50, source, target) == expected


def test_unknown_currency():
    with pytest.raises(MissingRate, matches='Rate USD -> EUR does not exist'):
        convert(5, 'USD', 'EUR')
