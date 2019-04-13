# coding: utf-8
import sys

from django.utils.translation import override

import pytest

from djmoney.money import Money, get_current_locale


def test_repr():
    assert repr(Money('10.5', 'USD')) == '<Money: 10.5 USD>'


def test_html_safe():
    assert Money('10.5', 'EUR').__html__() == u'10.50\xa0€'


def test_html_unsafe():
    class UnsafeMoney(Money):

        def __unicode__(self):
            return '<script>'

    assert UnsafeMoney().__html__() == '&lt;script&gt;'


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


@pytest.mark.skipif(
    sys.version_info[0] == 2,
    reason='round uses float on Python 2, which is a deprecated conversion for Money instances'
)
def test_round():
    assert round(Money('1.69', 'USD'), 1) == Money('1.7', 'USD')
