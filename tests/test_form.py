# -*- coding: utf-8 -*-
"""
Created on May 7, 2011

@author: jake
"""
from decimal import Decimal

from django import VERSION

import pytest

import moneyed
from djmoney.models.fields import MoneyField
from moneyed import Money

from .testapp.forms import (
    DefaultMoneyModelForm,
    MoneyForm,
    MoneyFormMultipleCurrencies,
    MoneyModelForm,
    NullableModelForm,
    OptionalMoneyForm,
)
from .testapp.models import ModelWithVanillaMoneyField, NullMoneyFieldModel


pytestmark = pytest.mark.django_db


@pytest.mark.xfail(VERSION[:3] == (1, 10, 1), reason='Bug in this Django version.', strict=True)
def test_save():
    money = Money(Decimal('10'), moneyed.SEK)
    form = MoneyModelForm({'money_0': money.amount, 'money_1': money.currency})

    assert form.is_valid()
    instance = form.save()

    retrieved = ModelWithVanillaMoneyField.objects.get(pk=instance.pk)
    assert money == retrieved.money


def test_validate():
    money = Money(Decimal('10'), moneyed.SEK)
    form = MoneyForm({'money_0': money.amount, 'money_1': money.currency})

    assert form.is_valid()

    result = form.cleaned_data['money']
    assert result == money


@pytest.mark.parametrize(
    'data',
    (
        {'money_0': 'xyz*|\\', 'money_1': moneyed.SEK},
        {'money_0': 10000, 'money_1': moneyed.SEK},
        {'money_0': 1, 'money_1': moneyed.SEK},
        {'money_0': 10, 'money_1': moneyed.EUR}
    )
)
def test_form_is_invalid(data):
    assert not MoneyForm(data).is_valid()


@pytest.mark.parametrize(
    'data, result',
    (
        ({'money_0': '', 'money_1': moneyed.SEK}, []),
        ({'money_0': '1.23', 'money_1': moneyed.SEK}, ['money']),
    )
)
def test_changed_data(data, result):
    assert MoneyForm(data).changed_data == result


def test_change_currency_not_amount():
    """
    If the amount is the same, but the currency changes, then we
    should consider this to be a change.
    """
    form = MoneyFormMultipleCurrencies(
        {'money_0': Decimal(10), 'money_1': moneyed.EUR},
        initial={'money': Money(Decimal(10), moneyed.SEK)}
    )
    assert form.changed_data == ['money']


@pytest.mark.parametrize(
    'data, result',
    (
        ({'money_1': moneyed.SEK}, True),
        ({'money_0': '', 'money_1': moneyed.SEK}, True),
        ({'money_0': 'xyz*|\\', 'money_1': moneyed.SEK}, False),
    )
)
def test_optional_money_form(data, result):
    """
    The currency widget means that 'money_1' will always be filled
    in, but 'money_0' could be absent/empty.
    """
    assert OptionalMoneyForm(data).is_valid() is result


def test_default_currency():
    """
    If field is nullable, then field's default_currency value should be selected by default.
    """
    instance = NullMoneyFieldModel.objects.create()
    form = NullableModelForm(instance=instance)
    if VERSION[:2] > (1, 10):
        expected = '<option value="USD" selected>US Dollar</option>'
    else:
        expected = '<option value="USD" selected="selected">US Dollar</option>'
    assert expected in form.as_p()


def test_fields_default_amount_becomes_forms_initial():
    """
    Formfield should take field's default amount
    and put it in form field's initial value
    """
    form = DefaultMoneyModelForm()
    assert form.fields['money'].initial == [123, 'PLN']


def test_no_deprecation_warning():
    """
    The library's code shouldn't generate any warnings itself. See #262.
    """
    with pytest.warns(None) as warning:
        MoneyField(max_digits=10, decimal_places=2, currency_choices=(('USD', 'USD'),)).formfield()
    assert not warning
