# -*- encoding: utf-8
from moneyed import test_moneyed_classes
from djmoney.models.fields import MoneyPatched

# replace class "Money" a class "MoneyPath"
test_moneyed_classes.Money = MoneyPatched

TestCurrency = test_moneyed_classes.TestCurrency

TestMoney = test_moneyed_classes.TestMoney
