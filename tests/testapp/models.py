'''
Created on May 7, 2011

@author: jake
'''

from djmoney.models.fields import MoneyField
from djmoney.models.managers import MoneyManager
from django.db import models

class ModelWithVanillaMoneyField(models.Model):
    
    money = MoneyField(max_digits=10, decimal_places=2)
    
    objects = MoneyManager()
    
    
    