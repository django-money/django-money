# coding: utf-8
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import (
    BaseValidator,
    MaxValueValidator,
    MinValueValidator,
)

from djmoney.money import Money


class BaseMoneyValidator(BaseValidator):

    def get_limit_value(self, cleaned):
        if isinstance(self.limit_value, Money):
            if cleaned.currency.code != self.limit_value.currency.code:
                return
            return self.limit_value
        elif isinstance(self.limit_value, (int, Decimal)):
            return self.limit_value
        try:
            return Money(self.limit_value[cleaned.currency.code], cleaned.currency.code)
        except KeyError:
            # There are no validation for this currency
            pass

    def __call__(self, value):
        cleaned = self.clean(value)
        limit_value = self.get_limit_value(cleaned)
        if limit_value is None:
            return
        if isinstance(limit_value, (int, Decimal)):
            cleaned = cleaned.amount
        params = {'limit_value': limit_value, 'show_value': cleaned, 'value': value}
        if self.compare(cleaned, limit_value):
            raise ValidationError(self.message, code=self.code, params=params)


class MinMoneyValidator(BaseMoneyValidator, MinValueValidator):
    pass


class MaxMoneyValidator(BaseMoneyValidator, MaxValueValidator):
    pass
