# -*- coding: utf-8 -*-
from __future__ import division

from decimal import Decimal
from warnings import warn

from django import VERSION
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Field, Func, Value
from django.db.models.expressions import BaseExpression
from django.db.models.signals import class_prepared
from django.utils.functional import cached_property

from djmoney import forms
from djmoney.money import Currency, Money
from moneyed import Money as OldMoney

from .._compat import (
    MoneyValidator,
    setup_managers,
    smart_unicode,
    string_types,
)
from ..settings import CURRENCY_CHOICES, DEFAULT_CURRENCY
from ..utils import MONEY_CLASSES, get_currency_field_name, prepare_expression


__all__ = ('MoneyField', )


def get_value(obj, expr):
    """
    Extracts value from object or expression.
    """
    if isinstance(expr, F):
        expr = getattr(obj, expr.name)
    else:
        expr = expr.value
    if isinstance(expr, OldMoney):
        expr.__class__ = Money
    return expr


def validate_money_expression(obj, expr):
    """
    Money supports different types of expressions, but you can't do following:
      - Add or subtract money with not-money
      - Any exponentiation
      - Any operations with money in different currencies
      - Multiplication, division, modulo with money instances on both sides of expression
    """
    connector = expr.connector
    lhs = get_value(obj, expr.lhs)
    rhs = get_value(obj, expr.rhs)

    if (not isinstance(rhs, Money) and connector in ('+', '-')) or connector == '^':
        raise ValidationError('Invalid F expression for MoneyField.', code='invalid')
    if isinstance(lhs, Money) and isinstance(rhs, Money):
        if connector in ('*', '/', '^', '%%'):
            raise ValidationError('Invalid F expression for MoneyField.', code='invalid')
        if lhs.currency != rhs.currency:
            raise ValidationError('You cannot use F() with different currencies.', code='invalid')


def validate_money_value(value):
    """
    Valid value for money are:
      - Single numeric value
      - Money instances
      - Pairs of numeric value and currency. Currency can't be None.
    """
    if isinstance(value, (list, tuple)) and (len(value) != 2 or value[1] is None):
        raise ValidationError(
            'Invalid value for MoneyField: %(value)s.',
            code='invalid',
            params={'value': value},
        )


def get_currency(value):
    """
    Extracts currency from value.
    """
    if isinstance(value, MONEY_CLASSES):
        return smart_unicode(value.currency)
    elif isinstance(value, (list, tuple)):
        return value[1]


class MoneyFieldProxy(object):

    def __init__(self, field):
        self.field = field
        self.currency_field_name = get_currency_field_name(self.field.name, self.field)

    def _money_from_obj(self, obj):
        amount = obj.__dict__[self.field.name]
        currency = obj.__dict__[self.currency_field_name]
        if amount is None:
            return None
        return Money(amount=amount, currency=currency)

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        data = obj.__dict__
        if isinstance(data[self.field.name], BaseExpression):
            return data[self.field.name]
        if not isinstance(data[self.field.name], Money):
            data[self.field.name] = self._money_from_obj(obj)
        return data[self.field.name]

    def __set__(self, obj, value):  # noqa
        if value is not None and self.field._currency_field.null and not isinstance(value, MONEY_CLASSES + (Decimal,)):
            # For nullable fields we need either both NULL amount and currency or both NOT NULL
            raise ValueError('Missing currency value')
        if isinstance(value, BaseExpression):
            if isinstance(value, Value):
                value = self.prepare_value(obj, value.value)
            elif not isinstance(value, Func):
                validate_money_expression(obj, value)
                prepare_expression(value)
        else:
            value = self.prepare_value(obj, value)
        obj.__dict__[self.field.name] = value

    def prepare_value(self, obj, value):
        validate_money_value(value)
        currency = get_currency(value)
        if currency:
            self.set_currency(obj, currency)
        return self.field.to_python(value)

    def set_currency(self, obj, value):
        # we have to determine whether to replace the currency.
        # i.e. if we do the following:
        # .objects.get_or_create(money_currency='EUR')
        # then the currency is already set up, before this code hits
        # __set__ of MoneyField. This is because the currency field
        # has less creation counter than money field.
        #
        # Gotcha:
        # But we should also allow setting a field back to its original default
        # value!
        # https://github.com/django-money/django-money/issues/221
        object_currency = obj.__dict__.get(self.currency_field_name)
        if object_currency != value:
            # in other words, update the currency only if it wasn't
            # changed before.
            setattr(obj, self.currency_field_name, value)


class CurrencyField(models.CharField):
    description = 'A field which stores currency.'

    def __init__(self, price_field=None, default=DEFAULT_CURRENCY, **kwargs):
        if isinstance(default, Currency):
            default = default.code
        kwargs['max_length'] = 3
        self.price_field = price_field
        super(CurrencyField, self).__init__(default=default, **kwargs)

    def contribute_to_class(self, cls, name):
        if name not in [f.name for f in cls._meta.fields]:
            super(CurrencyField, self).contribute_to_class(cls, name)


