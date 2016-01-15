'''
Created on May 7, 2011

@author: jake
'''
from decimal import Decimal
from django.test import TestCase
from django.db.models import F, Q
try:
    from unittest import skipIf
except ImportError:
    # For python2.6 compatibility
    from unittest2 import skipIf
from moneyed import Money
from .testapp.models import (ModelWithVanillaMoneyField,
    ModelRelatedToModelWithMoney, ModelWithChoicesMoneyField, BaseModel, InheritedModel, InheritorModel,
    SimpleModel, NullMoneyFieldModel, ModelWithDefaultAsDecimal, ModelWithDefaultAsFloat, ModelWithDefaultAsInt,
    ModelWithDefaultAsString, ModelWithDefaultAsStringWithCurrency, ModelWithDefaultAsMoney, ModelWithTwoMoneyFields,
    ProxyModel, ModelWithNonMoneyField)
from djmoney.models.fields import MoneyPatched, AUTO_CONVERT_MONEY
import moneyed
from mock import patch


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

        object = BaseModel.objects.create()
        self.assertEquals(Money(0, 'USD'), object.first_field)
        object = BaseModel.objects.create(first_field='111.2')
        self.assertEquals(Money('111.2', 'USD'), object.first_field)
        object = BaseModel.objects.create(first_field=Money('123', 'PLN'))
        self.assertEquals(Money('123', 'PLN'), object.first_field)

        object = ModelWithDefaultAsDecimal.objects.create()
        self.assertEquals(Money('0.01', 'CHF'), object.money)
        object = ModelWithDefaultAsInt.objects.create()
        self.assertEquals(Money('123', 'GHS'), object.money)
        object = ModelWithDefaultAsString.objects.create()
        self.assertEquals(Money('123', 'PLN'), object.money)
        object = ModelWithDefaultAsStringWithCurrency.objects.create()
        self.assertEquals(Money('123', 'USD'), object.money)
        object = ModelWithDefaultAsFloat.objects.create()
        self.assertEquals(Money('12.05', 'PLN'), object.money)
        object = ModelWithDefaultAsMoney.objects.create()
        self.assertEquals(Money('0.01', 'RUB'), object.money)

    def testRounding(self):
        somemoney = Money("100.0623456781123219")

        model = ModelWithVanillaMoneyField(money=somemoney)
        model.save()

        retrieved = ModelWithVanillaMoneyField.objects.get(pk=model.pk)

        self.assertEquals(somemoney.currency, retrieved.money.currency)
        self.assertEquals(Money("100.06"), retrieved.money)

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
        # check that one cannot use different currencies with F()
        mymodel = ModelWithVanillaMoneyField.objects.get(pk=mymodel.pk)
        with self.assertRaises(ValueError):
            # this model has USD as a currency, therefore this should fail.
            mymodel.money = F('money') + Money(100, 'EUR')

    def testComparisonLookup(self):
        ModelWithTwoMoneyFields.objects.create(amount1=Money(1, 'USD'), amount2=Money(2, 'USD'))
        ModelWithTwoMoneyFields.objects.create(amount1=Money(2, 'USD'), amount2=Money(0, 'USD'))
        ModelWithTwoMoneyFields.objects.create(amount1=Money(3, 'USD'), amount2=Money(0, 'USD'))
        ModelWithTwoMoneyFields.objects.create(amount1=Money(4, 'USD'), amount2=Money(0, 'GHS'))
        ModelWithTwoMoneyFields.objects.create(amount1=Money(5, 'USD'), amount2=Money(5, 'USD'))

        qs = ModelWithTwoMoneyFields.objects.filter(amount1=F('amount2'))
        self.assertEquals(1, qs.count())

        qs = ModelWithTwoMoneyFields.objects.filter(amount1__gt=F('amount2'))
        # should yield 2 USD, 3 USD, but not 4 GHS (different currency)
        self.assertEquals(2, qs.count())

        qs = ModelWithTwoMoneyFields.objects.filter(Q(amount1=Money(1, 'USD')) | Q(amount2=Money(0, 'USD')))
        self.assertEquals(3, qs.count())

        qs = ModelWithTwoMoneyFields.objects.filter(Q(amount1=Money(1, 'USD')) | Q(amount1=Money(4, 'USD')) | Q(amount2=Money(0, 'GHS')))
        self.assertEquals(2, qs.count())

        qs = ModelWithTwoMoneyFields.objects.filter(Q(amount1=Money(1, 'USD')) | Q(amount1=Money(5, 'USD')) | Q(amount2=Money(0, 'GHS')))
        self.assertEquals(3, qs.count())

        qs = ModelWithTwoMoneyFields.objects.filter(Q(amount1=Money(1, 'USD')) | Q(amount1=Money(4, 'USD'), amount2=Money(0, 'GHS')))
        self.assertEquals(2, qs.count())

        qs = ModelWithTwoMoneyFields.objects.filter(Q(amount1=Money(1, 'USD')) | Q(amount1__gt=Money(4, 'USD'), amount2=Money(0, 'GHS')))
        self.assertEquals(1, qs.count())

        qs = ModelWithTwoMoneyFields.objects.filter(Q(amount1=Money(1, 'USD')) | Q(amount1__gte=Money(4, 'USD'), amount2=Money(0, 'GHS')))
        self.assertEquals(2, qs.count())

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

    def testNullDefault(self):
        null_instance = NullMoneyFieldModel.objects.create()
        self.assertEquals(null_instance.field, None)

    def test_get_or_create_respects_currency(self):
        instance, created = ModelWithVanillaMoneyField.objects.get_or_create(
            money_currency='PLN'
        )

        self.assertEquals(str(instance.money.currency), 'PLN', 'currency should be taken into account in get_or_create')

        instance, created = ModelWithVanillaMoneyField.objects.get_or_create(
            money=Money(0, 'EUR')
        )

        self.assertEquals(str(instance.money.currency), 'EUR', 'currency should be taken into account in get_or_create')


