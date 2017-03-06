# coding: utf-8
from __future__ import unicode_literals

from django.contrib.admin.utils import display_for_field

from moneyed import Money

from .testapp.models import ModelWithVanillaMoneyField


def test_display_for_field():
    field = ModelWithVanillaMoneyField._meta.get_field('money')
    assert display_for_field(Money(10, 'RUB'), field, '') == 'руб.10.00'
