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
from django.db.models import F, Q
from django.utils.six import PY2
from django.utils.translation import override

import pytest

import moneyed
from djmoney._compat import Case, Func, Value, When, get_fields
from djmoney.models.fields import MoneyField, MoneyPatched
from moneyed import Money

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
    ModelWithDefaultAsString,
    ModelWithDefaultAsStringWithCurrency,
    ModelWithNonMoneyField,
    ModelWithTwoMoneyFields,
    ModelWithUniqueIdAndCurrency,
    ModelWithVanillaMoneyField,
    NullMoneyFieldModel,
    ProxyModel,
    SimpleModel,
)


if VERSION >= (1, 7):
    from django.db.migrations.writer import MigrationWriter


pytestmark = pytest.mark.django_db


class TestVanillaMoneyField:

    @pytest.mark.parametrize(
        'model_class, kwargs, expected',
        (
            (ModelWithVanillaMoneyField, {'money': Money('100.0')}, Money('100.0')),
            (BaseModel, {}, Money(0, 'USD')),
            (BaseModel, {'money': '111.2'}, Money('111.2', 'USD')),
            (BaseModel, {'money': Money('123', 'PLN')}, Money('123', 'PLN')),
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

    @pytest.mark.parametrize(
        'model_class, other_value',
        (
            (ModelWithVanillaMoneyField, Money('100.0')),
            (BaseModel, Money(0, 'USD')),
            (ModelWithDefaultAsMoney, Money('0.01', 'RUB')),
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

    @pytest.mark.parametrize('field_name', ('money', 'second_money'))
    def test_save_new_value(self, field_name):
        ModelWithVanillaMoneyField.objects.create(**{field_name: Money('100.0')})

        # Try setting the value directly
        retrieved = ModelWithVanillaMoneyField.objects.get()
        setattr(retrieved, field_name, Money(1, moneyed.DKK))
        retrieved.save()
        retrieved = ModelWithVanillaMoneyField.objects.get()

        assert getattr(retrieved, field_name) == Money(1, moneyed.DKK)

    def test_rounding(self):
        money = Money('100.0623456781123219')

        instance = ModelWithVanillaMoneyField.objects.create(money=money)
        # TODO. Should instance.money be rounded too?

        retrieved = ModelWithVanillaMoneyField.objects.get(pk=instance.pk)

        assert retrieved.money == Money('100.06')

    @pytest.fixture
    def objects_setup(self):
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
            (Q(amount1=Money(1, 'USD')) | Q(amount1=Money(5, 'USD')) | Q(amount2=Money(0, 'GHS')), 3),
            (Q(amount1=Money(1, 'USD')) | Q(amount1=Money(4, 'USD'), amount2=Money(0, 'GHS')), 2),
            (Q(amount1=Money(1, 'USD')) | Q(amount1__gt=Money(4, 'USD'), amount2=Money(0, 'GHS')), 1),
            (Q(amount1=Money(1, 'USD')) | Q(amount1__gte=Money(4, 'USD'), amount2=Money(0, 'GHS')), 2),
        )
    )
    @pytest.mark.usefixtures('objects_setup')
    def test_comparison_lookup(self, filters, expected_count):
        assert ModelWithTwoMoneyFields.objects.filter(filters).count() == expected_count

    @pytest.mark.skipif(VERSION < (1, 9), reason='Only Django 1.9+ supports __date lookup')
    def test_date_lookup(self):
        DateTimeModel.objects.create(field=Money(1, 'USD'), created='2016-12-05')
        assert DateTimeModel.objects.filter(created__date='2016-12-01').count() == 0
        assert DateTimeModel.objects.filter(created__date='2016-12-05').count() == 1

    skip_lookup = pytest.mark.skipif(VERSION < (1, 6), reason='This lookup doesn\'t play well on Django < 1.6')

    @pytest.mark.parametrize('lookup, rhs, expected', (
        ('startswith', 2, 1),
        skip_lookup(('regex', '^[134]', 3)),
        skip_lookup(('iregex', '^[134]', 3)),
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

    @pytest.mark.parametrize('model_class', (ModelWithVanillaMoneyField, ModelWithChoicesMoneyField))
    def test_currency_querying(self, model_class):
        model_class.objects.create(money=Money('100.0', moneyed.ZWN))

        assert model_class.objects.filter(money__lt=Money('1000', moneyed.USD)).count() == 0
        assert model_class.objects.filter(money__lt=Money('1000', moneyed.ZWN)).count() == 1

    @pytest.mark.usefixtures('objects_setup')
    def test_in_lookup(self):
        assert ModelWithTwoMoneyFields.objects.filter(amount1__in=(Money(1, 'USD'), Money(5, 'EUR'))).count() == 2
        assert ModelWithTwoMoneyFields.objects.filter(
            Q(amount1__lte=Money(2, 'USD')), amount1__in=(Money(1, 'USD'), Money(3, 'USD'))
        ).count() == 1
        assert ModelWithTwoMoneyFields.objects.exclude(amount1__in=(Money(1, 'USD'), Money(5, 'EUR'))).count() == 4
        assert ModelWithTwoMoneyFields.objects.filter(amount1__in=(1, Money(5, 'EUR'))).count() == 2
        assert ModelWithTwoMoneyFields.objects.filter(amount1__in=(1, 5)).count() == 3

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
        'kwargs, currency',
        (
            ({'money_currency': 'PLN'}, 'PLN'),
            ({'money': Money(0, 'EUR')}, 'EUR')
        )
    )
    def test_get_or_create_respects_currency(self, kwargs, currency):
        instance, created = ModelWithVanillaMoneyField.objects.get_or_create(**kwargs)
        assert str(instance.money.currency) == currency, 'currency should be taken into account in get_or_create'

    def test_get_or_create_respects_defaults(self):
        instance = ModelWithUniqueIdAndCurrency.objects.create(money=Money(0, 'SEK'))
        _, created = ModelWithUniqueIdAndCurrency.objects.get_or_create(
            id=instance.id,
            money_currency=instance.money_currency
        )
        assert not created

    def test_defaults(self):
        money = Money(10, 'EUR')
        instance, _ = ModelWithVanillaMoneyField.objects.get_or_create(integer=1, defaults={'money': money})
        assert instance.money == money

    def test_currency_field_lookup(self):
        ModelWithVanillaMoneyField.objects.create(money=Money(0, 'EUR'))
        instance, created = ModelWithVanillaMoneyField.objects.get_or_create(money_currency__iexact='eur')
        assert not created

    def test_no_default_model(self):
        NullMoneyFieldModel.objects.create(field=Money(100, 'USD'))
        instance, created = NullMoneyFieldModel.objects.get_or_create(field=100, field_currency='USD')
        assert not created


class TestFExpressions:

    parametrize_f_objects = pytest.mark.parametrize(
        'f_obj, expected',
        (
            (F('money') + Money(100, 'USD'), Money(200, 'USD')),
            (F('money') - Money(100, 'USD'), Money(0, 'USD')),
            (F('money') * 2, Money(200, 'USD')),
            (F('money') * F('integer'), Money(200, 'USD')),
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
        instance = ModelWithVanillaMoneyField.objects.get(pk=instance.pk)
        assert instance.money == expected

    @parametrize_f_objects
    def test_f_update(self, f_obj, expected):
        instance = ModelWithVanillaMoneyField.objects.create(money=Money(100, 'USD'), integer=2)
        ModelWithVanillaMoneyField.objects.update(money=f_obj)
        instance = ModelWithVanillaMoneyField.objects.get(pk=instance.pk)
        assert instance.money == expected

    def test_default_update(self):
        instance = ModelWithVanillaMoneyField.objects.create(money=Money(100, 'USD'), integer=2)
        second_money = Money(100, 'USD')
        ModelWithVanillaMoneyField.objects.update(second_money=second_money)
        instance = ModelWithVanillaMoneyField.objects.get(pk=instance.pk)
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

    @pytest.mark.skipif(VERSION < (1, 5), reason='Django < 1.5 does not support `update_fields` kwarg')
    def test_update_fields_save(self):
        instance = ModelWithVanillaMoneyField.objects.create(money=Money(100, 'USD'), integer=2)
        instance.money = F('money') + Money(100, 'USD')
        instance.save(update_fields=['money'])
        instance = ModelWithVanillaMoneyField.objects.get(pk=instance.pk)
        assert instance.money == Money(200, 'USD')

    INVALID_EXPRESSIONS = [
        F('money') + Money(100, 'EUR'),
        F('money') * F('money'),
        F('money') / F('money'),
        F('money') % F('money'),
        F('money') + F('integer'),
        F('money') + F('second_money'),
    ]
    if VERSION >= (1, 7):
        INVALID_EXPRESSIONS.extend([
            F('money') ** F('money'),
            F('money') ** F('integer'),
            F('money') ** 2,
        ])

    @pytest.mark.parametrize('f_obj', INVALID_EXPRESSIONS)
    def test_invalid_expressions_access(self, f_obj):
        instance = ModelWithVanillaMoneyField.objects.create(money=Money(100, 'USD'))
        with pytest.raises(ValidationError):
            instance.money = f_obj


@pytest.mark.skipif(VERSION < (1, 8), reason='Only Django 1.8+ supports query expressions')
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

    @pytest.mark.skipif(VERSION < (1, 9), reason='Only Django 1.9+ supports this')
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


class TestDifferentCurrencies:
    """Test add/sub operations between different currencies"""

    def test_add_default(self):
        with pytest.raises(TypeError):
            MoneyPatched(10, 'EUR') + Money(1, 'USD')

    def test_sub_default(self):
        with pytest.raises(TypeError):
            MoneyPatched(10, 'EUR') - Money(1, 'USD')

    @pytest.mark.usefixtures('patched_convert_money')
    def test_add_with_auto_convert(self, settings):
        settings.AUTO_CONVERT_MONEY = True
        result = MoneyPatched(10, 'EUR') + Money(1, 'USD')
        assert Decimal(str(round(result.amount, 2))) == Decimal('10.88')
        assert result.currency == moneyed.EUR

    @pytest.mark.usefixtures('patched_convert_money')
    def test_sub_with_auto_convert(self, settings):
        settings.AUTO_CONVERT_MONEY = True
        result = MoneyPatched(10, 'EUR') - Money(1, 'USD')
        assert Decimal(str(round(result.amount, 2))) == Decimal('9.23')
        assert result.currency == moneyed.EUR

    def test_eq(self):
        assert MoneyPatched(1, 'EUR') == Money(1, 'EUR')

    def test_ne(self):
        assert MoneyPatched(1, 'EUR') != Money(2, 'EUR')

    def test_ne_currency(self):
        assert MoneyPatched(10, 'EUR') != Money(10, 'USD')

    @pytest.mark.skipif(VERSION < (1, 9) or VERSION > (2, 0), reason='djmoney_rates supports only Django < 1.9')
    def test_incompatibility(self, settings):
        settings.AUTO_CONVERT_MONEY = True
        with pytest.raises(ImproperlyConfigured) as exc:
            MoneyPatched(10, 'EUR') - Money(1, 'USD')
        assert str(exc.value) == 'djmoney_rates doesn\'t support Django 1.9+'

    @pytest.mark.skipif(VERSION[:2] >= (2, 0), reason='djmoney_rates supports only Django < 1.9')
    def test_djmoney_rates_not_installed(self, settings):
        settings.AUTO_CONVERT_MONEY = True
        settings.INSTALLED_APPS.remove('djmoney_rates')

        with pytest.raises(ImproperlyConfigured) as exc:
            MoneyPatched(10, 'EUR') - Money(1, 'USD')
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


@pytest.mark.skipif(VERSION >= (1, 10), reason='Django >= 1.10 dropped `get_field_by_name` method of `Options`.')
def test_get_field_by_name():
    assert BaseModel._meta.get_field_by_name('money')[0].__class__.__name__ == 'MoneyField'
    assert BaseModel._meta.get_field_by_name('money_currency')[0].__class__.__name__ == 'CurrencyField'


def test_different_hashes():
    money = BaseModel._meta.get_field('money')
    money_currency = BaseModel._meta.get_field('money_currency')
    assert hash(money) != hash(money_currency)


@pytest.mark.skipif(VERSION < (1, 7), reason='Django < 1.7 handles migrations differently')
def test_migration_serialization():
    imports = set(['import djmoney.models.fields'])
    if PY2:
        serialized = 'djmoney.models.fields.MoneyPatched(100, b\'GBP\')'
    else:
        serialized = 'djmoney.models.fields.MoneyPatched(100, \'GBP\')'
    assert MigrationWriter.serialize(MoneyPatched(100, 'GBP')) == (serialized, imports)


no_system_checks_framework = pytest.mark.skipif(VERSION >= (1, 7), reason='Django 1.7+ has system checks framework')


class TestFieldAttributes:

    def create_class(self, **field_kwargs):

        class Model(models.Model):
            field = MoneyField(**field_kwargs)

            class Meta:
                app_label = 'test'

        return Model

    @pytest.mark.parametrize('field_kwargs, message', (
        no_system_checks_framework(
            ({'max_digits': 10}, 'You have to provide a decimal_places attribute to Money fields.')
        ),
        no_system_checks_framework(
            ({'decimal_places': 2}, 'You have to provide a max_digits attribute to Money fields.')
        ),
        ({'default': {}}, 'default value must be an instance of Money, is: {}'),
    ))
    def test_missing_attributes(self, field_kwargs, message):
        with pytest.raises(ValueError) as exc:
            self.create_class(**field_kwargs)
        assert str(exc.value) == message

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
    hashes = [hash(field) for field in get_fields(ModelWithVanillaMoneyField)]
    assert len(hashes) == len(set(hashes))


def test_override_decorator():
    """
    When current locale is changed, MoneyPatched instances should be represented correctly.
    """
    with override('cs'):
        assert str(MoneyPatched(10, 'CZK')) == 'Kč10.00'


def test_properties_access():
    with pytest.raises(TypeError) as exc:
        ModelWithVanillaMoneyField(money=Money(1, 'USD'), bla=1)
    assert str(exc.value) == "'bla' is an invalid keyword argument for this function"
