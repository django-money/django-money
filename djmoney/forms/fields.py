from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from django import forms
from .widgets import InputMoneyWidget
from moneyed.classes import Money, CURRENCIES, DEFAULT_CURRENCY_CODE

__all__ = ('MoneyField',)


class MoneyField(forms.DecimalField):
    def __init__(self, currency_widget=None, currency_choices=CURRENCIES,
                 *args, **kwargs):
        widget = InputMoneyWidget(currency_widget=currency_widget,
                                  currency_choices=currency_choices)
        kwargs.setdefault('widget', widget)
        super(MoneyField, self).__init__(*args, **kwargs)

    def to_python(self, value):

        if value is None:
            return None
        if isinstance(value, Money):
            return value

        if not isinstance(value, tuple) or len(value) != 2:
            raise Exception(
                "Invalid money input, expected amount and currency, got: %s." % value)

        amount, currency = value
        if not currency:
            raise forms.ValidationError(_('Currency is missing'))

        if not isinstance(currency, basestring):
            raise forms.ValidationError(
                _("Unrecognized currency type '%s'." % currency))

        currency = currency.upper()
        if currency not in CURRENCIES or currency == DEFAULT_CURRENCY_CODE:
            raise forms.ValidationError(
                _("Unrecognized currency type '%s'." % currency))

        amount = super(MoneyField, self).to_python(amount)
        return Money(amount=amount, currency=currency)

    def validate(self, value):
        if value is None:
            return None
        if not isinstance(value, Money):
            raise Exception(
                "Invalid money input, expected Money object to validate.")

        super(MoneyField, self).validate(value.amount)
