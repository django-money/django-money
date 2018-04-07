# -*- coding: utf-8 -*-
import pytest

from djmoney.contrib.exchange.models import (
    ExchangeBackend,
    Rate,
    get_default_backend_name,
)
from djmoney.money import Money
from tests.testapp.models import InheritorModel, ModelWithDefaultAsInt


@pytest.fixture
def m2m_object():
    return ModelWithDefaultAsInt.objects.create(money=Money(100, 'USD'))


@pytest.fixture()
def backend():
    return ExchangeBackend.objects.create(name=get_default_backend_name(), base_currency='USD')


@pytest.fixture()
def autoconversion(backend, settings):
    settings.AUTO_CONVERT_MONEY = True
    Rate.objects.create(currency='EUR', value='0.88', backend=backend)


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
