# -*- coding: utf-8 -*-
from __future__ import division

import inspect
from decimal import ROUND_DOWN, Decimal

from django import VERSION
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.db import models
from django.db.models import F, Field
from django.db.models.signals import class_prepared
from django.utils import translation

from djmoney import forms
from moneyed import Currency, Money
from moneyed.localization import _FORMATTER, format_money

from .._compat import (
    BaseExpression,
    Func,
    Value,
    deconstructible,
    setup_managers,
    smart_unicode,
    split_expression,
    string_types,
)
from ..settings import CURRENCY_CHOICES, DECIMAL_PLACES, DEFAULT_CURRENCY
from ..utils import get_currency_field_name, prepare_expression


__all__ = ('MoneyField', )


@deconstructible
class MoneyPatched(Money):

    # Set to True or False has a higher priority
    # than USE_L10N == True in the django settings file.
    # The variable "self.use_l10n" has three states:
    use_l10n = None

    def __float__(self):
        return float(self.amount)

    def _convert_to_local_currency(self, other):
        """
        Converts other Money instances to the local currency.
        If django-money-rates is installed we can automatically perform operations with different currencies
        """
        if getattr(settings, 'AUTO_CONVERT_MONEY', False):
            if 'djmoney_rates' in settings.INSTALLED_APPS:
                try:
                    from djmoney_rates.utils import convert_money

                    return convert_money(other.amount, other.currency, self.currency)
                except ImportError:
                    raise ImproperlyConfigured('djmoney_rates doesn\'t support Django 1.9+')
            raise ImproperlyConfigured('You must install djmoney-rates to use AUTO_CONVERT_MONEY = True')
        return other

    @classmethod
    def _patch_to_current_class(cls, money):
        """
        Converts object of type MoneyPatched on the object of type Money.
        """
        return cls(money.amount, money.currency)

    def __pos__(self):
        return MoneyPatched._patch_to_current_class(
            super(MoneyPatched, self).__pos__())

    def __neg__(self):
        return MoneyPatched._patch_to_current_class(
            super(MoneyPatched, self).__neg__())

    def __add__(self, other):
        other = self._convert_to_local_currency(other)
        return MoneyPatched._patch_to_current_class(
            super(MoneyPatched, self).__add__(other))

    def __sub__(self, other):
        other = self._convert_to_local_currency(other)
        return MoneyPatched._patch_to_current_class(
            super(MoneyPatched, self).__sub__(other))

    def __mul__(self, other):
        return MoneyPatched._patch_to_current_class(
            super(MoneyPatched, self).__mul__(other))

    def __eq__(self, other):
        if hasattr(other, 'currency'):
            if self.currency == other.currency:
                return self.amount == other.amount
        return False

    def __truediv__(self, other):
        result = super(MoneyPatched, self).__truediv__(other)
        if isinstance(other, Money):
            return result
        return self._patch_to_current_class(result)

    def __rmod__(self, other):
        return MoneyPatched._patch_to_current_class(
            super(MoneyPatched, self).__rmod__(other))

    def __get_current_locale(self):
        # get_language can return None starting on django 1.8
        language = translation.get_language() or settings.LANGUAGE_CODE
        locale = translation.to_locale(language)

        if locale.upper() in _FORMATTER.formatting_definitions:
            return locale

        locale = ('%s_%s' % (locale, locale)).upper()
        if locale in _FORMATTER.formatting_definitions:
            return locale

        return ''

    def __use_l10n(self):
        """
        Return boolean.
        """
        if self.use_l10n is None:
            return settings.USE_L10N
        return self.use_l10n

    def __unicode__(self):
        kwargs = {'money': self, 'decimal_places': DECIMAL_PLACES}
        if self.__use_l10n():
            locale = self.__get_current_locale()
            if locale:
                kwargs['locale'] = locale

        return format_money(**kwargs)

    def __str__(self):
        value = self.__unicode__()
        if not isinstance(value, str):
            value = value.encode('utf8')
        return value

    def __repr__(self):
        return '%s %s' % (self.amount.to_integral_value(ROUND_DOWN), self.currency)


def get_value(obj, expr):
    """
    Extracts value from object or expression.
    """
    if isinstance(expr, F):
        expr = getattr(obj, expr.name)
    elif hasattr(expr, 'value'):
        expr = expr.value
    return expr


def validate_money_expression(obj, expr):
    """
    Money supports different types of expressions, but you can't do following:
      - Add or subtract money with not-money
      - Any exponentiation
      - Any operations with money in different currencies
      - Multiplication, division, modulo with money instances on both sides of expression
    """
    lhs, rhs = split_expression(expr)
    connector = expr.connector
    lhs = get_value(obj, lhs)
    rhs = get_value(obj, rhs)

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
    if isinstance(value, Money):
        return smart_unicode(value.currency)
    elif isinstance(value, (list, tuple)):
        return value[1]


class MoneyFieldProxy(object):

    def __init__(self, field):
        self.field = field
        self.currency_field_name = get_currency_field_name(self.field.name)

    def _money_from_obj(self, obj):
        amount = obj.__dict__[self.field.name]
        currency = obj.__dict__[self.currency_field_name]
        if amount is None:
            return None
        return MoneyPatched(amount=amount, currency=currency)

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
        if isinstance(value, BaseExpression):
            if Value and isinstance(value, Value):
                value = self.prepare_value(obj, value.value)
            elif Func and isinstance(value, Func):
                pass
            else:
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
        object_currency = obj.__dict__[self.currency_field_name]
        if object_currency != value:
            # in other words, update the currency only if it wasn't
            # changed before.
            setattr(obj, self.currency_field_name, value)


