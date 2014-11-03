import operator

from django.conf import settings
from django.forms import TextInput, Select, MultiWidget
from moneyed import CURRENCIES, DEFAULT_CURRENCY_CODE

__all__ = ('MoneyWidget', )

PROJECT_CURRENCIES = getattr(settings, 'CURRENCIES', None)

if PROJECT_CURRENCIES:
    CURRENCY_CHOICES = [(code, CURRENCIES[code].name) for code in
                        PROJECT_CURRENCIES]
else:
    CURRENCY_CHOICES = [(c.code, c.name) for i, c in CURRENCIES.items() if
                        c.code != DEFAULT_CURRENCY_CODE]

CURRENCY_CHOICES.sort(key=operator.itemgetter(1))


class MoneyWidget(MultiWidget):
    def __init__(self, choices=CURRENCY_CHOICES, amount_widget=None, currency_widget=None, *args, **kwargs):
        if not amount_widget:
            amount_widget = TextInput
        if not currency_widget:
            currency_widget = Select(choices=choices)
        widgets = (amount_widget, currency_widget)
        super(MoneyWidget, self).__init__(widgets, *args, **kwargs)

    def decompress(self, value):
        if value:
            return [value.amount, value.currency]
        return [None, None]
