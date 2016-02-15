# -*- coding: utf-8 -*-
from decimal import Decimal

import pytest
from moneyed import Money

from ._compat import patch


@pytest.yield_fixture()
def patched_convert_money():
    """
    The `convert_money` function will always return amount * 0.88.
    """

    def convert_money(amount, currency_from, currency_to):  # noqa
        return Money(amount * Decimal('0.88'), currency_to)

    with patch('djmoney.models.fields.convert_money', side_effect=convert_money) as patched:
        yield patched
