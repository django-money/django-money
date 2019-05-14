from django.contrib.admin import site

import pytest

from djmoney.contrib.exchange.admin import RateAdmin
from djmoney.contrib.exchange.models import Rate


pytestmark = pytest.mark.django_db


def test_last_update(backend):
    rate = Rate(currency="NOK", value=5, backend=backend)
    assert RateAdmin(Rate, site).last_update(rate) == backend.last_update
