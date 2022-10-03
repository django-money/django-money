from collections import Counter
from decimal import Decimal

import pytest

from djmoney.money import Money

from ..testapp.models import ModelWithVanillaMoneyField, NullMoneyFieldModel, ValidatedMoneyModel


pytestmark = pytest.mark.django_db
serializers = pytest.importorskip("rest_framework.serializers")
fields = pytest.importorskip("rest_framework.fields")
djmoney_fields = pytest.importorskip("djmoney.contrib.django_rest_framework.fields")


class TestMoneyField:
    def get_serializer(
        self, model_class, field_name=None, instance=None, data=fields.empty, fields_="__all__", field_kwargs=None
    ):
        class MetaSerializer(serializers.SerializerMetaclass):
            def __new__(cls, name, bases, attrs):
                from djmoney.contrib.django_rest_framework import MoneyField

                if field_name is not None and field_kwargs is not None:
                    attrs[field_name] = MoneyField(max_digits=10, decimal_places=2, **field_kwargs)
                return super().__new__(cls, name, bases, attrs)

        class Serializer(serializers.ModelSerializer, metaclass=MetaSerializer):
            class Meta:
                model = model_class
                fields = fields_

        return Serializer(instance=instance, data=data)

    @pytest.mark.parametrize(
        "model_class, create_kwargs, expected",
        (
            (NullMoneyFieldModel, {"field": None}, {"field": None, "field_currency": "USD"}),
            (NullMoneyFieldModel, {"field": Money(10, "USD")}, {"field": "10.00", "field_currency": "USD"}),
            (
                ModelWithVanillaMoneyField,
                {"money": Money(10, "USD")},
                {
                    "integer": 0,
                    "money": "10.00",
                    "money_currency": "USD",
                    "second_money": "0.00",
                    "second_money_currency": "EUR",
                },
            ),
        ),
    )
    def test_to_representation(self, model_class, create_kwargs, expected):
        instance = model_class.objects.create(**create_kwargs)
        expected["id"] = instance.id
        serializer = self.get_serializer(model_class, instance=instance)
        assert serializer.data == expected

    @pytest.mark.parametrize(
        "model_class, field, field_kwargs, value, expected",
        (
            (NullMoneyFieldModel, "field", None, None, None),
            (NullMoneyFieldModel, "field", {"default_currency": "EUR", "allow_null": True}, None, None),
            (NullMoneyFieldModel, "field", None, Money(10, "USD"), Money(10, "USD")),
            (NullMoneyFieldModel, "field", {"default_currency": "EUR"}, Money(10, "USD"), Money(10, "USD")),
            (ModelWithVanillaMoneyField, "money", {"default_currency": "EUR"}, 10, Money(10, "EUR")),
            (ModelWithVanillaMoneyField, "money", None, Money(10, "USD"), Money(10, "USD")),
            (ModelWithVanillaMoneyField, "money", {"default_currency": "EUR"}, Money(10, "USD"), Money(10, "USD")),
            (ModelWithVanillaMoneyField, "money", {"default_currency": "EUR"}, 10, Money(10, "EUR")),
        ),
    )
    def test_to_internal_value(self, model_class, field, field_kwargs, value, expected):
        serializer = self.get_serializer(model_class, field_name=field, data={field: value}, field_kwargs=field_kwargs)
        assert serializer.is_valid()
        instance = serializer.save()
        assert getattr(instance, field) == expected

    def test_invalid_value(self):
        serializer = self.get_serializer(ModelWithVanillaMoneyField, data={"money": None})
        assert not serializer.is_valid()
        error_text = "This field may not be null."
        assert serializer.errors == {"money": [error_text]}

    @pytest.mark.parametrize(
        "body, field_kwargs, expected",
        (
            ({"field": "10", "field_currency": "EUR"}, None, Money(10, "EUR")),
            ({"field": "10"}, {"default_currency": "EUR"}, Money(10, "EUR")),
            ({"field": "12.20", "field_currency": "GBP"}, None, Money(12.20, "GBP")),
            ({"field": "15.15", "field_currency": "USD"}, None, Money(15.15, "USD")),
            ({"field": None, "field_currency": None}, None, None),
            ({"field": None, "field_currency": None}, {"default_currency": "EUR"}, None),
            ({"field": "16", "field_currency": None}, None, Decimal("16.00")),
            ({"field": "16", "field_currency": None}, {"default_currency": "EUR"}, Decimal("16.00")),
            ({"field": None, "field_currency": "USD"}, None, None),
            ({"field": None, "field_currency": "USD"}, {"default_currency": "EUR"}, None),
        ),
    )
    def test_post_put_values(self, body, field_kwargs, expected):
        if field_kwargs is not None:
            field_kwargs["allow_null"] = True
        serializer = self.get_serializer(NullMoneyFieldModel, data=body, field_name="field", field_kwargs=field_kwargs)
        serializer.is_valid()
        assert serializer.validated_data["field"] == expected

    def test_serializer_with_fields(self):
        serializer = self.get_serializer(ModelWithVanillaMoneyField, data={"money": "10.00"}, fields_=("money",))
        serializer.is_valid(raise_exception=True)
        assert serializer.data == {"money": "10.00"}

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
    def test_model_validators(self, value, error):
        serializer = self.get_serializer(
            ValidatedMoneyModel, data={"money": value.amount, "money_currency": value.currency.code}
        )
        assert not serializer.is_valid()
        assert serializer.errors["money"][0] == error

    @pytest.mark.parametrize(
        "value, error",
        (
            (Money(50, "EUR"), "Ensure this value is greater than or equal to 100."),
            (Money(1500, "EUR"), "Ensure this value is less than or equal to 1000."),
        ),
    )
    def test_boundary_values(self, value, error):
        serializer = self.get_serializer(
            NullMoneyFieldModel,
            data={"field": value.amount, "field_currency": value.currency.code},
            field_name="field",
            field_kwargs={"min_value": 100, "max_value": 1000},
        )
        assert not serializer.is_valid()
        assert serializer.errors["field"][0] == error

    @pytest.mark.parametrize(
        ("data", "error_codes"),
        [
            pytest.param(
                {"money": "", "money_currency": "XUA"},
                [("money", "invalid")],
                id="amount_as_empty_string",
            ),
            pytest.param(
                {"money": None, "money_currency": "XUA"},
                [("money", "null")],
                id="amount_as_none",
            ),
            pytest.param(
                {"money": "v", "money_currency": "XUA"},
                [("money", "invalid")],
                id="amount_as_invalid_decimal",
            ),
            pytest.param(
                {"money": "0.01", "money_currency": "v"},
                [("money", "invalid_currency")],
                id="invalid_currency",
            ),
            pytest.param(
                {"money_currency": "SEK"},
                [("money", "required")],
                id="amount_key_not_in_data",
            ),
        ],
    )
    def test_errors_on(self, data, error_codes):
        class Serializer(serializers.Serializer):
            money = djmoney_fields.MoneyField(max_digits=9, decimal_places=2)

        serializer = Serializer(data=data)
        with pytest.raises(serializers.ValidationError) as err:
            serializer.is_valid(raise_exception=True)

        assert Counter([(field, code) for field, codes in err.value.get_codes().items() for code in codes]) == Counter(
            error_codes
        )

    @pytest.mark.parametrize(
        ("data", "expected"),
        [
            pytest.param({"money": "0.01", "money_currency": None}, Decimal("0.01"), id="is_none"),
            pytest.param({"money": "0.01", "money_currency": ""}, Decimal("0.01"), id="is_empty_string"),
            pytest.param({"money": "0.01"}, Decimal("0.01"), id="key_not_in_data"),
        ],
    )
    def test_returns_decimal_when_currency(self, data, expected):
        class Serializer(serializers.Serializer):
            money = djmoney_fields.MoneyField(max_digits=9, decimal_places=2)

        serializer = Serializer(data=data)
        serializer.is_valid(raise_exception=True)
        assert serializer.validated_data["money"] == expected
