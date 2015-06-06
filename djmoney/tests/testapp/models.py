'''
Created on May 7, 2011

@author: jake
'''

from djmoney.models.fields import MoneyField
from django.db import models

import moneyed
from decimal import Decimal


class ModelWithVanillaMoneyField(models.Model):
    money = MoneyField(max_digits=10, decimal_places=2)

class ModelWithDefaultAsInt(models.Model):
    money = MoneyField(default=123, max_digits=10, decimal_places=2, default_currency='GHS')

class ModelWithDefaultAsStringWithCurrency(models.Model):
    money = MoneyField(default='123 USD', max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'model_default_string_currency'

class ModelWithDefaultAsString(models.Model):
    money = MoneyField(default='123', max_digits=10, decimal_places=2, default_currency='PLN')

class ModelWithDefaultAsFloat(models.Model):
    money = MoneyField(default=12.05, max_digits=10, decimal_places=2, default_currency='PLN')

class ModelWithDefaultAsDecimal(models.Model):
    money = MoneyField(default=Decimal('0.01'), max_digits=10, decimal_places=2, default_currency='CHF')

class ModelWithDefaultAsMoney(models.Model):
    money = MoneyField(default=moneyed.Money('0.01', 'RUB'), max_digits=10, decimal_places=2)

class ModelWithTwoMoneyFields(models.Model):
    amount1 = MoneyField(max_digits=10, decimal_places=2)
    amount2 = MoneyField(max_digits=10, decimal_places=3)

class ModelRelatedToModelWithMoney(models.Model):
    moneyModel = models.ForeignKey(ModelWithVanillaMoneyField)


class ModelWithChoicesMoneyField(models.Model):
    money = MoneyField(
        max_digits=10,
        decimal_places=2,
        currency_choices=[
            (moneyed.USD, 'US Dollars'),
            (moneyed.ZWN, 'Zimbabwian')
        ],
    )


class ModelWithNonMoneyField(models.Model):
    money = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')
    desc = models.CharField(max_length=10)


class AbstractModel(models.Model):
    price1 = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')

    class Meta:
        abstract = True


class InheritorModel(AbstractModel):
    price2 = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')


class RevisionedModel(models.Model):
    amount = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')

import reversion
reversion.register(RevisionedModel)


class BaseModel(models.Model):
    first_field = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')


class InheritedModel(BaseModel):
    second_field = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')


class SimpleModel(models.Model):
    money = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')


class NullMoneyFieldModel(models.Model):
    field = MoneyField(max_digits=10, decimal_places=2, null=True)


class ProxyModel(SimpleModel):
    class Meta:
        proxy = True
