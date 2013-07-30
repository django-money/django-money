from decimal import Decimal
from django.utils.translation import ugettext_lazy as _
from django import forms
from widgets import InputMoneyWidget
from moneyed.classes import Money, CURRENCIES, DEFAULT_CURRENCY_CODE

__all__ = ('MoneyField',)


class MoneyField(forms.DecimalField):
    def __init__(self, currency_widget=None, currency_choices=CURRENCIES,
                 *args, **kwargs):
        self.widget = InputMoneyWidget(currency_widget=currency_widget,
                                       currency_choices=currency_choices)
        super(MoneyField, self).__init__(*args, **kwargs)

    def to_python(self, value):

        if value is None:
            return None
        if isinstance(value, Money):
            return value

        if not isinstance(value, tuple):
            raise Exception(
                "Invalid money input, expected amount and currency, got: %s." % value)

        amount = super(MoneyField, self).to_python(value[0])

        currency = value[1]
        if not currency:
            raise forms.ValidationError(_(u'Currency is missing'))
        currency = currency.upper()
        if not CURRENCIES.get(currency,
                              False) or currency == DEFAULT_CURRENCY_CODE:
            raise forms.ValidationError(
                _(u"Unrecognized currency type '%s'." % currency))
        return Money(amount=amount, currency=currency)

    def validate(self, value):
        if value is None:
            return None
        if not isinstance(value, Money):
            raise Exception(
                "Invalid money input, expected Money object to validate.")

        super(MoneyField, self).validate(value.amount)
