from __future__ import unicode_literals
from django.forms import MultiValueField, DecimalField, ChoiceField
from .widgets import MoneyWidget, CURRENCY_CHOICES
from moneyed.classes import Money

__all__ = ('MoneyField',)


class MoneyField(MultiValueField):
    def __init__(self, currency_widget=None, currency_choices=CURRENCY_CHOICES, max_value=None, min_value=None,
                 max_digits=None, decimal_places=None, *args, **kwargs):
        decimal_field = DecimalField(max_value, min_value, max_digits, decimal_places, *args, **kwargs)
        self.widget = currency_widget if currency_widget else MoneyWidget(choices=CURRENCY_CHOICES,
                                                                          amount_widget=decimal_field.widget)
        fields = (decimal_field, ChoiceField(choices=currency_choices))
        super(MoneyField, self).__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        return Money(*data_list[:2])