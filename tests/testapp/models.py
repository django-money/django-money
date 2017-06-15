# -*- coding: utf-8 -*-
"""
Created on May 7, 2011

@author: jake
"""
from decimal import Decimal

from django import VERSION
from django.db import models

import moneyed
from djmoney.models.fields import MoneyField
from djmoney.models.managers import money_manager, understands_money

from .._compat import register


class ModelWithVanillaMoneyField(models.Model):
    money = MoneyField(max_digits=10, decimal_places=2)
    second_money = MoneyField(max_digits=10, decimal_places=2, default_currency='EUR')
    integer = models.IntegerField(default=0)


class ModelWithDefaultAsInt(models.Model):
    money = MoneyField(default=123, max_digits=10, decimal_places=2, default_currency='GHS')


class ModelWithUniqueIdAndCurrency(models.Model):
    money = MoneyField(default=123, max_digits=10, decimal_places=2, default_currency='GHS')

    class Meta:
        unique_together = ('id', 'money')


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
    moneyModel = models.ForeignKey(ModelWithVanillaMoneyField, on_delete=models.CASCADE)


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
    money = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')
    m2m_field = models.ManyToManyField(ModelWithDefaultAsInt)

    class Meta:
        abstract = True


class InheritorModel(AbstractModel):
    second_field = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')


class RevisionedModel(models.Model):
    amount = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')


register(RevisionedModel)


class BaseModel(models.Model):
    money = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')


class InheritedModel(BaseModel):
    second_field = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')


class SimpleModel(models.Model):
    money = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')


class NullMoneyFieldModel(models.Model):
    field = MoneyField(max_digits=10, decimal_places=2, null=True, default_currency='USD', blank=True)


class ProxyModel(SimpleModel):

    class Meta:
        proxy = True


class MoneyManager(models.Manager):

    @understands_money
    def super_method(self, **kwargs):
        return self.filter(**kwargs)


class ModelWithCustomManager(models.Model):
    field = MoneyField(max_digits=10, decimal_places=2)

    manager = money_manager(MoneyManager())


class DateTimeModel(models.Model):
    field = MoneyField(max_digits=10, decimal_places=2)
    created = models.DateTimeField(null=True, blank=True)


if VERSION < (1, 7, 0):
    from djmoney.contrib.django_rest_framework import register_money_field
    from djmoney.admin import setup_admin_integration

    register_money_field()
    setup_admin_integration()


class ModelIssue300(models.Model):
    money = models.ForeignKey(DateTimeModel, on_delete=models.CASCADE)
    price = MoneyField(max_digits=10, decimal_places=2, default_currency='EUR', default=Decimal('0.0'))
