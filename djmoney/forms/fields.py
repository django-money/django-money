from __future__ import unicode_literals
from warnings import warn

from django.forms import MultiValueField, DecimalField, ChoiceField
from moneyed.classes import Money

from .widgets import MoneyWidget, CURRENCY_CHOICES


__all__ = ('MoneyField',)


class MoneyField(MultiValueField):
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
        try:
            if data_list[0] is None:
                return None
        except IndexError:
            return None
        return Money(*data_list[:2])
