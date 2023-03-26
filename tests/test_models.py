"""
Created on May 7, 2011

@author: jake
"""
import datetime
from copy import copy
from decimal import Decimal, InvalidOperation

from django import VERSION
from django.core.exceptions import ValidationError
from django.db import IntegrityError, models
from django.db.migrations.writer import MigrationWriter
from django.db.models import Case, F, Func, Q, Value, When
from django.db.models.functions import Coalesce
from django.utils.translation import override

import pytest

from djmoney.models.fields import MoneyField
from djmoney.money import Money
from moneyed import Money as OldMoney
from moneyed.classes import CurrencyDoesNotExist

from .testapp.models import (
    AbstractModel,
    BaseModel,
    CryptoModel,
    DateTimeModel,
    InheritedModel,
    InheritorModel,
    ModelIssue300,
    ModelRelatedToModelWithMoney,
    ModelWithChoicesMoneyField,
    ModelWithCustomDefaultManager,
    ModelWithCustomManager,
    ModelWithDefaultAsDecimal,
    ModelWithDefaultAsFloat,
    ModelWithDefaultAsInt,
    ModelWithDefaultAsMoney,
    ModelWithDefaultAsOldMoney,
    ModelWithDefaultAsString,
    ModelWithDefaultAsStringWithCurrency,
    ModelWithNonMoneyField,
    ModelWithNullableCurrency,
    ModelWithNullDefaultOnNonNullableField,
    ModelWithSharedCurrency,
    ModelWithTwoMoneyFields,
    ModelWithUniqueIdAndCurrency,
    ModelWithVanillaMoneyField,
    NotNullMoneyFieldModel,
    NullMoneyFieldModel,
    ProxyModel,
    ProxyModelWrapper,
    SimpleModel,
)


pytestmark = pytest.mark.django_db