class MoneyField(models.DecimalField):
    description = 'A field which stores both the currency and amount of money.'

    def __init__(self, verbose_name=None, name=None,
                 max_digits=None, decimal_places=None,
                 default=None,
                 default_currency=DEFAULT_CURRENCY,
                 currency_choices=CURRENCY_CHOICES,
                 currency_field_name=None, **kwargs):
        nullable = kwargs.get('null', False)
        default = self.setup_default(default, default_currency, nullable)
        if not default_currency and default is not None:
            default_currency = default.currency

        self.default_currency = default_currency
        self.currency_choices = currency_choices
        self.currency_field_name = currency_field_name

        super(MoneyField, self).__init__(verbose_name, name, max_digits, decimal_places, default=default, **kwargs)
        self.creation_counter += 1
        Field.creation_counter += 1

    def setup_default(self, default, default_currency, nullable):
        if default is None and not nullable:
            # Backwards compatible fix for non-nullable fields
            default = 0.0
        if isinstance(default, string_types):
            try:
                # handle scenario where default is formatted like:
                # 'amount currency-code'
                amount, currency = default.split(' ')
            except ValueError:
                # value error would be risen if the default is
                # without the currency part, i.e
                # 'amount'
                amount = default
                currency = default_currency
            default = Money(Decimal(amount), Currency(code=currency))
        elif isinstance(default, (float, Decimal, int)):
            default = Money(default, default_currency)
        elif isinstance(default, OldMoney):
            default.__class__ = Money
        if not (nullable and default is None) and not isinstance(default, Money):
            raise ValueError('default value must be an instance of Money, is: %s' % default)
        return default

    def to_python(self, value):
        if isinstance(value, MONEY_CLASSES):
            value = value.amount
        elif isinstance(value, tuple):
            value = value[0]
        if isinstance(value, float):
            value = str(value)
        return super(MoneyField, self).to_python(value)

    def clean(self, value, model_instance):
        """
        We need to run validation against ``Money`` instance.
        """
        output = self.to_python(value)
        self.validate(value, model_instance)
        self.run_validators(value)
        return output

    if VERSION[:2] > (1, 8):

        @cached_property
        def validators(self):
            """
            Default ``DecimalValidator`` doesn't work with ``Money`` instances.
            """
            return super(models.DecimalField, self).validators + [
                MoneyValidator(self.max_digits, self.decimal_places)
            ]

    def contribute_to_class(self, cls, name):
        cls._meta.has_money_field = True

        if not hasattr(self, '_currency_field'):
            self.add_currency_field(cls, name)

        super(MoneyField, self).contribute_to_class(cls, name)

        setattr(cls, self.name, MoneyFieldProxy(self))

    def add_currency_field(self, cls, name):
        """
        Adds CurrencyField instance to a model class.
        """
        currency_field = CurrencyField(
            price_field=self,
            default=self.default_currency, editable=False,
            choices=self.currency_choices, null=self.default_currency is None
        )
        currency_field.creation_counter = self.creation_counter - 1
        currency_field_name = get_currency_field_name(name, self)
        cls.add_to_class(currency_field_name, currency_field)
        self._currency_field = currency_field

    def get_db_prep_save(self, value, connection):
        if isinstance(value, MONEY_CLASSES):
            value = value.amount
        return super(MoneyField, self).get_db_prep_save(value, connection)

    def get_default(self):
        if isinstance(self.default, Money):
            return self.default
        else:
            return super(MoneyField, self).get_default()

    def formfield(self, **kwargs):
        defaults = {'form_class': forms.MoneyField}
        defaults.update(kwargs)
        defaults['currency_choices'] = self.currency_choices
        defaults['default_currency'] = self.default_currency
        if self.default is not None:
            defaults['default_amount'] = self.default.amount
        return super(MoneyField, self).formfield(**defaults)

    def value_to_string(self, obj):
        if VERSION == (1, 8):
            value = self._get_val_from_obj(obj)
        else:
            value = self.value_from_object(obj)
        return self.get_prep_value(value)

    def deconstruct(self):
        name, path, args, kwargs = super(MoneyField, self).deconstruct()

        if self.default is not None:
            kwargs['default'] = self.default.amount
        if self.default_currency != DEFAULT_CURRENCY:
            kwargs['default_currency'] = str(self.default_currency)
        if self.currency_choices != CURRENCY_CHOICES:
            kwargs['currency_choices'] = self.currency_choices
        if self.currency_field_name:
            kwargs['currency_field_name'] = self.currency_field_name
        return name, path, args, kwargs


def patch_managers(sender, **kwargs):
    """
    Patches models managers.
    """
    if sender._meta.proxy_for_model:
        has_money_field = hasattr(sender._meta.proxy_for_model._meta, 'has_money_field')
    else:
        has_money_field = hasattr(sender._meta, 'has_money_field')

    if has_money_field:
        setup_managers(sender)


class_prepared.connect(patch_managers)


class MoneyPatched(Money):

    def __init__(self, *args, **kwargs):
        warn(
            "'djmoney.models.fields.MoneyPatched' is deprecated. Use 'djmoney.money.Money' instead",
            PendingDeprecationWarning
        )
        super(MoneyPatched, self).__init__(*args, **kwargs)
