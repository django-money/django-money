from __future__ import unicode_literals
from warnings import warn

from django.core import validators
from django.forms import MultiValueField, DecimalField, ChoiceField
from moneyed.classes import Money

from .widgets import MoneyWidget, CURRENCY_CHOICES


__all__ = ('MoneyField',)


class MoneyField(MultiValueField):

    # Django 1.5 compat:
    if not hasattr(MultiValueField, 'empty_values'):
        empty_values = list(validators.EMPTY_VALUES)

    def __init__(self, currency_widget=None, currency_choices=CURRENCY_CHOICES, choices=CURRENCY_CHOICES,
                 max_value=None, min_value=None,
                 max_digits=None, decimal_places=None, *args, **kwargs):
        if currency_choices != CURRENCY_CHOICES:
            warn('currency_choices will be deprecated in favor of choices', PendingDeprecationWarning)
            choices = currency_choices
        decimal_field = DecimalField(max_value, min_value, max_digits, decimal_places, *args, **kwargs)
        choice_field = ChoiceField(choices=currency_choices)
        self.widget = currency_widget if currency_widget else MoneyWidget(amount_widget=decimal_field.widget,
                                                                          currency_widget=choice_field.widget)
        fields = (decimal_field, choice_field)
        super(MoneyField, self).__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        if data_list:
            if not self.required and data_list[0] in self.empty_values:
                return None
            else:
                return Money(*data_list[:2])
        return None

    def _has_changed(self, initial, data):
        # ChoiceField._has_changed returns True always here, so we rely solely
        # on the DecimalField. Based on MultiValueField.
        if initial is None:
            initial = ['' for x in range(0, len(data))]
        else:
            if not isinstance(initial, list):
                initial = self.widget.decompress(initial)
        return self.fields[0]._has_changed(initial[0], data[0])