class TestVanillaMoneyField:
    @pytest.mark.parametrize(
        "model_class, kwargs, expected",
        (
            (ModelWithVanillaMoneyField, {"money": Money("100.0", "USD")}, Money("100.0", "USD")),
            (ModelWithVanillaMoneyField, {"money": OldMoney("100.0", "USD")}, Money("100.0", "USD")),
            (BaseModel, {}, Money(0, "USD")),
            (BaseModel, {"money": "111.2"}, Money("111.2", "USD")),
            (BaseModel, {"money": Money("123", "PLN")}, Money("123", "PLN")),
            (BaseModel, {"money": OldMoney("123", "PLN")}, Money("123", "PLN")),
            (BaseModel, {"money": ("123", "PLN")}, Money("123", "PLN")),
            (BaseModel, {"money": (123.0, "PLN")}, Money("123", "PLN")),
            (ModelWithDefaultAsMoney, {}, Money("0.01", "RUB")),
            (ModelWithDefaultAsFloat, {}, Money("12.05", "PLN")),
            (ModelWithDefaultAsStringWithCurrency, {}, Money("123", "USD")),
            (ModelWithDefaultAsString, {}, Money("123", "PLN")),
            (ModelWithDefaultAsInt, {}, Money("123", "GHS")),
            (ModelWithDefaultAsDecimal, {}, Money("0.01", "CHF")),
            (CryptoModel, {"money": Money(10, "USDT")}, Money(10, "USDT")),
        ),
    )
    def test_create_defaults(self, model_class, kwargs, expected):
        instance = model_class.objects.create(**kwargs)
        assert instance.money == expected

        retrieved = model_class.objects.get(pk=instance.pk)
        assert retrieved.money == expected

    def test_old_money_not_mutated_default(self):
        # See GH-603
        money = OldMoney(1, "EUR")

        # When `moneyed.Money` is passed as a default value to a model
        class Model(models.Model):
            price = MoneyField(default=money, max_digits=10, decimal_places=2)

            class Meta:
                abstract = True

        # Its class should remain the same
        assert type(money) is OldMoney

    def test_old_money_not_mutated_f_object(self):
        # See GH-603
        money = OldMoney(1, "EUR")

        instance = ModelWithVanillaMoneyField.objects.create(money=Money(5, "EUR"), integer=2)
        # When `moneyed.Money` is a part of an F-expression
        instance.money = F("money") + money

        # Its class should remain the same
        assert type(money) is OldMoney

    def test_old_money_defaults(self):
        instance = ModelWithDefaultAsOldMoney.objects.create()
        assert instance.money == Money(".01", "RUB")

    @pytest.mark.parametrize(
        "model_class, other_value",
        (
            (BaseModel, Money(0, "USD")),
            (ModelWithDefaultAsMoney, Money("0.01", "RUB")),
            (ModelWithDefaultAsFloat, OldMoney("12.05", "PLN")),
            (ModelWithDefaultAsFloat, Money("12.05", "PLN")),
        ),
    )
    def test_revert_to_default(self, model_class, other_value):
        if hasattr(model_class._meta, "get_field"):
            default_instance = model_class._meta.get_field("money").get_default()
        else:
            default_instance = model_class._meta.get_field_by_name("money").default
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

    @pytest.mark.parametrize("value", ((1, "USD", "extra_string"), (1, None), (1,)))
    def test_invalid_values(self, value):
        with pytest.raises(ValidationError):
            BaseModel.objects.create(money=value)

    @pytest.mark.parametrize("money_class", (Money, OldMoney))
    def test_save_new_value_on_field_without_default(self, money_class):
        ModelWithVanillaMoneyField.objects.create(money=money_class("100.0", "DKK"))

        # Try setting the value directly
        retrieved = ModelWithVanillaMoneyField.objects.get()
        retrieved.money = Money(1, "DKK")
        retrieved.save()
        retrieved = ModelWithVanillaMoneyField.objects.get()
        assert retrieved.money == Money(1, "DKK")

    def test_save_new_value_on_field_with_default(self):
        ModelWithDefaultAsMoney.objects.create()

        # Try setting the value directly
        retrieved = ModelWithDefaultAsMoney.objects.get()
        retrieved.money = Money(1, "DKK")
        retrieved.save()
        retrieved = ModelWithDefaultAsMoney.objects.get()
        assert retrieved.money == Money(1, "DKK")

    def test_rounding(self):
        money = Money("100.0623456781123219", "USD")

        instance = ModelWithVanillaMoneyField.objects.create(money=money)
        # TODO. Should instance.money be rounded too?

        retrieved = ModelWithVanillaMoneyField.objects.get(pk=instance.pk)

        assert retrieved.money == Money("100.06", "USD")

    @pytest.fixture(params=[Money, OldMoney])
    def objects_setup(self, request):
        Money = request.param
        ModelWithTwoMoneyFields.objects.bulk_create(
            (
                ModelWithTwoMoneyFields(amount1=Money(1, "USD"), amount2=Money(2, "USD")),
                ModelWithTwoMoneyFields(amount1=Money(2, "USD"), amount2=Money(0, "USD")),
                ModelWithTwoMoneyFields(amount1=Money(3, "USD"), amount2=Money(0, "USD")),
                ModelWithTwoMoneyFields(amount1=Money(4, "USD"), amount2=Money(0, "GHS")),
                ModelWithTwoMoneyFields(amount1=Money(5, "USD"), amount2=Money(5, "USD")),
                ModelWithTwoMoneyFields(amount1=Money(5, "EUR"), amount2=Money(5, "USD")),
            )
        )

    @pytest.mark.parametrize(
        "filters, expected_count",
        (
            (Q(amount1=F("amount2")), 1),
            (Q(amount1__gt=F("amount2")), 2),
            (Q(amount1__in=(Money(1, "USD"), Money(5, "EUR"))), 2),
            (Q(id__in=(-1, -2)), 0),
            (Q(amount1=Money(1, "USD")) | Q(amount2=Money(0, "USD")), 3),
            (Q(amount1=Money(1, "USD")) | Q(amount1=Money(4, "USD")) | Q(amount2=Money(0, "GHS")), 2),
            (Q(amount1=OldMoney(1, "USD")) | Q(amount1=OldMoney(4, "USD")) | Q(amount2=OldMoney(0, "GHS")), 2),
            (Q(amount1=Money(1, "USD")) | Q(amount1=Money(5, "USD")) | Q(amount2=Money(0, "GHS")), 3),
            (Q(amount1=Money(1, "USD")) | Q(amount1=Money(4, "USD"), amount2=Money(0, "GHS")), 2),
            (Q(amount1=Money(1, "USD")) | Q(amount1__gt=Money(4, "USD"), amount2=Money(0, "GHS")), 1),
            (Q(amount1=Money(1, "USD")) | Q(amount1__gte=Money(4, "USD"), amount2=Money(0, "GHS")), 2),
        ),
    )
    @pytest.mark.usefixtures("objects_setup")
    def test_comparison_lookup(self, filters, expected_count):
        assert ModelWithTwoMoneyFields.objects.filter(filters).count() == expected_count

    def test_date_lookup(self):
        DateTimeModel.objects.create(field=Money(1, "USD"), created="2016-12-05")
        assert DateTimeModel.objects.filter(created__date="2016-12-01").count() == 0
        assert DateTimeModel.objects.filter(created__date="2016-12-05").count() == 1

    @pytest.mark.parametrize(
        "lookup, rhs, expected",
        (
            ("startswith", 2, 1),
            ("regex", "^[134]", 3),
            ("iregex", "^[134]", 3),
            ("istartswith", 2, 1),
            ("contains", 5, 2),
            ("lt", 5, 4),
            ("endswith", 5, 2),
            ("iendswith", 5, 2),
            ("gte", 4, 3),
            ("iexact", 3, 1),
            ("exact", 3, 1),
            ("isnull", True, 0),
            ("range", (3, 5), 4),
            ("lte", 2, 2),
            ("gt", 3, 3),
            ("icontains", 5, 2),
            ("in", (1, 0), 1),
        ),
    )
    @pytest.mark.usefixtures("objects_setup")
    def test_all_lookups(self, lookup, rhs, expected):
        kwargs = {"amount1__" + lookup: rhs}
        assert ModelWithTwoMoneyFields.objects.filter(**kwargs).count() == expected

    def test_exact_match(self):
        money = Money("100.0", "USD")

        instance = ModelWithVanillaMoneyField.objects.create(money=money)
        retrieved = ModelWithVanillaMoneyField.objects.get(money=money)

        assert instance.pk == retrieved.pk

    def test_issue_300_regression(self):
        date = datetime.datetime(year=2017, month=2, day=1)
        ModelIssue300.objects.filter(money__created=date)
        ModelIssue300.objects.filter(money__created__gt=date)

    def test_range_search(self):
        money = Money("3", "EUR")

        instance = ModelWithVanillaMoneyField.objects.create(money=Money("100.0", "EUR"))
        retrieved = ModelWithVanillaMoneyField.objects.get(money__gt=money)

        assert instance.pk == retrieved.pk

        assert ModelWithVanillaMoneyField.objects.filter(money__lt=money).count() == 0

    def test_filter_chaining(self):
        usd_instance = ModelWithVanillaMoneyField.objects.create(money=Money(100, "USD"))
        ModelWithVanillaMoneyField.objects.create(money=Money(100, "EUR"))
        query = ModelWithVanillaMoneyField.objects.filter().filter(money=Money(100, "USD"))
        assert usd_instance in query
        assert query.count() == 1

    @pytest.mark.parametrize("model_class", (ModelWithVanillaMoneyField, ModelWithChoicesMoneyField))
    def test_currency_querying(self, model_class):
        model_class.objects.create(money=Money("100.0", "ZWN"))

        assert model_class.objects.filter(money__lt=Money("1000", "USD")).count() == 0
        assert model_class.objects.filter(money__lt=Money("1000", "ZWN")).count() == 1

    @pytest.mark.usefixtures("objects_setup")
    def test_in_lookup(self):
        assert ModelWithTwoMoneyFields.objects.filter(amount1__in=(Money(1, "USD"), Money(5, "EUR"))).count() == 2
        assert (
            ModelWithTwoMoneyFields.objects.filter(
                Q(amount1__lte=Money(2, "USD")), amount1__in=(Money(1, "USD"), Money(3, "USD"))
            ).count()
            == 1
        )
        assert ModelWithTwoMoneyFields.objects.exclude(amount1__in=(Money(1, "USD"), Money(5, "EUR"))).count() == 4
        assert ModelWithTwoMoneyFields.objects.filter(amount1__in=(1, Money(5, "EUR"))).count() == 2
        assert ModelWithTwoMoneyFields.objects.filter(amount1__in=(1, 5)).count() == 3

    @pytest.mark.usefixtures("objects_setup")
    def test_in_lookup_f_expression(self):
        assert ModelWithTwoMoneyFields.objects.filter(amount1__in=(Money(4, "USD"), F("amount2"))).count() == 2

    def test_isnull_lookup(self):
        NullMoneyFieldModel.objects.create(field=None)
        NullMoneyFieldModel.objects.create(field=Money(100, "USD"))

        queryset = NullMoneyFieldModel.objects.filter(field=None)
        assert queryset.count() == 1

    def test_null_default(self):
        instance = NullMoneyFieldModel.objects.create()
        assert instance.field is None

    def test_implicit_currency_field_not_nullable_when_money_field_not_nullable(self):
        instance = ModelWithVanillaMoneyField(money=10, money_currency=None)
        with pytest.raises(TypeError, match=r"Currency code can't be None"):
            instance.save()

    def test_raises_type_error_setting_currency_to_none_on_nullable_currency_field_while_having_amount(self):
        with pytest.raises(ValueError, match=r"Missing currency value"):
            NullMoneyFieldModel(field=10, field_currency=None)

    def test_currency_field_null_switch_not_triggered_from_default_currency(self):
        # We want a sane default behaviour and simply declaring a `MoneyField(...)`
        # without any default value args should create non nullable amount and currency
        # fields
        assert ModelWithVanillaMoneyField._meta.get_field("money").null is False
        assert ModelWithVanillaMoneyField._meta.get_field("money_currency").null is False

    def test_currency_field_nullable_when_money_field_is_nullable(self):
        assert NullMoneyFieldModel._meta.get_field("field").null is True
        assert NullMoneyFieldModel._meta.get_field("field_currency").null is True


