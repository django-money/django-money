'''
Created on May 7, 2011

@author: jake
'''

from djmoney.models.fields import MoneyField
from django.db import models

import moneyed

class ModelWithVanillaMoneyField(models.Model):

    money = MoneyField(max_digits=10, decimal_places=2)


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


class AbstractModel(models.Model):
    price = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')
    class Meta:
        abstract = True


class InheritorModel(AbstractModel):
    name = models.CharField(max_length=50)


class NullMoneyFieldModel(models.Model):
    field = MoneyField(max_digits=10, decimal_places=2, null=True)

class BaseModel(models.Model):
    first_field = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')


class InheritedModel(BaseModel):
    second_field = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')
