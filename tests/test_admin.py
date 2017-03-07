# coding: utf-8
from __future__ import unicode_literals

from django import VERSION

import pytest

from djmoney._compat import admin_utils
from moneyed import Money

from .testapp.models import ModelWithVanillaMoneyField


def get_args(value):
    """
    Constructs arguments for `display_for_field`.
    """
    field = ModelWithVanillaMoneyField._meta.get_field('money')
    if VERSION < (1, 7):
        return value, field
    return value, field, ''


@pytest.mark.parametrize('value, kwargs, expected', (
    (Money(10, 'RUB'), {}, 'руб.10.00'),  # Issue 232
    (Money(1234), {'USE_L10N': True, 'USE_THOUSAND_SEPARATOR': True}, '1,234.00 XYZ'),  # Issue 220
    (Money(1000, 'SAR'), {'USE_I18N': True, 'LANGUAGE_CODE': 'en-us'}, 'ر.س1,000.00'),  # Issue 196
    (Money(1000, 'PLN'), {}, '1,000.00 zł'),  # Issue 102
    (Money('3.33', 'EUR'), {'USE_I18N': True, 'LANGUAGE_CODE': 'de-de'}, '3.33 €'),  # Issue 90
))
def test_display_for_field(settings, value, kwargs, expected):
    for k, v in kwargs.items():
        setattr(settings, k, v)
    assert admin_utils.display_for_field(*get_args(value)) == expected