@pytest.mark.parametrize(
    ("default", "error", "error_match"),
    [
        pytest.param("10", AssertionError, r"Default currency can not be `None`", id="string without currency"),
        pytest.param(b"10", AssertionError, r"Default currency can not be `None`", id="bytes without currency"),
        pytest.param(13.37, AssertionError, r"Default currency can not be `None`", id="float"),
        pytest.param(Decimal(10), AssertionError, r"Default currency can not be `None`", id="decimal"),
        pytest.param(10, AssertionError, r"Default currency can not be `None`", id="int"),
        pytest.param("100 ", CurrencyDoesNotExist, r"code  ", id="string with trailing space and without currency"),
        pytest.param(b"100 ", CurrencyDoesNotExist, r"code  ", id="bytes with trailing space and without currency"),
        pytest.param("100 ABC123", CurrencyDoesNotExist, r"code ABC123", id="string with unknown currency code"),
        pytest.param(b"100 ABC123", CurrencyDoesNotExist, r"code ABC123", id="bytes with unknown currency code"),
        # TODO: Better error reporting on > 1 white spaces between amount and currency as that could be
        # quite difficult to spot?
        pytest.param(
            "100  SEK", CurrencyDoesNotExist, r"code  SEK", id="string with too much value and currency separation"
        ),
        pytest.param(
            b"100  SEK", CurrencyDoesNotExist, r"code  SEK", id="bytes with too much value and currency separation"
        ),
        pytest.param(
            "  10 SEK  ",
            InvalidOperation,
            r"(ConversionSyntax|Invalid literal)",
            id="string with leading and trailing spaces",
        ),
        pytest.param(
            b"  10 SEK  ",
            InvalidOperation,
            r"(ConversionSyntax|Invalid literal)",
            id="bytes with leading and trailing spaces",
        ),
        pytest.param(
            "  10 SEK", InvalidOperation, r"(ConversionSyntax|Invalid literal)", id="string with leading spaces"
        ),
        pytest.param(
            b"  10 SEK", InvalidOperation, r"(ConversionSyntax|Invalid literal)", id="bytes with leading spaces"
        ),
        pytest.param("10 SEK  ", CurrencyDoesNotExist, r"code SEK   ", id="string with trailing spaces"),
        pytest.param(b"10 SEK  ", CurrencyDoesNotExist, r"code SEK   ", id="bytes with trailing spaces"),
    ],
)
def test_errors_instantiating_money_field_with_no_default_currency_and_default_as(default, error, error_match):
    with pytest.raises(error, match=error_match):
        MoneyField(max_digits=10, decimal_places=2, default=default, default_currency=None)


