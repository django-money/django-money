# -*- encoding: utf-8
from moneyed import test_moneyed_classes
from djmoney.models.fields import MoneyPatched


class TestDjangoMoney(test_moneyed_classes.TestMoney):

    # MoneyPatched localizes to 'en_US', removing "US" from the default
    # py-moneyed prefix, 'US$'. This breaks py-moneyed's test_str.
    def test_str(self):
        assert str(self.one_million_bucks) == '$1,000,000.00'

# replace class "Money" a class "MoneyPath"
test_moneyed_classes.Money = MoneyPatched

TestCurrency = test_moneyed_classes.TestCurrency

TestMoney = TestDjangoMoney
