# coding: utf-8
from djmoney.money import Money


def test_float():
    assert float(Money(10, 'USD')) == 10.0


def test_repr():
    assert repr(Money('10.5', 'USD')) == '10 USD'