@pytest.mark.parametrize(
    ("default", "default_currency", "expected"),
    [
        pytest.param("10 SEK", None, Money(10, "SEK"), id="string with currency"),
        pytest.param(b"10 SEK", None, Money(10, "SEK"), id="bytes with currency"),
        pytest.param("10", "USD", Money(10, "USD"), id="string without currency and currency default"),
        pytest.param(b"10", "USD", Money(10, "USD"), id="bytes without currency and currency default"),
    ],
)
def test_can_instantiate_money_field_default_as(default, default_currency, expected):
    field = MoneyField(max_digits=10, decimal_places=2, default=default, default_currency=default_currency)
    assert field.default == expected


def test_errors_on_default_values_being_none_when_fields_have_not_null_constraint():
    instance = ModelWithNullDefaultOnNonNullableField()
    assert instance.money is None
    assert instance.money_currency is None
    with pytest.raises(IntegrityError, match=r"testapp_modelwithnulldefaultonnonnullablefield.money"):
        instance.save()


class TestGetOrCreate:
    @pytest.mark.parametrize(
        "model, field_name, kwargs, currency",
        (
            (ModelWithDefaultAsInt, "money", {"money_currency": "PLN"}, "PLN"),
            (ModelWithVanillaMoneyField, "money", {"money": Money(0, "EUR")}, "EUR"),
            (ModelWithVanillaMoneyField, "money", {"money": OldMoney(0, "EUR")}, "EUR"),
            (ModelWithSharedCurrency, "first", {"first": 10, "second": 15, "currency": "CZK"}, "CZK"),
        ),
    )
    def test_get_or_create_respects_currency(self, model, field_name, kwargs, currency):
        instance, created = model.objects.get_or_create(**kwargs)
        field = getattr(instance, field_name)
        assert str(field.currency) == currency, "currency should be taken into account in get_or_create"

    def test_get_or_create_respects_defaults(self):
        value = Money(10, "SEK")
        instance = ModelWithUniqueIdAndCurrency.objects.create(money=value)
        instance, created = ModelWithUniqueIdAndCurrency.objects.get_or_create(
            id=instance.id, money_currency=instance.money_currency
        )
        assert not created
        assert instance.money == value

    def test_defaults(self):
        money = Money(10, "EUR")
        instance, _ = ModelWithVanillaMoneyField.objects.get_or_create(integer=1, defaults={"money": money})
        assert instance.money == money

    def test_currency_field_lookup(self):
        value = Money(10, "EUR")
        ModelWithVanillaMoneyField.objects.create(money=value)
        instance, created = ModelWithVanillaMoneyField.objects.get_or_create(money_currency__iexact="eur")
        assert not created
        assert instance.money == value

    @pytest.mark.parametrize(
        "model, create_kwargs, get_kwargs",
        (
            (NullMoneyFieldModel, {"field": Money(100, "USD")}, {"field": 100, "field_currency": "USD"}),
            (ModelWithSharedCurrency, {"first": 10, "second": 15, "currency": "USD"}, {"first": 10, "currency": "USD"}),
        ),
    )
    def test_no_default_model(self, model, create_kwargs, get_kwargs):
        model.objects.create(**create_kwargs)
        instance, created = model.objects.get_or_create(**get_kwargs)
        assert not created

    def test_shared_currency(self):
        instance, created = ModelWithSharedCurrency.objects.get_or_create(first=10, second=15, currency="USD")
        assert instance.first == Money(10, "USD")
        assert instance.second == Money(15, "USD")


