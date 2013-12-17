'''
Created on May 7, 2011

@author: jake
'''
from decimal import Decimal

import moneyed
from django.test import TestCase
from moneyed import Money

from .testapp.forms import MoneyForm, MoneyModelForm
from .testapp.models import ModelWithVanillaMoneyField


class MoneyFormTestCase(TestCase):
    def testRender(self):
        form = MoneyForm()
        expected = """<tr><th><label for="id_money_0">Money:</label></th><td><input type="text" name="money_0" id="id_money_0" /><select name="money_1" id="id_money_1">
<option value="SEK">Swedish Krona</option>
</select></td></tr>"""
        self.assertHTMLEqual(str(form), expected)

    def testValidate(self):
        m = Money(Decimal(10), moneyed.SEK)

        form = MoneyForm({"money_0": m.amount, "money_1": m.currency})

        self.assertTrue(form.is_valid())

        result = form.cleaned_data['money']
        self.assertTrue(isinstance(result, Money))

        self.assertEquals(result.amount, Decimal("10"))
        self.assertEquals(result.currency, moneyed.SEK)
        self.assertEquals(result, m)

    def testAmountIsNotANumber(self):
        form = MoneyForm({"money_0": "xyz*|\\", "money_1": moneyed.SEK})
        self.assertFalse(form.is_valid())

    def testAmountExceedsMaxValue(self):
        form = MoneyForm({"money_0": 10000, "money_1": moneyed.SEK})
        self.assertFalse(form.is_valid())

    def testAmountExceedsMinValue(self):
        form = MoneyForm({"money_0": 1, "money_1": moneyed.SEK})
        self.assertFalse(form.is_valid())

    def testNonExistentCurrency(self):
        m = Money(Decimal(10), moneyed.EUR)
        form = MoneyForm({"money_0": m.amount, "money_1": m.currency})
        self.assertFalse(form.is_valid())


class MoneyModelFormTestCase(TestCase):
    def testSave(self):
        m = Money(Decimal("10"), moneyed.SEK)
        form = MoneyModelForm({"money_0": m.amount, "money_1": m.currency})

        self.assertTrue(form.is_valid())
        model = form.save()

        retrieved = ModelWithVanillaMoneyField.objects.get(pk=model.pk)
        self.assertEqual(m, retrieved.money)
