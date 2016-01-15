# coding=utf-8
"""
Created on May 7, 2011

@author: jake
"""
from decimal import Decimal

from django.db.models import F, Q

import moneyed
import pytest
from moneyed import Money

from djmoney.models.fields import AUTO_CONVERT_MONEY, MoneyPatched

from .testapp.models import (
    BaseModel,
    InheritedModel,
    InheritorModel,
    ModelRelatedToModelWithMoney,
    ModelWithChoicesMoneyField,
    ModelWithDefaultAsDecimal,
    ModelWithDefaultAsFloat,
    ModelWithDefaultAsInt,
    ModelWithDefaultAsMoney,
    ModelWithDefaultAsString,
    ModelWithDefaultAsStringWithCurrency,
    ModelWithNonMoneyField,
    ModelWithTwoMoneyFields,
    ModelWithVanillaMoneyField,
    NullMoneyFieldModel,
    ProxyModel,
    SimpleModel,
)


pytestmark = pytest.mark.django_db


class TestVanillaMoneyField:

    @pytest.mark.parametrize(
        'model_class, kwargs, expected',
        (
            (ModelWithVanillaMoneyField, {'money': Money('100.0')}, Money('100.0')),
            (BaseModel, {}, Money(0, 'USD')),
            (BaseModel, {'money': '111.2'}, Money('111.2', 'USD')),
            (BaseModel, {'money': Money('123', 'PLN')}, Money('123', 'PLN')),
            (ModelWithDefaultAsMoney, {}, Money('0.01', 'RUB')),
            (ModelWithDefaultAsFloat, {}, Money('12.05', 'PLN')),
            (ModelWithDefaultAsStringWithCurrency, {}, Money('123', 'USD')),
            (ModelWithDefaultAsString, {}, Money('123', 'PLN')),
            (ModelWithDefaultAsInt, {}, Money('123', 'GHS')),
            (ModelWithDefaultAsDecimal, {}, Money('0.01', 'CHF')),
        )
    )
    def test_create_defaults(self, model_class, kwargs, expected):
        instance = model_class.objects.create(**kwargs)
        assert instance.money == expected

        retrieved = model_class.objects.get(pk=instance.pk)
        assert retrieved.money == expected

    def test_save_new_value(self):
        instance = ModelWithVanillaMoneyField.objects.create(money=(Money('100.0')))
        retrieved = ModelWithVanillaMoneyField.objects.get(pk=instance.pk)

        # Try setting the value directly
        retrieved.money = Money(1, moneyed.DKK)
        retrieved.save()
        retrieved = ModelWithVanillaMoneyField.objects.get(pk=instance.pk)

        assert retrieved.money == Money(1, moneyed.DKK)

    def test_rounding(self):
        money = Money('100.0623456781123219')

        instance = ModelWithVanillaMoneyField.objects.create(money=money)
        # TODO. Should instance.money be rounded too?

        retrieved = ModelWithVanillaMoneyField.objects.get(pk=instance.pk)

        assert retrieved.money == Money('100.06')

    @pytest.mark.parametrize(
        'f_obj, expected',
        (
            (F('money') + Money(100, 'USD'), Money(200, 'USD')),
            (F('money') - Money(100, 'USD'), Money(0, 'USD')),
            (F('money') * 2, Money(200, 'USD')),
            (F('money') * F('integer'), Money(200, 'USD')),
            (F('money') / 2, Money(50, 'USD')),
            (F('money') / F('integer'), Money(50, 'USD')),
            (F('money') + F('money'), Money(200, 'USD')),
            (F('money') - F('money'), Money(0, 'USD')),
        )
    )
    def test_f_queries(self, f_obj, expected):
        instance = ModelWithVanillaMoneyField.objects.create(money=Money(100, 'USD'), integer=2)
        instance.money = f_obj
        instance.save()
        instance = ModelWithVanillaMoneyField.objects.get(pk=instance.pk)
        assert instance.money == expected

    def test_different_currencies(self):
        instance = ModelWithVanillaMoneyField.objects.create(money=Money(100, 'USD'))
        # check that one cannot use different currencies with F()
        with pytest.raises(ValueError):
            # this model has USD as a currency, therefore this should fail.
            instance.money = F('money') + Money(100, 'EUR')

    @pytest.mark.parametrize(
        'filters, expected_count',
        (
            (Q(amount1=F('amount2')), 1),
            pytest.mark.xfail(
                (Q(amount1__gt=F('amount2')), 2),
                reason='Filtering with Q objects is not the same as filtering with kwargs.'
                       'It generates different queries.'
            ),
            (Q(amount1=Money(1, 'USD')) | Q(amount2=Money(0, 'USD')), 3),
            (Q(amount1=Money(1, 'USD')) | Q(amount1=Money(4, 'USD')) | Q(amount2=Money(0, 'GHS')), 2),
            (Q(amount1=Money(1, 'USD')) | Q(amount1=Money(5, 'USD')) | Q(amount2=Money(0, 'GHS')), 3),
            (Q(amount1=Money(1, 'USD')) | Q(amount1=Money(4, 'USD'), amount2=Money(0, 'GHS')), 2),
            (Q(amount1=Money(1, 'USD')) | Q(amount1__gt=Money(4, 'USD'), amount2=Money(0, 'GHS')), 1),
            (Q(amount1=Money(1, 'USD')) | Q(amount1__gte=Money(4, 'USD'), amount2=Money(0, 'GHS')), 2),
        )
    )
    def test_comparison_lookup(self, filters, expected_count):
        ModelWithTwoMoneyFields.objects.bulk_create((
            ModelWithTwoMoneyFields(amount1=Money(1, 'USD'), amount2=Money(2, 'USD')),
            ModelWithTwoMoneyFields(amount1=Money(2, 'USD'), amount2=Money(0, 'USD')),
            ModelWithTwoMoneyFields(amount1=Money(3, 'USD'), amount2=Money(0, 'USD')),
            ModelWithTwoMoneyFields(amount1=Money(4, 'USD'), amount2=Money(0, 'GHS')),
            ModelWithTwoMoneyFields(amount1=Money(5, 'USD'), amount2=Money(5, 'USD')),
        ))

        assert ModelWithTwoMoneyFields.objects.filter(filters).count() == expected_count

    def test_exact_match(self):
        money = Money('100.0')

        instance = ModelWithVanillaMoneyField.objects.create(money=money)
        retrieved = ModelWithVanillaMoneyField.objects.get(money=money)

        assert instance.pk == retrieved.pk

    def test_range_search(self):
        money = Money('3')

        instance = ModelWithVanillaMoneyField.objects.create(money=Money('100.0'))
        retrieved = ModelWithVanillaMoneyField.objects.get(money__gt=money)

        assert instance.pk == retrieved.pk

        assert ModelWithVanillaMoneyField.objects.filter(money__lt=money).count() == 0

    @pytest.mark.parametrize('model_class', (ModelWithVanillaMoneyField, ModelWithChoicesMoneyField))
    def test_currency_querying(self, model_class):
        model_class.objects.create(money=Money('100.0', moneyed.ZWN))

        assert model_class.objects.filter(money__lt=Money('1000', moneyed.USD)).count() == 0
        assert model_class.objects.filter(money__lt=Money('1000', moneyed.ZWN)).count() == 1

    def test_isnull_lookup(self):
        NullMoneyFieldModel.objects.create(field=None)
        NullMoneyFieldModel.objects.create(field=Money(100, 'USD'))

        queryset = NullMoneyFieldModel.objects.filter(field=None)
        assert queryset.count() == 1

    def test_null_default(self):
        instance = NullMoneyFieldModel.objects.create()
        assert instance.field is None

    @pytest.mark.parametrize(
        'kwargs, currency',
        (
            ({'money_currency': 'PLN'}, 'PLN'),
            ({'money': Money(0, 'EUR')}, 'EUR')
        )
    )
    def test_get_or_create_respects_currency(self, kwargs, currency):
        instance, created = ModelWithVanillaMoneyField.objects.get_or_create(**kwargs)
        assert str(instance.money.currency) == currency, 'currency should be taken into account in get_or_create'


