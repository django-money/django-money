# -*- coding: utf-8 -*-
from rest_framework.compat import MinValueValidator, MaxValueValidator
from rest_framework.fields import empty
from rest_framework.serializers import DecimalField, ModelSerializer

from djmoney.models.fields import MoneyField as ModelField
from djmoney.models.validators import MinMoneyValidator, MaxMoneyValidator
from djmoney.money import Money
from djmoney.utils import MONEY_CLASSES, get_currency_field_name


class MoneyField(DecimalField):
    """
    Treats ``Money`` objects as decimal values in representation and
    does decimal's validation during transformation to native value.
    """

    def __init__(self, *args, **kwargs):
        self.default_currency = kwargs.pop('default_currency', None)
        super(MoneyField, self).__init__(*args, **kwargs)
        # patches wrong validators for drf
        validators = self.validators
        print(type(validators))
        for i in range(len(validators)):
            if isinstance(validators[i], MinValueValidator):
                validators[i] = MinMoneyValidator(self.min_value)
            elif isinstance(validators[i], MaxValueValidator):
                validators[i] = MaxMoneyValidator(self.max_value)
        self.validators = validators

    def to_representation(self, obj):
        """
        When ``field_currency`` is not in ``self.validated_data`` then ``obj`` is an instance of ``Decimal``, otherwise
        it is ``Money``.
        """
        if isinstance(obj, MONEY_CLASSES):
            obj = obj.amount
        return super(MoneyField, self).to_representation(obj)

    def to_internal_value(self, data):
        if isinstance(data, MONEY_CLASSES):
            amount = super(MoneyField, self).to_internal_value(data.amount)
            return Money(amount, data.currency)
        return super(MoneyField, self).to_internal_value(data)

    def get_value(self, data):
        amount = super(MoneyField, self).get_value(data)
        currency = data.get(get_currency_field_name(self.field_name), self.default_currency)
        if currency and amount is not None and not isinstance(amount, MONEY_CLASSES) and amount is not empty:
            return Money(amount, currency)
        return amount


def register_money_field():
    ModelSerializer.serializer_field_mapping[ModelField] = MoneyField
