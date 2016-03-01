# -*- coding: utf-8 -*-
from decimal import Decimal

import pytest
from moneyed import Money

from tests.testapp.models import InheritorModel, ModelWithDefaultAsInt

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


@pytest.fixture
def m2m_object():
    return ModelWithDefaultAsInt.objects.create(money=Money(100, 'USD'))


@pytest.fixture
def concrete_instance(m2m_object):
    instance = InheritorModel.objects.create()
    instance.m2m_field.add(m2m_object)
    return instance
