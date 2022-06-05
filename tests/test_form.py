"""
Created on May 7, 2011

@author: jake
"""
from decimal import Decimal

import pytest

from djmoney import settings
from djmoney.models.fields import MoneyField
from djmoney.money import Money

from .testapp.forms import (
    DefaultMoneyModelForm,
    DefaultPrecisionModelForm,
    DisabledFieldForm,
    MoneyForm,
    MoneyFormMultipleCurrencies,
    MoneyModelForm,
    MoneyModelFormWithValidation,
    NullableModelForm,
    OptionalMoneyForm,
    PositiveValidatedMoneyModelForm,
    PreciseForm,
    PreciseModelForm,
    ValidatedMoneyModelForm,
)
from .testapp.models import ModelWithVanillaMoneyField, NullMoneyFieldModel


pytestmark = pytest.mark.django_db


def test_save():
    money = Money(Decimal("10"), "SEK")
    form = MoneyModelForm({"money_0": money.amount, "money_1": money.currency})

    assert form.is_valid()
    instance = form.save()

    retrieved = ModelWithVanillaMoneyField.objects.get(pk=instance.pk)
    assert money == retrieved.money


def test_validate():
    money = Money(Decimal("10"), "SEK")
    form = MoneyForm({"money_0": money.amount, "money_1": money.currency})

    assert form.is_valid()

    result = form.cleaned_data["money"]
    assert result == money


@pytest.mark.parametrize(
    "data",
    (
        {"money_0": "xyz*|\\", "money_1": "SEK"},
        {"money_0": 10000, "money_1": "SEK"},
        {"money_0": 1, "money_1": "SEK"},
        {"money_0": 10, "money_1": "EUR"},
    ),
)
def test_form_is_invalid(data):
    assert not MoneyForm(data).is_valid()


@pytest.mark.parametrize(
    "data, result", (({"money_0": "", "money_1": "SEK"}, []), ({"money_0": "1.23", "money_1": "SEK"}, ["money"]))
)
def test_changed_data(data, result):
    assert MoneyForm(data).changed_data == result


def test_change_currency_not_amount():
    """
    If the amount is the same, but the currency changes, then we
    should consider this to be a change.
    """
    form = MoneyFormMultipleCurrencies(
        {"money_0": Decimal(10), "money_1": "EUR"}, initial={"money": Money(Decimal(10), "SEK")}
    )
    assert form.changed_data == ["money"]


@pytest.mark.parametrize(
    "data, result",
    (
        ({"money_1": "SEK"}, True),
        ({"money_0": "", "money_1": "SEK"}, True),
        ({"money_0": "xyz*|\\", "money_1": "SEK"}, False),
    ),
)
def test_optional_money_form(data, result):
    """
    The currency widget means that 'money_1' will always be filled
    in, but 'money_0' could be absent/empty.
    """
    assert OptionalMoneyForm(data).is_valid() is result


def test_default_currency():
    """
    If field is nullable, then field's default_currency value should be selected by default.
    """
    instance = NullMoneyFieldModel.objects.create()
    form = NullableModelForm(instance=instance)
    assert '<option value="USD" selected>US Dollar</option>' in form.as_p()


def test_fields_default_amount_becomes_forms_initial():
    """
    Formfield should take field's default amount
    and put it in form field's initial value
    """
    form = DefaultMoneyModelForm()
    assert form.fields["money"].initial == [123, "PLN"]


def test_no_deprecation_warning():
    """
    The library's code shouldn't generate any warnings itself. See #262.
    """
    with pytest.warns(None) as warning:
        MoneyField(max_digits=10, decimal_places=2, currency_choices=(("USD", "USD"),)).formfield()
    assert not warning


class TestValidation:
    @pytest.mark.parametrize(
        "value, error",
        (
            (Money(50, "EUR"), "Ensure this value is greater than or equal to €100.00."),
            (Money(1500, "EUR"), "Ensure this value is less than or equal to €1,000.00."),
            (Money(40, "USD"), "Ensure this value is greater than or equal to $50.00."),
            (Money(600, "USD"), "Ensure this value is less than or equal to $500.00."),
            (Money(400, "NOK"), "Ensure this value is greater than or equal to NOK500.00."),
            (Money(950, "NOK"), "Ensure this value is less than or equal to NOK900.00."),
            (Money(5, "SEK"), "Ensure this value is greater than or equal to 10."),
            (Money(1600, "SEK"), "Ensure this value is less than or equal to 1500."),
        ),
    )
    def test_invalid(self, value, error):
        form = ValidatedMoneyModelForm(data={"money_0": value.amount, "money_1": value.currency})
        assert not form.is_valid()
        assert form.errors == {"money": [error]}

    @pytest.mark.parametrize("value", (Money(150, "EUR"), Money(200, "USD"), Money(50, "SEK"), Money(600, "NOK")))
    def test_valid(self, value):
        assert ValidatedMoneyModelForm(data={"money_0": value.amount, "money_1": value.currency}).is_valid()

    @pytest.mark.parametrize("value", (Money(-0.01, "EUR"), Money(-1, "USD"), Money(-10, "NOK"), Money(-100, "SEK")))
    def test_non_negative_validator(self, value):
        """Fails if Validator(0) silently allows negative values."""
        form = PositiveValidatedMoneyModelForm(data={"money_0": value.amount, "money_1": value.currency})
        assert not form.is_valid()
        assert form.errors == {"money": ["Ensure this value is greater than or equal to 0."]}

    @pytest.mark.parametrize(
        "value", (Money(0, "PHP"), Money(0.01, "EUR"), Money(1, "USD"), Money(10, "NOK"), Money(100, "SEK"))
    )
    def test_positive_validator(self, value):
        """Fails if MinMoneyValidator(0) blocks positive values.

        MinMoneyValidator(0) should also allow exactly 0.
        """
        form = PositiveValidatedMoneyModelForm(data={"money_0": value.amount, "money_1": value.currency})
        assert form.is_valid()

    def test_default_django_validator(self):
        form = MoneyModelFormWithValidation(data={"balance_0": 0, "balance_1": "GBP"})
        assert not form.is_valid()
        assert form.errors == {"balance": ["Ensure this value is greater than or equal to £100.00."]}


class TestDisabledField:
    def test_validation(self):
        instance = ModelWithVanillaMoneyField.objects.create(money=Money("42.00", "USD"))
        form = DisabledFieldForm(data={}, instance=instance)
        assert not form.errors
        assert form.is_valid()

    def test_has_changed(self):
        form = DisabledFieldForm(data={})
        assert not form.has_changed()


@pytest.mark.parametrize("model_class", (PreciseForm, DefaultPrecisionModelForm))
def test_decimal_places_model_form(model_class):
    """Forms should use DECIMAL_PLACES setting value when none specified."""

    expected = str(10**-settings.DECIMAL_PLACES)
    assert model_class().fields["money"].widget.widgets[0].attrs["step"] == expected


def test_precedence_decimal_places_model_form():
    """Forms should use decimal_places in field value when specified."""

    decimal_places = PreciseModelForm.Meta.model._meta.fields[2].decimal_places
    expected = str(10**-decimal_places)
    assert PreciseModelForm().fields["money"].widget.widgets[0].attrs["step"] == expected
