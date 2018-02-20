# -*- coding: utf-8 -*-
from decimal import Decimal

from django import VERSION

import pytest

from djmoney.money import Money
from tests.testapp.models import InheritorModel, ModelWithDefaultAsInt

from ._compat import patch


@pytest.yield_fixture()
def patched_convert_money():
    """
    The `convert_money` function will always return amount * 0.88.
    """
    if VERSION != (1, 8):
        pytest.xfail('djmoney_rates supports only Django 1.8')

    def convert_money(amount, currency_from, currency_to):  # noqa
        return Money(amount * Decimal('0.88'), currency_to)

    with patch('djmoney_rates.utils.convert_money', side_effect=convert_money) as patched:
        yield patched


@pytest.fixture
def m2m_object():
    return ModelWithDefaultAsInt.objects.create(money=Money(100, 'USD'))


@pytest.fixture
def concrete_instance(m2m_object):
    instance = InheritorModel.objects.create()
    instance.m2m_field.add(m2m_object)
    return instance


pytest_plugins = 'pytester'


@pytest.fixture
def coveragerc(request, testdir):
    """
    Generates .coveragerc to be used to combine test results from different subprocesses.
    """
    data_file = '%s/.coverage.%s' % (request.config.rootdir, request.node.name)
    return testdir.makefile('.ini', coveragerc='''
    [run]
    branch = true
    data_file = %s

    [report]
    show_missing = true
    precision = 2
    exclude_lines = raise NotImplementedError
    ''' % data_file)