class TestNullableCurrency:
    def test_create_nullable(self):
        instance = ModelWithNullableCurrency.objects.create()
        assert instance.money is None
        assert instance.money_currency is None

    def test_create_default(self):
        money = Money(100, "SEK")
        instance = ModelWithNullableCurrency.objects.create(money=money)
        assert instance.money == money

    def test_fails_with_null_currency(self):
        with pytest.raises(ValueError) as exc:
            ModelWithNullableCurrency.objects.create(money=10)
        assert str(exc.value) == "Missing currency value"
        assert not ModelWithNullableCurrency.objects.exists()

    def test_fails_with_null_currency_decimal(self):
        with pytest.raises(ValueError) as exc:
            ModelWithNullableCurrency.objects.create(money=Decimal(10))
        assert str(exc.value) == "Missing currency value"
        assert not ModelWithNullableCurrency.objects.exists()

    def test_fails_with_nullable_but_no_default(self):
        match = r"NOT NULL constraint failed: testapp_modelwithtwomoneyfields.amount1"
        with pytest.raises(IntegrityError, match=match):
            ModelWithTwoMoneyFields.objects.create()

    def test_query_not_null(self):
        money = Money(100, "EUR")
        ModelWithNullableCurrency.objects.create(money=money)
        instance = ModelWithNullableCurrency.objects.get()
        assert instance.money == money

    def test_query_null(self):
        ModelWithNullableCurrency.objects.create()
        instance = ModelWithNullableCurrency.objects.get()
        assert instance.money is None
        assert instance.money_currency is None


class TestFExpressions:

    parametrize_f_objects = pytest.mark.parametrize(
        "f_obj, expected",
        (
            (F("money") + Money(100, "USD"), Money(200, "USD")),
            (F("money") + OldMoney(100, "USD"), Money(200, "USD")),
            (Money(100, "USD") + F("money"), Money(200, "USD")),
            (F("money") - Money(100, "USD"), Money(0, "USD")),
            (Money(100, "USD") - F("money"), Money(0, "USD")),
            (F("money") * 2, Money(200, "USD")),
            (F("money") * F("integer"), Money(200, "USD")),
            (Money(50, "USD") * F("integer"), Money(100, "USD")),
            (F("integer") * Money(50, "USD"), Money(100, "USD")),
            (Money(50, "USD") / F("integer"), Money(25, "USD")),
            (Money(51, "USD") % F("integer"), Money(1, "USD")),  # type: ignore
            (F("money") / 2, Money(50, "USD")),
            (F("money") % 98, Money(2, "USD")),
            (F("money") / F("integer"), Money(50, "USD")),
            (F("money") + F("money"), Money(200, "USD")),
            (F("money") - F("money"), Money(0, "USD")),
        ),
    )

    @parametrize_f_objects
    def test_save(self, f_obj, expected):
        instance = ModelWithVanillaMoneyField.objects.create(money=Money(100, "USD"), integer=2)
        instance.money = f_obj
        instance.save()
        instance.refresh_from_db()
        assert instance.money == expected

    @parametrize_f_objects
    def test_f_update(self, f_obj, expected):
        instance = ModelWithVanillaMoneyField.objects.create(money=Money(100, "USD"), integer=2)
        ModelWithVanillaMoneyField.objects.update(money=f_obj)
        instance.refresh_from_db()
        assert instance.money == expected

    def test_default_update(self):
        instance = ModelWithVanillaMoneyField.objects.create(money=Money(100, "USD"), integer=2)
        second_money = Money(100, "USD")
        ModelWithVanillaMoneyField.objects.update(second_money=second_money)
        instance.refresh_from_db()
        assert instance.second_money == second_money

    @pytest.mark.parametrize(
        "create_kwargs, filter_value, in_result",
        (
            ({"money": Money(100, "USD"), "second_money": Money(100, "USD")}, {"money": F("money")}, True),
            ({"money": Money(100, "USD"), "second_money": Money(100, "USD")}, {"money": F("second_money")}, True),
            ({"money": Money(100, "USD"), "second_money": Money(100, "EUR")}, {"money": F("second_money")}, False),
            ({"money": Money(50, "USD"), "second_money": Money(100, "USD")}, {"second_money": F("money") * 2}, True),
            (
                {"money": Money(50, "USD"), "second_money": Money(100, "USD")},
                {"second_money": F("money") + Money(50, "USD")},
                True,
            ),
            ({"money": Money(50, "USD"), "second_money": Money(100, "EUR")}, {"second_money": F("money") * 2}, False),
            (
                {"money": Money(50, "USD"), "second_money": Money(100, "EUR")},
                {"second_money": F("money") + Money(50, "USD")},
                False,
            ),
        ),
    )
    def test_filtration(self, create_kwargs, filter_value, in_result):
        instance = ModelWithVanillaMoneyField.objects.create(**create_kwargs)
        assert (instance in ModelWithVanillaMoneyField.objects.filter(**filter_value)) is in_result

    def test_update_fields_save(self):
        instance = ModelWithVanillaMoneyField.objects.create(money=Money(100, "USD"), integer=2)
        instance.money = F("money") + Money(100, "USD")
        instance.save(update_fields=["money"])
        instance.refresh_from_db()
        assert instance.money == Money(200, "USD")

    INVALID_EXPRESSIONS = [
        F("money") + Money(100, "EUR"),
        F("money") * F("money"),
        F("money") / F("money"),
        F("money") % F("money"),
        F("money") + F("integer"),
        F("money") + F("second_money"),
        F("money") ** F("money"),
        F("money") ** F("integer"),
        F("money") ** 2,
    ]

    @pytest.mark.parametrize("f_obj", INVALID_EXPRESSIONS)
    def test_invalid_expressions_access(self, f_obj):
        instance = ModelWithVanillaMoneyField.objects.create(money=Money(100, "USD"))
        with pytest.raises(ValidationError):
            instance.money = f_obj


