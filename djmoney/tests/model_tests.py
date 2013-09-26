'''
Created on May 7, 2011

@author: jake
'''

from django.test import TestCase
from moneyed import Money
from testapp.models import (ModelWithVanillaMoneyField,
    ModelRelatedToModelWithMoney, ModelWithChoicesMoneyField, BaseModel, InheritedModel, NullMoneyFieldModel)
import moneyed


class VanillaMoneyFieldTestCase(TestCase):

    def testSaving(self):

        somemoney = Money("100.0")

        model = ModelWithVanillaMoneyField(money=somemoney)
        model.save()

        retrieved = ModelWithVanillaMoneyField.objects.get(pk=model.pk)

        self.assertEquals(somemoney.currency, retrieved.money.currency)
        self.assertEquals(somemoney, retrieved.money)

        # Try setting the value directly
        retrieved.money = Money(1, moneyed.DKK)
        retrieved.save()
        retrieved = ModelWithVanillaMoneyField.objects.get(pk=model.pk)

        self.assertEquals(Money(1, moneyed.DKK), retrieved.money)

    def testExactMatch(self):

        somemoney = Money("100.0")

        model = ModelWithVanillaMoneyField()
        model.money = somemoney

        model.save()

        retrieved = ModelWithVanillaMoneyField.objects.get(money=somemoney)

        self.assertEquals(model.pk, retrieved.pk)

    def testRangeSearch(self):

        minMoney = Money("3")

        model = ModelWithVanillaMoneyField(money=Money("100.0"))

        model.save()

        retrieved = ModelWithVanillaMoneyField.objects.get(money__gt=minMoney)
        self.assertEquals(model.pk, retrieved.pk)

        shouldBeEmpty = ModelWithVanillaMoneyField.objects.filter(money__lt=minMoney)
        self.assertEquals(shouldBeEmpty.count(), 0)

    def testCurrencySearch(self):

        otherMoney = Money("1000", moneyed.USD)
        correctMoney = Money("1000", moneyed.ZWN)

        model = ModelWithVanillaMoneyField(money=Money("100.0", moneyed.ZWN))
        model.save()

        shouldBeEmpty = ModelWithVanillaMoneyField.objects.filter(money__lt=otherMoney)
        self.assertEquals(shouldBeEmpty.count(), 0)

        shouldBeOne = ModelWithVanillaMoneyField.objects.filter(money__lt=correctMoney)
        self.assertEquals(shouldBeOne.count(), 1)


    def testCurrencyChoices(self):

        otherMoney = Money("1000", moneyed.USD)
        correctMoney = Money("1000", moneyed.ZWN)

        model = ModelWithChoicesMoneyField(
            money = Money("100.0", moneyed.ZWN)
        )
        model.save()

        shouldBeEmpty = ModelWithChoicesMoneyField.objects.filter(money__lt=otherMoney)
        self.assertEquals(shouldBeEmpty.count(), 0)

        shouldBeOne = ModelWithChoicesMoneyField.objects.filter(money__lt=correctMoney)
        self.assertEquals(shouldBeOne.count(), 1)

        model = ModelWithChoicesMoneyField(
            money = Money("100.0", moneyed.USD)
        )
        model.save()

        # Non-handled currency
        model = ModelWithChoicesMoneyField(
            money = Money("100.0", moneyed.DKK)
        )
        model.save()

    def testIsNullLookup(self):

        null_instance = NullMoneyFieldModel.objects.create(field=None)
        null_instance.save()

        normal_instance = NullMoneyFieldModel.objects.create(field=Money(100, 'USD'))
        normal_instance.save()

        shouldBeOne = NullMoneyFieldModel.objects.filter(field=None)
        self.assertEquals(shouldBeOne.count(), 1)


class RelatedModelsTestCase(TestCase):

    def testFindModelsRelatedToMoneyModels(self):

        moneyModel = ModelWithVanillaMoneyField(money=Money("100.0", moneyed.ZWN))
        moneyModel.save()

        relatedModel = ModelRelatedToModelWithMoney(moneyModel=moneyModel)
        relatedModel.save()

        ModelRelatedToModelWithMoney.objects.get(moneyModel__money=Money("100.0", moneyed.ZWN))
        ModelRelatedToModelWithMoney.objects.get(moneyModel__money__lt=Money("1000.0", moneyed.ZWN))


class InheritedModelTestCase(TestCase):

    def testBaseModel(self):
        self.assertEqual(BaseModel.objects.model, BaseModel)

    def testInheritedModel(self):
        self.assertEqual(InheritedModel.objects.model, InheritedModel)