class RelatedModelsTestCase(TestCase):

    def testFindModelsRelatedToMoneyModels(self):

        moneyModel = ModelWithVanillaMoneyField(money=Money("100.0", moneyed.ZWN))
        moneyModel.save()

        relatedModel = ModelRelatedToModelWithMoney(moneyModel=moneyModel)
        relatedModel.save()

        ModelRelatedToModelWithMoney.objects.get(moneyModel__money=Money("100.0", moneyed.ZWN))
        ModelRelatedToModelWithMoney.objects.get(moneyModel__money__lt=Money("1000.0", moneyed.ZWN))


class NonMoneyTestCase(TestCase):

    def testAllowExpressionNodesWithoutMoney(self):
        """ allow querying on expression nodes that are not Money """
        ModelWithNonMoneyField(money=Money(100.0), desc="hundred").save()
        instance = ModelWithNonMoneyField.objects.filter(desc=F("desc")).get()
        self.assertEqual(instance.desc, "hundred")


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


class ProxyModelTest(TestCase):

    def test_instances(self):
        ProxyModel.objects.create(money=Money("100.0", 'USD'))
        self.assertIsInstance(ProxyModel.objects.get(pk=1), ProxyModel)

    def test_patching(self):
        ProxyModel.objects.create(money=Money("100.0", 'USD'))
        # This will fail if ProxyModel.objects doesn't have the patched manager:
        self.assertEqual(ProxyModel.objects.filter(money__gt=Money("50.00", 'GBP')).count(),
                         0)


class DifferentCurrencyTestCase(TestCase):
    """Test sum/sub operations between different currencies"""

    @skipIf(AUTO_CONVERT_MONEY is False, "You need to install django-money-rates to run this test")
    def test_sum(self):
        with patch(
            'djmoney.models.fields.convert_money',
            side_effect=lambda amount, cur_from, cur_to: Money((amount * Decimal(0.88)), cur_to)
        ):
            result = MoneyPatched(10, 'EUR') + Money(1, 'USD')
            self.assertEqual(round(result.amount, 2), 10.88)
            self.assertEqual(result.currency, moneyed.EUR)

    @skipIf(AUTO_CONVERT_MONEY is False, "You need to install django-money-rates to run this test")
    def test_sub(self):
        with patch(
            'djmoney.models.fields.convert_money',
            side_effect=lambda amount, cur_from, cur_to: Money((amount * Decimal(0.88)), cur_to)
        ):
            result = MoneyPatched(10, 'EUR') - Money(1, 'USD')
            self.assertEqual(round(result.amount, 2), 9.23)
            self.assertEqual(result.currency, moneyed.EUR)

    def test_eq(self):
        self.assertEqual(MoneyPatched(1, 'EUR'), Money(1, 'EUR'))
        self.assertNotEqual(MoneyPatched(1, 'EUR'), Money(2, 'EUR'))
        with self.assertRaises(TypeError):
            MoneyPatched(10, 'EUR') == Money(10, 'USD')
