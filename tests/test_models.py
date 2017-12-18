# -*- coding: utf-8 -*-
"""
Created on May 7, 2011

@author: jake
"""
import datetime
from copy import copy
from decimal import Decimal

from django import VERSION
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.db import models
from django.db.migrations.writer import MigrationWriter
from django.db.models import Case, F, Func, Q, Value, When
from django.utils.six import PY2
from django.utils.translation import override

import pytest

from djmoney.models.fields import MoneyField, MoneyPatched
from djmoney.money import Money
from moneyed import Money as OldMoney

from .testapp.models import (
    AbstractModel,
    BaseModel,
    DateTimeModel,
    InheritedModel,
    InheritorModel,
    ModelIssue300,
    ModelRelatedToModelWithMoney,
    ModelWithChoicesMoneyField,
    ModelWithCustomManager,
    ModelWithDefaultAsDecimal,
    ModelWithDefaultAsFloat,
    ModelWithDefaultAsInt,
    ModelWithDefaultAsMoney,
    ModelWithDefaultAsOldMoney,
    ModelWithDefaultAsString,
    ModelWithDefaultAsStringWithCurrency,
    ModelWithNonMoneyField,
    ModelWithSharedCurrency,
    ModelWithTwoMoneyFields,
    ModelWithUniqueIdAndCurrency,
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
            (ModelWithVanillaMoneyField, {'money': OldMoney('100.0')}, Money('100.0')),
            (BaseModel, {}, Money(0, 'USD')),
            (BaseModel, {'money': '111.2'}, Money('111.2', 'USD')),
            (BaseModel, {'money': Money('123', 'PLN')}, Money('123', 'PLN')),
            (BaseModel, {'money': OldMoney('123', 'PLN')}, Money('123', 'PLN')),
            (BaseModel, {'money': ('123', 'PLN')}, Money('123', 'PLN')),
            (BaseModel, {'money': (123.0, 'PLN')}, Money('123', 'PLN')),
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

    def test_old_money_defaults(self):
        instance = ModelWithDefaultAsOldMoney.objects.create()
        assert instance.money == Money('.01', 'RUB')

    @pytest.mark.parametrize(
        'model_class, other_value',
        (
            (ModelWithVanillaMoneyField, Money('100.0')),
            (BaseModel, Money(0, 'USD')),
            (ModelWithDefaultAsMoney, Money('0.01', 'RUB')),
            (ModelWithDefaultAsFloat, OldMoney('12.05', 'PLN')),
            (ModelWithDefaultAsFloat, Money('12.05', 'PLN')),
        )
    )
    def test_revert_to_default(self, model_class, other_value):
        if hasattr(model_class._meta, 'get_field'):
            default_instance = model_class._meta.get_field('money').get_default()
        else:
            default_instance = model_class._meta.get_field_by_name('money').default
        instance1 = model_class.objects.create()
        pk = instance1.pk
        # Grab a fresh instance, change the currency to something non-default
        # and unexpected
        instance2 = model_class.objects.get(id=pk)
        instance2.money = Money(other_value.amount, "DKK")
        instance2.save()
        instance3 = model_class.objects.get(id=pk)
        assert instance3.money == Money(other_value.amount, "DKK")
        # Now change the field back to the default currency
        instance3.money = copy(default_instance)
        instance3.save()
        instance4 = model_class.objects.get(id=pk)
        assert instance4.money == default_instance

    @pytest.mark.parametrize(
        'value',
        (
            (1, 'USD', 'extra_string'),
            (1, None),
            (1, ),
        )
    )
    def test_invalid_values(self, value):
        with pytest.raises(ValidationError):
            BaseModel.objects.create(money=value)

    @pytest.mark.parametrize('Money', (Money, OldMoney))
    @pytest.mark.parametrize('field_name', ('money', 'second_money'))
    def test_save_new_value(self, field_name, Money):
        ModelWithVanillaMoneyField.objects.create(**{field_name: Money('100.0')})

        # Try setting the value directly
        retrieved = ModelWithVanillaMoneyField.objects.get()
        setattr(retrieved, field_name, Money(1, 'DKK'))
        retrieved.save()
        retrieved = ModelWithVanillaMoneyField.objects.get()

        assert getattr(retrieved, field_name) == Money(1, 'DKK')

    def test_rounding(self):
        money = Money('100.0623456781123219')

        instance = ModelWithVanillaMoneyField.objects.create(money=money)
        # TODO. Should instance.money be rounded too?

        retrieved = ModelWithVanillaMoneyField.objects.get(pk=instance.pk)

        assert retrieved.money == Money('100.06')

    @pytest.fixture(params=[Money, OldMoney])
    def objects_setup(self, request):
        Money = request.param
        ModelWithTwoMoneyFields.objects.bulk_create((
            ModelWithTwoMoneyFields(amount1=Money(1, 'USD'), amount2=Money(2, 'USD')),
            ModelWithTwoMoneyFields(amount1=Money(2, 'USD'), amount2=Money(0, 'USD')),
            ModelWithTwoMoneyFields(amount1=Money(3, 'USD'), amount2=Money(0, 'USD')),
            ModelWithTwoMoneyFields(amount1=Money(4, 'USD'), amount2=Money(0, 'GHS')),
            ModelWithTwoMoneyFields(amount1=Money(5, 'USD'), amount2=Money(5, 'USD')),
            ModelWithTwoMoneyFields(amount1=Money(5, 'EUR'), amount2=Money(5, 'USD')),
        ))

    @pytest.mark.parametrize(
        'filters, expected_count',
        (
            (Q(amount1=F('amount2')), 1),
            (Q(amount1__gt=F('amount2')), 2),
            (Q(amount1__in=(Money(1, 'USD'), Money(5, 'EUR'))), 2),
            (Q(id__in=(-1, -2)), 0),
            (Q(amount1=Money(1, 'USD')) | Q(amount2=Money(0, 'USD')), 3),
            (Q(amount1=Money(1, 'USD')) | Q(amount1=Money(4, 'USD')) | Q(amount2=Money(0, 'GHS')), 2),
            (Q(amount1=OldMoney(1, 'USD')) | Q(amount1=OldMoney(4, 'USD')) | Q(amount2=OldMoney(0, 'GHS')), 2),
            (Q(amount1=Money(1, 'USD')) | Q(amount1=Money(5, 'USD')) | Q(amount2=Money(0, 'GHS')), 3),
            (Q(amount1=Money(1, 'USD')) | Q(amount1=Money(4, 'USD'), amount2=Money(0, 'GHS')), 2),
            (Q(amount1=Money(1, 'USD')) | Q(amount1__gt=Money(4, 'USD'), amount2=Money(0, 'GHS')), 1),
            (Q(amount1=Money(1, 'USD')) | Q(amount1__gte=Money(4, 'USD'), amount2=Money(0, 'GHS')), 2),
        )
    )
    @pytest.mark.usefixtures('objects_setup')
    def test_comparison_lookup(self, filters, expected_count):
        assert ModelWithTwoMoneyFields.objects.filter(filters).count() == expected_count

    @pytest.mark.skipif(VERSION[:2] == (1, 8), reason="Django 1.8 doesn't support __date lookup")
    def test_date_lookup(self):
        DateTimeModel.objects.create(field=Money(1, 'USD'), created='2016-12-05')
        assert DateTimeModel.objects.filter(created__date='2016-12-01').count() == 0
        assert DateTimeModel.objects.filter(created__date='2016-12-05').count() == 1

    @pytest.mark.parametrize('lookup, rhs, expected', (
        ('startswith', 2, 1),
        ('regex', '^[134]', 3),
        ('iregex', '^[134]', 3),
        ('istartswith', 2, 1),
        ('contains', 5, 2),
        ('lt', 5, 4),
        ('endswith', 5, 2),
        ('iendswith', 5, 2),
        ('gte', 4, 3),
        ('iexact', 3, 1),
        ('exact', 3, 1),
        ('isnull', True, 0),
        ('range', (3, 5), 4),
        ('lte', 2, 2),
        ('gt', 3, 3),
        ('icontains', 5, 2),
        ('in', (1, 0), 1)
    ))
    @pytest.mark.usefixtures('objects_setup')
    def test_all_lookups(self, lookup, rhs, expected):
        kwargs = {'amount1__' + lookup: rhs}
        assert ModelWithTwoMoneyFields.objects.filter(**kwargs).count() == expected

    def test_exact_match(self):
        money = Money('100.0')

        instance = ModelWithVanillaMoneyField.objects.create(money=money)
        retrieved = ModelWithVanillaMoneyField.objects.get(money=money)

        assert instance.pk == retrieved.pk

    def test_issue_300_regression(self):
        date = datetime.datetime(year=2017, month=2, day=1)
        ModelIssue300.objects.filter(money__created=date)
        ModelIssue300.objects.filter(money__created__gt=date)

    def test_range_search(self):
        money = Money('3')

        instance = ModelWithVanillaMoneyField.objects.create(money=Money('100.0'))
        retrieved = ModelWithVanillaMoneyField.objects.get(money__gt=money)

        assert instance.pk == retrieved.pk

        assert ModelWithVanillaMoneyField.objects.filter(money__lt=money).count() == 0

    def test_filter_chaining(self):
        usd_instance = ModelWithVanillaMoneyField.objects.create(money=Money(100, 'USD'))
        ModelWithVanillaMoneyField.objects.create(money=Money(100, 'EUR'))
        query = ModelWithVanillaMoneyField.objects.filter().filter(money=Money(100, 'USD'))
        assert usd_instance in query
        assert query.count() == 1

    @pytest.mark.parametrize('model_class', (ModelWithVanillaMoneyField, ModelWithChoicesMoneyField))
    def test_currency_querying(self, model_class):
        model_class.objects.create(money=Money('100.0', 'ZWN'))

        assert model_class.objects.filter(money__lt=Money('1000', 'USD')).count() == 0
        assert model_class.objects.filter(money__lt=Money('1000', 'ZWN')).count() == 1

    @pytest.mark.usefixtures('objects_setup')
    def test_in_lookup(self):
        assert ModelWithTwoMoneyFields.objects.filter(amount1__in=(Money(1, 'USD'), Money(5, 'EUR'))).count() == 2
        assert ModelWithTwoMoneyFields.objects.filter(
            Q(amount1__lte=Money(2, 'USD')), amount1__in=(Money(1, 'USD'), Money(3, 'USD'))
        ).count() == 1
        assert ModelWithTwoMoneyFields.objects.exclude(amount1__in=(Money(1, 'USD'), Money(5, 'EUR'))).count() == 4
        assert ModelWithTwoMoneyFields.objects.filter(amount1__in=(1, Money(5, 'EUR'))).count() == 2
        assert ModelWithTwoMoneyFields.objects.filter(amount1__in=(1, 5)).count() == 3

    @pytest.mark.usefixtures('objects_setup')
    def test_in_lookup_f_expression(self):
        assert ModelWithTwoMoneyFields.objects.filter(amount1__in=(Money(4, 'USD'), F('amount2'))).count() == 2

    def test_isnull_lookup(self):
        NullMoneyFieldModel.objects.create(field=None)
        NullMoneyFieldModel.objects.create(field=Money(100, 'USD'))

        queryset = NullMoneyFieldModel.objects.filter(field=None)
        assert queryset.count() == 1

    def test_null_default(self):
        instance = NullMoneyFieldModel.objects.create()
        assert instance.field is None


class TestGetOrCreate:

    @pytest.mark.parametrize(
        'model, field_name, kwargs, currency',
        (
            (ModelWithVanillaMoneyField, 'money', {'money_currency': 'PLN'}, 'PLN'),
            (ModelWithVanillaMoneyField, 'money', {'money': Money(0, 'EUR')}, 'EUR'),
            (ModelWithVanillaMoneyField, 'money', {'money': OldMoney(0, 'EUR')}, 'EUR'),
            (ModelWithSharedCurrency, 'first', {'first': 10, 'second': 15, 'currency': 'CZK'}, 'CZK')
        )
    )
    def test_get_or_create_respects_currency(self, model, field_name, kwargs, currency):
        instance, created = model.objects.get_or_create(**kwargs)
        field = getattr(instance, field_name)
        assert str(field.currency) == currency, 'currency should be taken into account in get_or_create'

    def test_get_or_create_respects_defaults(self):
        value = Money(10, 'SEK')
        instance = ModelWithUniqueIdAndCurrency.objects.create(money=value)
        instance, created = ModelWithUniqueIdAndCurrency.objects.get_or_create(
            id=instance.id,
            money_currency=instance.money_currency
        )
        assert not created
        assert instance.money == value

    def test_defaults(self):
        money = Money(10, 'EUR')
        instance, _ = ModelWithVanillaMoneyField.objects.get_or_create(integer=1, defaults={'money': money})
        assert instance.money == money

    def test_currency_field_lookup(self):
        value = Money(10, 'EUR')
        ModelWithVanillaMoneyField.objects.create(money=value)
        instance, created = ModelWithVanillaMoneyField.objects.get_or_create(money_currency__iexact='eur')
        assert not created
        assert instance.money == value

    @pytest.mark.parametrize('model, create_kwargs, get_kwargs', (
        (NullMoneyFieldModel, {'field': Money(100, 'USD')}, {'field': 100, 'field_currency': 'USD'}),
        (ModelWithSharedCurrency, {'first': 10, 'second': 15, 'currency': 'USD'}, {'first': 10, 'currency': 'USD'}),
    ))
    def test_no_default_model(self, model, create_kwargs, get_kwargs):
        model.objects.create(**create_kwargs)
        instance, created = model.objects.get_or_create(**get_kwargs)
        assert not created

    def test_shared_currency(self):
        instance, created = ModelWithSharedCurrency.objects.get_or_create(first=10, second=15, currency='USD')
        assert instance.first == Money(10, 'USD')
        assert instance.second == Money(15, 'USD')


class TestFExpressions:

    parametrize_f_objects = pytest.mark.parametrize(
        'f_obj, expected',
        (
            (F('money') + Money(100, 'USD'), Money(200, 'USD')),
            (F('money') + OldMoney(100, 'USD'), Money(200, 'USD')),
            (Money(100, 'USD') + F('money'), Money(200, 'USD')),
            (F('money') - Money(100, 'USD'), Money(0, 'USD')),
            (Money(100, 'USD') - F('money'), Money(0, 'USD')),
            (F('money') * 2, Money(200, 'USD')),
            (F('money') * F('integer'), Money(200, 'USD')),
            (Money(50, 'USD') * F('integer'), Money(100, 'USD')),
            (F('integer') * Money(50, 'USD'), Money(100, 'USD')),
            (Money(50, 'USD') / F('integer'), Money(25, 'USD')),
            (Money(51, 'USD') % F('integer'), Money(1, 'USD')),
            (F('money') / 2, Money(50, 'USD')),
            (F('money') % 98, Money(2, 'USD')),
            (F('money') / F('integer'), Money(50, 'USD')),
            (F('money') + F('money'), Money(200, 'USD')),
            (F('money') - F('money'), Money(0, 'USD')),
        )
    )

    @parametrize_f_objects
    def test_save(self, f_obj, expected):
        instance = ModelWithVanillaMoneyField.objects.create(money=Money(100, 'USD'), integer=2)
        instance.money = f_obj
        instance.save()
        instance.refresh_from_db()
        assert instance.money == expected

    @parametrize_f_objects
    def test_f_update(self, f_obj, expected):
        instance = ModelWithVanillaMoneyField.objects.create(money=Money(100, 'USD'), integer=2)
        ModelWithVanillaMoneyField.objects.update(money=f_obj)
        instance.refresh_from_db()
        assert instance.money == expected

    def test_default_update(self):
        instance = ModelWithVanillaMoneyField.objects.create(money=Money(100, 'USD'), integer=2)
        second_money = Money(100, 'USD')
        ModelWithVanillaMoneyField.objects.update(second_money=second_money)
        instance.refresh_from_db()
        assert instance.second_money == second_money

    @pytest.mark.parametrize(
        'create_kwargs, filter_value, in_result',
        (
            (
                {'money': Money(100, 'USD'), 'second_money': Money(100, 'USD')},
                {'money': F('money')},
                True
            ),
            (
                {'money': Money(100, 'USD'), 'second_money': Money(100, 'USD')},
                {'money': F('second_money')},
                True
            ),
            (
                {'money': Money(100, 'USD'), 'second_money': Money(100, 'EUR')},
                {'money': F('second_money')},
                False
            ),
            (
                {'money': Money(50, 'USD'), 'second_money': Money(100, 'USD')},
                {'second_money': F('money') * 2},
                True
            ),
            (
                {'money': Money(50, 'USD'), 'second_money': Money(100, 'USD')},
                {'second_money': F('money') + Money(50, 'USD')},
                True
            ),
            (
                {'money': Money(50, 'USD'), 'second_money': Money(100, 'EUR')},
                {'second_money': F('money') * 2},
                False
            ),
            (
                {'money': Money(50, 'USD'), 'second_money': Money(100, 'EUR')},
                {'second_money': F('money') + Money(50, 'USD')},
                False
            ),
        )
    )
    def test_filtration(self, create_kwargs, filter_value, in_result):
        instance = ModelWithVanillaMoneyField.objects.create(**create_kwargs)
        assert (instance in ModelWithVanillaMoneyField.objects.filter(**filter_value)) is in_result

    def test_update_fields_save(self):
        instance = ModelWithVanillaMoneyField.objects.create(money=Money(100, 'USD'), integer=2)
        instance.money = F('money') + Money(100, 'USD')
        instance.save(update_fields=['money'])
        instance.refresh_from_db()
        assert instance.money == Money(200, 'USD')

    INVALID_EXPRESSIONS = [
        F('money') + Money(100, 'EUR'),
        F('money') * F('money'),
        F('money') / F('money'),
        F('money') % F('money'),
        F('money') + F('integer'),
        F('money') + F('second_money'),
        F('money') ** F('money'),
        F('money') ** F('integer'),
        F('money') ** 2,
    ]

    @pytest.mark.parametrize('f_obj', INVALID_EXPRESSIONS)
    def test_invalid_expressions_access(self, f_obj):
        instance = ModelWithVanillaMoneyField.objects.create(money=Money(100, 'USD'))
        with pytest.raises(ValidationError):
            instance.money = f_obj


class TestExpressions:

    def test_conditional_update(self):
        ModelWithVanillaMoneyField.objects.bulk_create((
            ModelWithVanillaMoneyField(money=Money(1, 'USD'), integer=0),
            ModelWithVanillaMoneyField(money=Money(2, 'USD'), integer=1),
        ))
        ModelWithVanillaMoneyField.objects.update(money=Case(
            When(integer=0, then=Value(10)),
            default=Value(0)
        ))
        assert ModelWithVanillaMoneyField.objects.get(integer=0).money == Money(10, 'USD')
        assert ModelWithVanillaMoneyField.objects.get(integer=1).money == Money(0, 'USD')

    @pytest.mark.skipif(VERSION[:2] == (1, 8), reason="Django 1.8 doesn't supports this")
    def test_create_func(self):
        instance = ModelWithVanillaMoneyField.objects.create(money=Func(Value(-10), function='ABS'))
        instance.refresh_from_db()
        assert instance.money.amount == 10

    @pytest.mark.parametrize(
        'value, expected', (
            (None, None),
            (10, Money(10, 'USD')),
            (Money(10, 'EUR'), Money(10, 'EUR')),
        )
    )
    def test_value_create(self, value, expected):
        instance = NullMoneyFieldModel.objects.create(field=Value(value))
        instance.refresh_from_db()
        assert instance.field == expected

    def test_value_create_invalid(self):
        with pytest.raises(ValidationError):
            ModelWithVanillaMoneyField.objects.create(money=Value('string'))

    def test_expressions_for_non_money_fields(self):
        instance = ModelWithVanillaMoneyField.objects.create(money=Money(1, 'USD'), integer=0)
        assert ModelWithVanillaMoneyField.objects.get(money=F('integer') + 1) == instance
        assert ModelWithVanillaMoneyField.objects.get(Q(money=F('integer') + 1)) == instance


def test_find_models_related_to_money_models():
    moneyModel = ModelWithVanillaMoneyField.objects.create(money=Money('100.0', 'ZWN'))
    ModelRelatedToModelWithMoney.objects.create(moneyModel=moneyModel)

    ModelRelatedToModelWithMoney.objects.get(moneyModel__money=Money('100.0', 'ZWN'))
    ModelRelatedToModelWithMoney.objects.get(moneyModel__money__lt=Money('1000.0', 'ZWN'))


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
        first_value = Money('100.0', 'ZWN')
        second_value = Money('200.0', 'USD')
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


class TestDifferentCurrencies:
    """Test add/sub operations between different currencies"""

    def test_add_default(self):
        with pytest.raises(TypeError):
            Money(10, 'EUR') + Money(1, 'USD')

    def test_sub_default(self):
        with pytest.raises(TypeError):
            Money(10, 'EUR') - Money(1, 'USD')

    @pytest.mark.usefixtures('patched_convert_money')
    def test_add_with_auto_convert(self, settings):
        settings.AUTO_CONVERT_MONEY = True
        result = Money(10, 'EUR') + Money(1, 'USD')
        assert Decimal(str(round(result.amount, 2))) == Decimal('10.88')
        assert str(result.currency) == 'EUR'

    @pytest.mark.usefixtures('patched_convert_money')
    def test_sub_with_auto_convert(self, settings):
        settings.AUTO_CONVERT_MONEY = True
        result = Money(10, 'EUR') - Money(1, 'USD')
        assert Decimal(str(round(result.amount, 2))) == Decimal('9.23')
        assert str(result.currency) == 'EUR'

    def test_eq(self):
        assert Money(1, 'EUR') == Money(1, 'EUR')

    def test_ne(self):
        assert Money(1, 'EUR') != Money(2, 'EUR')

    def test_ne_currency(self):
        assert Money(10, 'EUR') != Money(10, 'USD')

    @pytest.mark.skipif(VERSION[:2] != (1, 11), reason='djmoney_rates supports only Django 1.8')
    def test_incompatibility(self, settings):
        """
        Django 1.11 is the only supported version, that will raise this exception during conversion.
        Newer versions will not even run.
        """
        settings.AUTO_CONVERT_MONEY = True
        with pytest.raises(ImproperlyConfigured) as exc:
            Money(10, 'EUR') - Money(1, 'USD')
        assert str(exc.value) == 'djmoney_rates supports only Django 1.8'

    @pytest.mark.skipif(VERSION[:2] != (1, 8), reason='djmoney_rates supports only Django 1.8')
    def test_djmoney_rates_not_installed(self, settings):
        settings.AUTO_CONVERT_MONEY = True
        settings.INSTALLED_APPS.remove('djmoney_rates')

        with pytest.raises(ImproperlyConfigured) as exc:
            Money(10, 'EUR') - Money(1, 'USD')
        assert str(exc.value) == 'You must install djmoney-rates to use AUTO_CONVERT_MONEY = True'


@pytest.mark.parametrize(
    'model_class', (
        AbstractModel,
        ModelWithNonMoneyField,
        InheritorModel,
        InheritedModel,
        ProxyModel,
    )
)
def test_manager_instance_access(model_class):
    with pytest.raises(AttributeError):
        model_class().objects.all()


@pytest.mark.skipif(VERSION[:2] != (1, 8), reason='Only Django 1.8 has `get_field_by_name` method of `Options`.')
def test_get_field_by_name():
    assert BaseModel._meta.get_field_by_name('money')[0].__class__.__name__ == 'MoneyField'
    assert BaseModel._meta.get_field_by_name('money_currency')[0].__class__.__name__ == 'CurrencyField'


def test_different_hashes():
    money = BaseModel._meta.get_field('money')
    money_currency = BaseModel._meta.get_field('money_currency')
    assert hash(money) != hash(money_currency)


def test_migration_serialization():
    if PY2:
        serialized = 'djmoney.money.Money(100, b\'GBP\')'
    else:
        serialized = 'djmoney.money.Money(100, \'GBP\')'
    assert MigrationWriter.serialize(Money(100, 'GBP')) == (serialized, {'import djmoney.money'})


def test_clear_meta_cache():
    """
    See issue GH-318.
    """
    ModelWithVanillaMoneyField._meta._expire_cache()
    manager_class = ModelWithVanillaMoneyField.objects.__class__
    assert manager_class.__module__ + '.' + manager_class.__name__ == 'djmoney.models.managers.MoneyManager'


class TestFieldAttributes:

    def create_class(self, **field_kwargs):

        class Model(models.Model):
            field = MoneyField(**field_kwargs)

            class Meta:
                app_label = 'test'

        return Model

    def test_missing_attributes(self):
        with pytest.raises(ValueError) as exc:
            self.create_class(default={})
        assert str(exc.value) == 'default value must be an instance of Money, is: {}'

    def test_default_currency(self):
        klass = self.create_class(default_currency=None, default=Money(10, 'EUR'), max_digits=10, decimal_places=2)
        assert str(klass._meta.fields[2].default_currency) == 'EUR'
        instance = klass()
        assert instance.field == Money(10, 'EUR')


class TestCustomManager:

    def test_method(self):
        assert ModelWithCustomManager.manager.super_method().count() == 0


def test_package_is_importable():
    __import__('djmoney.__init__')


def test_hash_uniqueness():
    """
    All fields of any model should have unique hash.
    """
    hashes = [hash(field) for field in ModelWithVanillaMoneyField._meta.get_fields()]
    assert len(hashes) == len(set(hashes))


def test_override_decorator():
    """
    When current locale is changed, Money instances should be represented correctly.
    """
    with override('cs'):
        assert str(Money(10, 'CZK')) == 'Kč10.00'


def test_deprecation():
    with pytest.warns(None) as warnings:
        MoneyPatched(1, 'USD')
    assert str(warnings[0].message) == "'djmoney.models.fields.MoneyPatched' is deprecated. " \
                                       "Use 'djmoney.money.Money' instead"


def test_properties_access():
    with pytest.raises(TypeError) as exc:
        ModelWithVanillaMoneyField(money=Money(1, 'USD'), bla=1)
    assert str(exc.value) == "'bla' is an invalid keyword argument for this function"


def parametrize_with_q(**kwargs):
    return pytest.mark.parametrize('args, kwargs', (
        ((), kwargs),
        ((Q(**kwargs),), {}),
    ))


class TestSharedCurrency:

    @pytest.fixture
    def instance(self):
        return ModelWithSharedCurrency.objects.create(first=10, second=15, currency='USD')

    def test_attributes(self, instance):
        assert instance.first == Money(10, 'USD')
        assert instance.second == Money(15, 'USD')
        assert instance.currency == 'USD'

    @parametrize_with_q(first=Money(10, 'USD'))
    def test_filter_by_money_match(self, instance, args, kwargs):
        assert instance in ModelWithSharedCurrency.objects.filter(*args, **kwargs)

    @parametrize_with_q(first=Money(10, 'EUR'))
    def test_filter_by_money_no_match(self, instance, args, kwargs):
        assert instance not in ModelWithSharedCurrency.objects.filter(*args, **kwargs)

    @parametrize_with_q(first=F('second'))
    def test_f_query(self, args, kwargs):
        instance = ModelWithSharedCurrency.objects.create(first=10, second=10, currency='USD')
        assert instance in ModelWithSharedCurrency.objects.filter(*args, **kwargs)

    @parametrize_with_q(first__in=[Money(10, 'USD'), Money(100, 'USD')])
    def test_in_lookup(self, instance, args, kwargs):
        assert instance in ModelWithSharedCurrency.objects.filter(*args, **kwargs)

    def test_create_with_money(self):
        value = Money(10, 'USD')
        instance = ModelWithSharedCurrency.objects.create(first=value, second=value)
        assert instance.first == value
        assert instance.second == value
