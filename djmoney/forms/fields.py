from django.utils.translation import ugettext_lazy as _
from django import forms
from widgets import InputMoneyWidget
from moneyed.classes import Money, CURRENCIES

__all__ = ('MoneyField',)

class MoneyField(forms.DecimalField):
    
    def __init__(self, currency_widget=None, *args, **kwargs):
        self.widget = InputMoneyWidget(currency_widget=currency_widget)
        super(MoneyField, self).__init__(*args, **kwargs)
    
    def clean(self, value):
        if not isinstance(value, tuple):
            raise Exception("Invalid value provided for MoneyField.clean (expected tuple).")
        amount = super(MoneyField, self).clean(value[0])
        currency = value[1]
        if not currency:
            raise forms.ValidationError(_(u'Input currency'))
        currency = currency.upper()
        if not CURRENCIES.get(currency, False) or currency == u'XXX':
            raise forms.ValidationError(_(u"Unrecognized currency type '%s'." % currency))
        return Money(amount=amount, currency=currency)
