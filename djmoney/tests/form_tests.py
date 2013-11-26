'''
Created on May 7, 2011

@author: jake
'''

import moneyed
from django.test import TestCase
from moneyed import Money
from decimal import Decimal
from .testapp.forms import MoneyForm, MoneyModelForm
from .testapp.models import ModelWithVanillaMoneyField


class MoneyFormTestCase(TestCase):

    def testRender(self):

        form = MoneyForm()
        expected = """<tr><th><label for="id_money">Money:</label></th><td><input id="id_money" name="money" type="text" /><select id="id_money_currency" name="money_currency">
<option value="a">a</option>
</select></td></tr>"""

        self.assertHTMLEqual(str(form), expected)

    def testValidate(self):

        form = MoneyForm({"money": "10", "money_currency": "SEK"})

        self.assertTrue(form.is_valid())

        result = form.cleaned_data['money']
        self.assertTrue(isinstance(result, Money))

        self.assertEquals(result.amount, Decimal("10"))
        self.assertEquals(result.currency, moneyed.SEK)

    def testNonExistentCurrency(self):

        form = MoneyForm({"money": "10", "money_currency": "_XX!123_"})

        self.assertRaises(moneyed.CurrencyDoesNotExist, form.is_valid)


class MoneyModelFormTestCase(TestCase):

    def testSave(self):
        form = MoneyModelForm({"money": "10", "money_currency": "SEK"})

        self.assertTrue(form.is_valid())
        model = form.save()

        retrieved = ModelWithVanillaMoneyField.objects.get(pk=model.pk)

        self.assertEqual(Money(10, moneyed.SEK), retrieved.money)