class TestExpressions:
    @pytest.mark.skipif(VERSION[:2] < (2, 2), reason="skipping tests for Django < 2.2")
    def test_bulk_update(self):
        assert ModelWithVanillaMoneyField.objects.filter(integer=0).count() == 0
        assert ModelWithVanillaMoneyField.objects.filter(integer=1).count() == 0
        ModelWithVanillaMoneyField.objects.create(money=Money(1, "USD"), integer=0)
        ModelWithVanillaMoneyField.objects.create(money=Money(2, "USD"), integer=1)
        first_inst = ModelWithVanillaMoneyField.objects.get(integer=0)
        second_inst = ModelWithVanillaMoneyField.objects.get(integer=1)
        assert first_inst.money == Money(1, "USD")
        assert second_inst.money == Money(2, "USD")
        first_inst.money = Money(3, "RUB")
        second_inst.money = Money(4, "UAH")
        second_inst.second_money = Money(5, "BYN")
        ModelWithVanillaMoneyField.objects.bulk_update(
            [first_inst, second_inst], ("money", "money_currency", "second_money", "second_money_currency")
        )
        assert ModelWithVanillaMoneyField.objects.get(integer=0).money == Money(3, "RUB")
        assert ModelWithVanillaMoneyField.objects.get(integer=1).money == Money(4, "UAH")
        assert ModelWithVanillaMoneyField.objects.get(integer=1).second_money == Money(5, "BYN")

    def test_conditional_update(self):
        ModelWithVanillaMoneyField.objects.bulk_create(
            (
                ModelWithVanillaMoneyField(money=Money(1, "USD"), integer=0),
                ModelWithVanillaMoneyField(money=Money(2, "USD"), integer=1),
            )
        )
        ModelWithVanillaMoneyField.objects.update(money=Case(When(integer=0, then=Value(10)), default=Value(0)))
        assert ModelWithVanillaMoneyField.objects.get(integer=0).money == Money(10, "USD")
        assert ModelWithVanillaMoneyField.objects.get(integer=1).money == Money(0, "USD")

    def test_update_with_coalesce(self):
        ModelWithVanillaMoneyField.objects.create(money=Money(1, "USD"), second_money=Money(2, "USD"), integer=0)
        ModelWithVanillaMoneyField.objects.update(
            money=Coalesce(F("second_money"), 0, output_field=models.DecimalField())
        )
        instance = ModelWithVanillaMoneyField.objects.get()
        assert instance.money == Money("2", "USD")

    def test_create_func(self):
        instance = ModelWithVanillaMoneyField.objects.create(
            money=Func(Value(-10), function="ABS"), money_currency="USD"
        )
        instance.refresh_from_db()
        assert instance.money == Money(10, "USD")

    @pytest.mark.parametrize(
        "value, expected", ((None, None), (10, Money(10, "USD")), (Money(10, "EUR"), Money(10, "EUR")))
    )
    def test_value_create(self, value, expected):
        instance = NullMoneyFieldModel.objects.create(field=Value(value))
        instance.refresh_from_db()
        assert instance.field == expected

    def test_value_create_invalid(self):
        with pytest.raises(ValidationError):
            ModelWithVanillaMoneyField.objects.create(money=Value("string"), money_currency="DKK")

    def test_expressions_for_non_money_fields(self):
        instance = ModelWithVanillaMoneyField.objects.create(money=Money(1, "USD"), integer=0)
        assert ModelWithVanillaMoneyField.objects.get(money=F("integer") + 1) == instance
        assert ModelWithVanillaMoneyField.objects.get(Q(money=F("integer") + 1)) == instance


