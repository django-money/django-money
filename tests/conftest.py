# coding: utf-8
from decimal import Decimal

import pytest
from moneyed import Money

from ._compat import patch


@pytest.fixture
def patched_convert_money(request):
    patched = patch(
        'djmoney.models.fields.convert_money',
        side_effect=lambda amount, cur_from, cur_to: Money((amount * Decimal('0.88')), cur_to)
    )
    patched.start()
    request.addfinalizer(patched.stop)
    return patched.new
