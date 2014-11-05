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

    # Needed for Django 1.5.x, where Field doesn't have the '_has_changed' method.
    # But it mustn't run on Django 1.6, where it doesn't work and isn't needed.

    if hasattr(TextInput, '_has_changed'):
        def _has_changed(self, initial, data):
            # Rely on the amount widget, not the currency widget.
            if initial is None:
                initial = ['' for x in range(0, len(data))]
            else:
                if not isinstance(initial, list):
                    initial = self.decompress(initial)
            return self.widgets[0]._has_changed(initial[0], data[0])