class CurrencyField(models.CharField):
    description = 'A field which stores currency.'

    def __init__(self, price_field=None, verbose_name=None, name=None,
                 default=DEFAULT_CURRENCY, **kwargs):
        if isinstance(default, Currency):
            default = default.code
        kwargs['max_length'] = 3
        self.price_field = price_field
        self.frozen_by_south = kwargs.pop('frozen_by_south', False)
        super(CurrencyField, self).__init__(verbose_name, name, default=default,
                                            **kwargs)

    def contribute_to_class(self, cls, name):
        if not self.frozen_by_south and name not in [f.name for f in cls._meta.fields]:
            super(CurrencyField, self).contribute_to_class(cls, name)


class MoneyField(models.DecimalField):
    description = 'A field which stores both the currency and amount of money.'

    def __init__(self, verbose_name=None, name=None,
                 max_digits=None, decimal_places=None,
                 default=None,
                 default_currency=DEFAULT_CURRENCY,
                 currency_choices=CURRENCY_CHOICES, **kwargs):
        nullable = kwargs.get('null', False)
        default = self.setup_default(default, default_currency, nullable)
        if not default_currency:
            default_currency = default.currency

        if VERSION < (1, 7):
            self.check_field_attributes(decimal_places, max_digits)

        self.default_currency = default_currency
        self.currency_choices = currency_choices
        self.frozen_by_south = kwargs.pop('frozen_by_south', False)

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
        if not (nullable and default is None) and not isinstance(default, Money):
            raise ValueError('default value must be an instance of Money, is: %s' % default)
        return default

    def check_field_attributes(self, decimal_places, max_digits):
        """
        Django < 1.7 has no system checks framework.
        Avoid giving the user hard-to-debug errors if they miss required attributes.
        """
        if max_digits is None:
            raise ValueError('You have to provide a max_digits attribute to Money fields.')
        if decimal_places is None:
            raise ValueError('You have to provide a decimal_places attribute to Money fields.')

    def to_python(self, value):
        if isinstance(value, Money):
            value = value.amount
        if isinstance(value, tuple):
            value = value[0]
        if isinstance(value, float):
            value = str(value)
        return super(MoneyField, self).to_python(value)

    def contribute_to_class(self, cls, name):
        cls._meta.has_money_field = True

        if not self.frozen_by_south:
            self.add_currency_field(cls, name)

        super(MoneyField, self).contribute_to_class(cls, name)

        setattr(cls, self.name, MoneyFieldProxy(self))

    def add_currency_field(self, cls, name):
        """
        Adds CurrencyField instance to a model class.
        """
        currency_field = CurrencyField(
            max_length=3, price_field=self,
            default=self.default_currency, editable=False,
            choices=self.currency_choices
        )
        currency_field.creation_counter = self.creation_counter - 1
        currency_field_name = get_currency_field_name(name)
        cls.add_to_class(currency_field_name, currency_field)

    def get_db_prep_save(self, value, connection):
        if isinstance(value, Money):
            value = value.amount
        return super(MoneyField, self).get_db_prep_save(value, connection)

    def get_default(self):
        if isinstance(self.default, Money):
            frm = inspect.stack()[1]
            mod = inspect.getmodule(frm[0])
            # We need to return the numerical value if this is called by south
            if mod is not None and mod.__name__.startswith('south.db'):
                return self.default.amount
            return self.default
        else:
            return super(MoneyField, self).get_default()

    def formfield(self, **kwargs):
        defaults = {'form_class': forms.MoneyField}
        defaults.update(kwargs)
        defaults['choices'] = self.currency_choices
        defaults['default_currency'] = self.default_currency
        if self.default is not None:
            defaults['default_amount'] = self.default.amount
        return super(MoneyField, self).formfield(**defaults)

    def value_to_string(self, obj):
        if VERSION < (2, 0):
            value = self._get_val_from_obj(obj)
        else:
            value = self.value_from_object(obj)
        return self.get_prep_value(value)

    # South support
    def south_field_triple(self):
        """Returns a suitable description of this field for South."""
        # Note: This method gets automatically with schemamigration time.
        from south.modelsinspector import introspector
        field_class = self.__class__.__module__ + '.' + self.__class__.__name__
        args, kwargs = introspector(self)
        # We need to
        # 1. Delete the default, 'cause it's not automatically supported.
        kwargs.pop('default')
        # 2. add the default currency, because it's not picked up from the inspector automatically.
        kwargs['default_currency'] = "'%s'" % self.default_currency
        return field_class, args, kwargs

    # Django 1.7 migration support
    def deconstruct(self):
        name, path, args, kwargs = super(MoneyField, self).deconstruct()

        if self.default is not None:
            kwargs['default'] = self.default.amount
        if self.default_currency != DEFAULT_CURRENCY:
            kwargs['default_currency'] = str(self.default_currency)
        if self.currency_choices != CURRENCY_CHOICES:
            kwargs['currency_choices'] = self.currency_choices
        return name, path, args, kwargs


try:
    from south.modelsinspector import add_introspection_rules
    rules = [
        # MoneyField has its own method.
        ((CurrencyField,),
         [],  # No positional args
         {'default': ('default', {'default': DEFAULT_CURRENCY.code}),
          'max_length': ('max_length', {'default': 3})}),
    ]

    # MoneyField implement the serialization in south_field_triple method
    add_introspection_rules(rules, ['^djmoney\.models\.fields\.CurrencyField'])
except ImportError:
    pass


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
