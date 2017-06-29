# coding: utf-8
import sys

from django.utils.translation import override

import pytest

from djmoney.money import Money, get_current_locale


def test_float():
    assert float(Money(10, 'USD')) == 10.0


def test_repr():
    assert repr(Money('10.5', 'USD')) == '10 USD'


def test_default_mul():
    assert Money(10, 'USD') * 2 == Money(20, 'USD')


@pytest.mark.skipif(sys.version_info[0] == 2, reason='py-moneyed doesnt support division on Python 2')
def test_default_truediv():
    assert Money(10, 'USD') / 2 == Money(5, 'USD')


@pytest.mark.parametrize('locale, expected', (
    ('pl', 'PL_PL'),
    ('pl_PL', 'pl_PL'),
))
def test_get_current_locale(locale, expected):
    with override(locale):
        assert get_current_locale() == expected