def test_find_models_related_to_money_models():
    moneyModel = ModelWithVanillaMoneyField.objects.create(money=Money('100.0', moneyed.ZWN))
    ModelRelatedToModelWithMoney.objects.create(moneyModel=moneyModel)

    ModelRelatedToModelWithMoney.objects.get(moneyModel__money=Money('100.0', moneyed.ZWN))
    ModelRelatedToModelWithMoney.objects.get(moneyModel__money__lt=Money('1000.0', moneyed.ZWN))


def test_allow_expression_nodes_without_money():
    """Allow querying on expression nodes that are not Money"""
    desc = 'hundred'
    ModelWithNonMoneyField.objects.create(money=Money(100.0), desc=desc)
    instance = ModelWithNonMoneyField.objects.filter(desc=F('desc')).get()
    assert instance.desc == desc


def test_base_model():
    assert BaseModel.objects.model == BaseModel


@pytest.mark.parametrize('model_class', (InheritedModel, InheritorModel))
class TestInheritance:
    """Test inheritance from a concrete and an abstract models"""

    def test_model(self, model_class):
        assert model_class.objects.model == model_class

    def test_fields(self, model_class):
        first_value = Money('100.0', moneyed.ZWN)
        second_value = Money('200.0', moneyed.USD)
        instance = model_class.objects.create(money=first_value, second_field=second_value)
        assert instance.money == first_value
        assert instance.second_field == second_value


class TestManager:

    def test_manager(self):
        assert hasattr(SimpleModel, 'objects')

    def test_objects_creation(self):
        SimpleModel.objects.create(money=Money('100.0', 'USD'))
        assert SimpleModel.objects.count() == 1


class TestProxyModel:

    def test_instances(self):
        ProxyModel.objects.create(money=Money('100.0', 'USD'))
        assert isinstance(ProxyModel.objects.get(pk=1), ProxyModel)

    def test_patching(self):
        ProxyModel.objects.create(money=Money('100.0', 'USD'))
        # This will fail if ProxyModel.objects doesn't have the patched manager
        assert ProxyModel.objects.filter(money__gt=Money('50.00', 'GBP')).count() == 0


rates_is_available = pytest.mark.skipif(
    not AUTO_CONVERT_MONEY,
    reason='You need to install django-money-rates to run this test'
)


class TestDifferentCurrencies:
    """Test add/sub operations between different currencies"""

    @rates_is_available
    @pytest.mark.usefixtures('patched_convert_money')
    def test_add(self):
        result = MoneyPatched(10, 'EUR') + Money(1, 'USD')
        assert Decimal(str(round(result.amount, 2))) == Decimal('10.88')
        assert result.currency == moneyed.EUR

    @rates_is_available
    @pytest.mark.usefixtures('patched_convert_money')
    def test_sub(self):
        result = MoneyPatched(10, 'EUR') - Money(1, 'USD')
        assert Decimal(str(round(result.amount, 2))) == Decimal('9.23')
        assert result.currency == moneyed.EUR

    def test_eq(self):
        assert MoneyPatched(1, 'EUR') == Money(1, 'EUR')

    def test_ne(self):
        assert MoneyPatched(1, 'EUR') != Money(2, 'EUR')

    def test_exception(self):
        with pytest.raises(TypeError):
            MoneyPatched(10, 'EUR') == Money(10, 'USD')