def test_find_models_related_to_money_models():
    moneyModel = ModelWithVanillaMoneyField.objects.create(money=Money("100.0", "ZWN"))
    ModelRelatedToModelWithMoney.objects.create(moneyModel=moneyModel)

    ModelRelatedToModelWithMoney.objects.get(moneyModel__money=Money("100.0", "ZWN"))
    ModelRelatedToModelWithMoney.objects.get(moneyModel__money__lt=Money("1000.0", "ZWN"))


def test_allow_expression_nodes_without_money():
    """Allow querying on expression nodes that are not Money"""
    desc = "hundred"
    ModelWithNonMoneyField.objects.create(money=Money(100.0, "USD"), desc=desc)
    instance = ModelWithNonMoneyField.objects.filter(desc=F("desc")).get()
    assert instance.desc == desc


def test_base_model():
    assert BaseModel.objects.model == BaseModel


@pytest.mark.parametrize("model_class", (InheritedModel, InheritorModel))
class TestInheritance:
    """Test inheritance from a concrete and an abstract models"""

    def test_model(self, model_class):
        assert model_class.objects.model == model_class

    def test_fields(self, model_class):
        first_value = Money("100.0", "ZWN")
        second_value = Money("200.0", "USD")
        instance = model_class.objects.create(money=first_value, second_field=second_value)
        assert instance.money == first_value
        assert instance.second_field == second_value


class TestManager:
    def test_manager(self):
        assert hasattr(SimpleModel, "objects")

    def test_objects_creation(self):
        SimpleModel.objects.create(money=Money("100.0", "USD"))
        assert SimpleModel.objects.count() == 1


class TestProxyModel:
    def test_instances(self):
        ProxyModel.objects.create(money=Money("100.0", "USD"))
        assert isinstance(ProxyModel.objects.get(pk=1), ProxyModel)

    def test_patching(self):
        ProxyModel.objects.create(money=Money("100.0", "USD"))
        # This will fail if ProxyModel.objects doesn't have the patched manager
        assert ProxyModel.objects.filter(money__gt=Money("50.00", "GBP")).count() == 0


class TestDifferentCurrencies:
    """Test add/sub operations between different currencies"""

    def test_add_default(self):
        with pytest.raises(TypeError):
            Money(10, "EUR") + Money(1, "USD")

    def test_sub_default(self):
        with pytest.raises(TypeError):
            Money(10, "EUR") - Money(1, "USD")

    @pytest.mark.usefixtures("autoconversion")
    def test_add_with_auto_convert(self):
        assert Money(10, "EUR") + Money(1, "USD") == Money("10.88", "EUR")

    @pytest.mark.usefixtures("autoconversion")
    def test_sub_with_auto_convert(self):
        assert Money(10, "EUR") - Money(1, "USD") == Money("9.12", "EUR")

    def test_eq(self):
        assert Money(1, "EUR") == Money(1, "EUR")

    def test_ne(self):
        assert Money(1, "EUR") != Money(2, "EUR")

    def test_ne_currency(self):
        assert Money(10, "EUR") != Money(10, "USD")


INSTANCE_ACCESS_MODELS = [ModelWithNonMoneyField, InheritorModel, InheritedModel, ProxyModel]

if VERSION[:2] < (3, 2):
    # Django 3.2 and later does not support AbstractModel instancing
    INSTANCE_ACCESS_MODELS.append(AbstractModel)


@pytest.mark.parametrize("model_class", INSTANCE_ACCESS_MODELS)
def test_manager_instance_access(model_class):
    with pytest.raises(AttributeError):
        model_class().objects.all()


def test_different_hashes():
    money = BaseModel._meta.get_field("money")
    money_currency = BaseModel._meta.get_field("money_currency")
    assert hash(money) != hash(money_currency)


def test_migration_serialization():
    serialized = "djmoney.money.Money(100, 'GBP')"
    assert MigrationWriter.serialize(Money(100, "GBP")) == (serialized, {"import djmoney.money"})


@pytest.mark.parametrize(
    "model, manager_name", ((ModelWithVanillaMoneyField, "objects"), (ModelWithCustomDefaultManager, "custom"))
)
def test_clear_meta_cache(model, manager_name):
    """
    See issue GH-318.
    """
    model._meta._expire_cache()
    manager_class = getattr(model, manager_name).__class__
    assert manager_class.__module__ + "." + manager_class.__name__ == "djmoney.models.managers.MoneyManager"


class TestFieldAttributes:
    def create_class(self, **field_kwargs):
        class Model(models.Model):
            field = MoneyField(**field_kwargs)

            class Meta:
                app_label = "test"

        return Model

    def test_missing_attributes(self):
        with pytest.raises(ValueError) as exc:
            self.create_class(default={})
        assert str(exc.value) == "default value must be an instance of Money, is: {}"

    def test_default_currency(self):
        klass = self.create_class(default_currency=None, default=Money(10, "EUR"), max_digits=10, decimal_places=2)
        assert str(klass._meta.fields[2].default_currency) == "EUR"
        instance = klass()
        assert instance.field == Money(10, "EUR")


