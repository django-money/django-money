'''
Created on May 7, 2011

@author: jake
'''

from djmoney.models.fields import MoneyField
from django.db import models

class ModelWithVanillaMoneyField(models.Model):
    
    money = MoneyField(max_digits=10, decimal_places=2)
    
class ModelRelatedToModelWithMoney(models.Model):
    
    moneyModel = models.ForeignKey(ModelWithVanillaMoneyField)