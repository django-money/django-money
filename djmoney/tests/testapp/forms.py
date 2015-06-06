'''
Created on May 15, 2011

@author: jake
'''

from django import forms
from djmoney.forms import MoneyField
from .models import ModelWithVanillaMoneyField


class MoneyForm(forms.Form):

    money = MoneyField(currency_choices=[(u'SEK', u'Swedish Krona')], max_value=1000, min_value=2)

class OptionalMoneyForm(forms.Form):

    money = MoneyField(required=False, currency_choices=[(u'SEK', u'Swedish Krona')])

class MoneyModelForm(forms.ModelForm):

    class Meta:
        model = ModelWithVanillaMoneyField
        fields = ('money',)