class TestCustomManager:
    def test_method(self):
        assert ModelWithCustomManager.manager.super_method().count() == 0


def test_package_is_importable():
    __import__("djmoney.__init__")


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
    with override("cs"):
        assert str(Money(10, "CZK")) == "10,00 Kč"


def test_properties_access():
    with pytest.raises(TypeError) as exc:
        ModelWithVanillaMoneyField(money=Money(1, "USD"), bla=1)
    if VERSION[:2] > (4, 0):
        assert str(exc.value) == "ModelWithVanillaMoneyField() got unexpected keyword arguments: 'bla'"
    elif VERSION[:2] > (2, 1):
        assert str(exc.value) == "ModelWithVanillaMoneyField() got an unexpected keyword argument 'bla'"
    else:
        assert str(exc.value) == "ModelWithVanillaMoneyField() got an unexpected keyword argument 'bla'"


def parametrize_with_q(**kwargs):
    return pytest.mark.parametrize("args, kwargs", (((), kwargs), ((Q(**kwargs),), {})))


class TestSharedCurrency:
    @pytest.fixture
    def instance(self):
        return ModelWithSharedCurrency.objects.create(first=10, second=15, currency="USD")

    def test_attributes(self, instance):
        assert instance.first == Money(10, "USD")
        assert instance.second == Money(15, "USD")
        assert instance.currency == "USD"

    @parametrize_with_q(first=Money(10, "USD"))
    def test_filter_by_money_match(self, instance, args, kwargs):
        assert instance in ModelWithSharedCurrency.objects.filter(*args, **kwargs)

    @parametrize_with_q(first=Money(10, "EUR"))
    def test_filter_by_money_no_match(self, instance, args, kwargs):
        assert instance not in ModelWithSharedCurrency.objects.filter(*args, **kwargs)

    @parametrize_with_q(first=F("second"))
    def test_f_query(self, args, kwargs):
        instance = ModelWithSharedCurrency.objects.create(first=10, second=10, currency="USD")
        assert instance in ModelWithSharedCurrency.objects.filter(*args, **kwargs)

    @parametrize_with_q(first__in=[Money(10, "USD"), Money(100, "USD")])
    def test_in_lookup(self, instance, args, kwargs):
        assert instance in ModelWithSharedCurrency.objects.filter(*args, **kwargs)

    def test_create_with_money(self):
        value = Money(10, "USD")
        instance = ModelWithSharedCurrency.objects.create(first=value, second=value)
        assert instance.first == value
        assert instance.second == value


def test_order_by():
    def extract_data(instance):
        return instance.money, instance.integer

    ModelWithVanillaMoneyField.objects.create(money=Money(10, "AUD"), integer=2)
    ModelWithVanillaMoneyField.objects.create(money=Money(10, "AUD"), integer=1)
    ModelWithVanillaMoneyField.objects.create(money=Money(10, "USD"), integer=3)

    qs = ModelWithVanillaMoneyField.objects.order_by("integer").filter(money=Money(10, "AUD"))
    assert list(map(extract_data, qs)) == [(Money(10, "AUD"), 1), (Money(10, "AUD"), 2)]


def test_distinct_through_wrapper():
    NotNullMoneyFieldModel.objects.create(money=10, money_currency="USD")
    NotNullMoneyFieldModel.objects.create(money=100, money_currency="USD")
    NotNullMoneyFieldModel.objects.create(money=10, money_currency="EUR")

    queryset = ProxyModelWrapper.objects.distinct()

    assert queryset.count() == 3


def test_mixer_blend():
    try:
        from mixer.backend.django import mixer
    except AttributeError:
        pass  # mixer doesn't work with pypy
    else:
        instance = mixer.blend(ModelWithTwoMoneyFields, amount1_currency="EUR", amount2_currency="USD")
        assert isinstance(instance.amount1, Money)
        assert isinstance(instance.amount2, Money)


@pytest.mark.parametrize(
    ("attribute", "build_kwargs", "expected"),
    [
        pytest.param(
            "default_currency",
            {"max_digits": 9, "null": True, "default_currency": None},
            None,
            id="default_currency_as_none",
        ),
        pytest.param(
            "default_currency",
            {"max_digits": 9, "null": True, "default_currency": "SEK"},
            "SEK",
            id="default_currency_as_non_default_not_none",
        ),
        pytest.param(
            "currency_max_length",
            {"max_digits": 9, "currency_max_length": 4},
            4,
            id="currency_max_length_as_non_default",
        ),
    ],
)
def test_deconstruct_includes(attribute, build_kwargs, expected):
    instance = MoneyField(**build_kwargs)
    __, ___, args, kwargs = instance.deconstruct()
    new = MoneyField(*args, **kwargs)
    assert getattr(new, attribute) == getattr(instance, attribute)
    assert getattr(new, attribute) == expected
