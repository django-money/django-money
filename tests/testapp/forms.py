# -*- coding: utf-8 -*-
"""
Created on May 15, 2011

@author: jake
"""
from __future__ import unicode_literals

from django import forms

from djmoney.forms import MoneyField

from .models import (
    ModelWithDefaultAsString,
    ModelWithValidation,
    ModelWithVanillaMoneyField,
    NullMoneyFieldModel,
    PositiveValidatedMoneyModel,
    ValidatedMoneyModel,
)


class MoneyForm(forms.Form):
    money = MoneyField(currency_choices=[('SEK', 'Swedish Krona')], max_value=1000, min_value=2)


class MoneyFormMultipleCurrencies(forms.Form):
    money = MoneyField(currency_choices=[('SEK', 'Swedish Krona'), ('EUR', 'Euro')], max_value=1000, min_value=2)


class OptionalMoneyForm(forms.Form):
    money = MoneyField(required=False, currency_choices=[('SEK', 'Swedish Krona')])


class MoneyModelForm(forms.ModelForm):

    class Meta:
        model = ModelWithVanillaMoneyField
        fields = ('money',)


class NullableModelForm(forms.ModelForm):

    class Meta:
        model = NullMoneyFieldModel
        fields = ('field', )


class DefaultMoneyModelForm(forms.ModelForm):

    class Meta:
        model = ModelWithDefaultAsString
        fields = ('money', )


class MoneyModelFormWithValidation(forms.ModelForm):

    class Meta:
        model = ModelWithValidation
        fields = ('balance', )


class ValidatedMoneyModelForm(forms.ModelForm):

    class Meta:
        model = ValidatedMoneyModel
        fields = ('money', )


class PositiveValidatedMoneyModelForm(forms.ModelForm):

    class Meta:
        model = PositiveValidatedMoneyModel
        fields = ('money', )
