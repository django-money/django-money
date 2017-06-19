# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from warnings import warn

from django import VERSION
from django.core import validators
from django.core.exceptions import ValidationError
from django.forms import ChoiceField, DecimalField, MultiValueField

from moneyed.classes import Money

from ..settings import CURRENCY_CHOICES
from .widgets import MoneyWidget


__all__ = ('MoneyField',)


class MoneyField(MultiValueField):

    # Django 1.5 compat:
    if not hasattr(MultiValueField, 'empty_values'):
        empty_values = list(validators.EMPTY_VALUES)

    def __init__(self, currency_widget=None, currency_choices=CURRENCY_CHOICES,
                 choices=CURRENCY_CHOICES, max_value=None, min_value=None,
                 max_digits=None, decimal_places=None, default_amount=None,
                 *args, **kwargs):

        # choices does not make sense in this context, it would mean we had
        # to replace two widgets with one widget dynamically... which is a
        # mess. Instead, we let currency_choices be the same as choices and
        # raise a warning.
        if currency_choices != CURRENCY_CHOICES:
            warn('currency_choices will be deprecated in favor of choices', PendingDeprecationWarning)
            choices = currency_choices

        # get the default currency if one was specified
        default_currency = kwargs.pop('default_currency', None)

        amount_field = DecimalField(
            *args, max_value=max_value, min_value=min_value, max_digits=max_digits, decimal_places=decimal_places,
            **kwargs
        )
        currency_field = ChoiceField(choices=choices)

        if VERSION < (1, 8) and hasattr(amount_field, '_has_changed') and hasattr(currency_field, '_has_changed'):
            amount_field.has_changed = amount_field._has_changed
            currency_field.has_changed = currency_field._has_changed

        # TODO: No idea what currency_widget is supposed to do since it doesn't
        # even receive currency choices as input. Somehow it's supposed to be
        # instantiated from outside. Hard to tell.
        if currency_widget:
            self.widget = currency_widget
        else:
            self.widget = MoneyWidget(
                amount_widget=amount_field.widget,
                currency_widget=currency_field.widget,
                default_currency=default_currency
            )
        # The two fields that this widget comprises
        fields = (amount_field, currency_field)
        super(MoneyField, self).__init__(fields, *args, **kwargs)

        # set the initial value to the default currency so that the
        # default currency appears as the selected menu item
        self.initial = [default_amount, default_currency]

    def compress(self, data_list):
        if data_list:
            if not self.required and data_list[0] in self.empty_values:
                return None
            else:
                return Money(*data_list[:2])
        return None

    def has_changed(self, initial, data):  # noqa
        if initial is None:
            initial = ['' for x in range(0, len(data))]
        else:
            if not isinstance(initial, list):
                initial = self.widget.decompress(initial)

        amount_field, currency_field = self.fields
        amount_initial, currency_initial = initial

        # We treat the amount and currency fields slightly
        # differently: if the amount has changed, then we definitely
        # consider the money value to have changed. If the currency
        # has changed, but the amount is *empty* then we do not
        # consider the money value to have changed. This means that it
        # plays nicely with empty formrows in formsets.
        try:
            amount_data = data[0]
        except IndexError:
            amount_data = None

        try:
            amount_initial = amount_field.to_python(amount_initial)
        except ValidationError:
            return True
        if amount_field.has_changed(amount_initial, amount_data):
            return True

        try:
            currency_data = data[1]
        except IndexError:
            currency_data = None

        try:
            currency_initial = currency_field.to_python(currency_initial)
        except ValidationError:
            return True
        # If the currency is valid, has changed and there is some
        # amount data, then the money value has changed.
        if currency_field.has_changed(currency_initial, currency_data) and amount_data:
            return True

        return False

    if VERSION < (1, 8):
        _has_changed = has_changed
