'''
Created on May 7, 2011

@author: jake
'''
from django.test import TestCase
from django.db.models import F
from moneyed import Money
from .testapp.models import (ModelWithVanillaMoneyField,
    ModelRelatedToModelWithMoney, ModelWithChoicesMoneyField, BaseModel, InheritedModel, InheritorModel,
    SimpleModel, NullMoneyFieldModel)
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

    def testRelativeAddition(self):
        # test relative value adding
        somemoney = Money(100, 'USD')
        mymodel = ModelWithVanillaMoneyField.objects.create(money=somemoney)
        # duplicate money
        mymodel.money = F('money') + somemoney
        mymodel.save()
        mymodel = ModelWithVanillaMoneyField.objects.get(pk=mymodel.pk)
        self.assertEquals(mymodel.money, 2 * somemoney)
        # subtract everything.
        mymodel.money = F('money') - (2 * somemoney)
        mymodel.save()
        mymodel = ModelWithVanillaMoneyField.objects.get(pk=mymodel.pk)
        self.assertEquals(Money(0, 'USD'), mymodel.money)

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
            money=Money("100.0", moneyed.ZWN)
        )
        model.save()

        shouldBeEmpty = ModelWithChoicesMoneyField.objects.filter(money__lt=otherMoney)
        self.assertEquals(shouldBeEmpty.count(), 0)

        shouldBeOne = ModelWithChoicesMoneyField.objects.filter(money__lt=correctMoney)
        self.assertEquals(shouldBeOne.count(), 1)

        model = ModelWithChoicesMoneyField(
            money=Money("100.0", moneyed.USD)
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
    """Test inheritence from a concrete model"""

    def testBaseModel(self):
        self.assertEqual(BaseModel.objects.model, BaseModel)

    def testInheritedModel(self):
        self.assertEqual(InheritedModel.objects.model, InheritedModel)
        moneyModel = InheritedModel(
            first_field=Money("100.0", moneyed.ZWN),
            second_field=Money("200.0", moneyed.USD),
        )
        moneyModel.save()
        self.assertEqual(moneyModel.first_field, Money(100.0, moneyed.ZWN))
        self.assertEqual(moneyModel.second_field, Money(200.0, moneyed.USD))


class InheritorModelTestCase(TestCase):
    """Test inheritence from an ABSTRACT model"""

    def testInheritorModel(self):
        self.assertEqual(InheritorModel.objects.model, InheritorModel)
        moneyModel = InheritorModel(
            price1=Money("100.0", moneyed.ZWN),
            price2=Money("200.0", moneyed.USD),
        )
        moneyModel.save()
        self.assertEqual(moneyModel.price1, Money(100.0, moneyed.ZWN))
        self.assertEqual(moneyModel.price2, Money(200.0, moneyed.USD))


class ManagerTest(TestCase):

    def test_manager(self):
        self.assertTrue(hasattr(SimpleModel, 'objects'))

    def test_objects_creation(self):
        SimpleModel.objects.create(money=Money("100.0", 'USD'))
        self.assertEqual(SimpleModel.objects.count(), 1)
