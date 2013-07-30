from django import forms
from django.conf import settings
from moneyed import Money, CURRENCIES, DEFAULT_CURRENCY_CODE
from decimal import Decimal
import operator

__all__ = ('InputMoneyWidget', 'CurrencySelectWidget',)

PROJECT_CURRENCIES = getattr(settings, 'CURRENCIES', None)

if PROJECT_CURRENCIES:
    CURRENCY_CHOICES = [(code, CURRENCIES[code].name) for code in
                        PROJECT_CURRENCIES]
else:
    CURRENCY_CHOICES = [(c.code, c.name) for i, c in CURRENCIES.items() if
                        c.code != DEFAULT_CURRENCY_CODE]

CURRENCY_CHOICES.sort(key=operator.itemgetter(1))


class CurrencySelectWidget(forms.Select):
    def __init__(self, attrs=None, choices=CURRENCY_CHOICES):
        super(CurrencySelectWidget, self).__init__(attrs, choices)


class InputMoneyWidget(forms.TextInput):
    def __init__(self, attrs=None, currency_widget=None,
                 default_currency=DEFAULT_CURRENCY_CODE,
                 currency_choices=CURRENCY_CHOICES):
        self.currency_widget = currency_widget or CurrencySelectWidget(choices=currency_choices)
        self.default_currency = default_currency
        super(InputMoneyWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        amount = ''
        currency = ''
        if isinstance(value, Money):
            amount = value.amount
            currency = value.currency.code
        if isinstance(value, tuple):
            amount = value[0]
            currency = value[1]
        if isinstance(value, int) or isinstance(value, Decimal):
            amount = value
            currency = self.default_currency

        result = super(InputMoneyWidget, self).render(name, amount, attrs)
        name += '_currency'
        attrs['id'] = 'id_' + name
        result += self.currency_widget.render(name, currency, attrs)

        return result

    def value_from_datadict(self, data, files, name):
        if not data.get(name, None):
            return None
        return Money(data.get(name, None), data.get(name + '_currency', None))
