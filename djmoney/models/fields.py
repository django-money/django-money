from __future__ import division
from django.db import models
from django.conf import settings
try:
    from django.db.models.expressions import Expression
except ImportError:
    # Django < 1.8
    from django.db.models.sql.expressions import SQLEvaluator as Expression
try:
    from django.utils.encoding import smart_unicode
except ImportError:
    # Python 3
    from django.utils.encoding import smart_text as smart_unicode
from django.utils import translation
from django.db.models.signals import class_prepared
from moneyed import Money, Currency, DEFAULT_CURRENCY
from moneyed.localization import _FORMATTER, format_money
from djmoney import forms
from djmoney.forms.widgets import CURRENCY_CHOICES
from djmoney.utils import get_currency_field_name
try:
    from django.db.models.expressions import BaseExpression
except ImportError:
    # Django < 1.8
    from django.db.models.expressions import ExpressionNode as BaseExpression

from decimal import Decimal, ROUND_DOWN
import inspect

try:
    unicode = unicode
except NameError:
    # 'unicode' is undefined, in Python 3
    basestring = (str, bytes)

__all__ = ('MoneyField', 'NotSupportedLookup')

SUPPORTED_LOOKUPS = ('exact', 'isnull', 'lt', 'gt', 'lte', 'gte')


class NotSupportedLookup(Exception):
    def __init__(self, lookup):
        self.lookup = lookup

    def __str__(self):
        return "Lookup '%s' is not supported for MoneyField" % self.lookup


class MoneyPatched(Money):

    # Set to True or False has a higher priority
    # than USE_L10N == True in the django settings file.
    # The variable "self.use_l10n" has three states:
    use_l10n = None

    def __float__(self):
        return float(self.amount)

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

        return MoneyPatched._patch_to_current_class(
            super(MoneyPatched, self).__add__(other))

    def __sub__(self, other):

        return MoneyPatched._patch_to_current_class(
            super(MoneyPatched, self).__sub__(other))

    def __mul__(self, other):

        return MoneyPatched._patch_to_current_class(
            super(MoneyPatched, self).__mul__(other))

    def __truediv__(self, other):

        if isinstance(other, Money):
            return super(MoneyPatched, self).__truediv__(other)
        else:
            return self._patch_to_current_class(
                super(MoneyPatched, self).__truediv__(other))

    def __rmod__(self, other):

        return MoneyPatched._patch_to_current_class(
            super(MoneyPatched, self).__rmod__(other))

    def __get_current_locale(self):
        locale = translation.to_locale(translation.get_language())

        if _FORMATTER.get_formatting_definition(locale):
            return locale

        if _FORMATTER.get_formatting_definition('%s_%s' % (locale, locale)):
            return '%s_%s' % (locale, locale)

        return ''

    def __use_l10n(self):
        """
        Return boolean.
        """
        if self.use_l10n is None:
            return settings.USE_L10N
        return self.use_l10n

    def __unicode__(self):

        if self.__use_l10n():
            locale = self.__get_current_locale()
            if locale:
                return format_money(self, locale=locale)

        return format_money(self)

    def __str__(self):

        if self.__use_l10n():
            locale = self.__get_current_locale()
            if locale:
                return format_money(self, locale=locale)

        return format_money(self)

    def __repr__(self):
        # small fix for tests
        return "%s %s" % (self.amount.to_integral_value(ROUND_DOWN),
                          self.currency)


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
            raise AttributeError('Can only be accessed via an instance.')
        if isinstance(obj.__dict__[self.field.name], BaseExpression):
            return obj.__dict__[self.field.name]
        if not isinstance(obj.__dict__[self.field.name], Money):
            obj.__dict__[self.field.name] = self._money_from_obj(obj)
        return obj.__dict__[self.field.name]

    def __set__(self, obj, value):
        if isinstance(value, tuple):
            value = Money(amount=value[0], currency=value[1])
        if isinstance(value, Money):
            obj.__dict__[self.field.name] = value.amount
            setattr(obj, self.currency_field_name,
                    smart_unicode(value.currency))
        elif isinstance(value, BaseExpression):
            if isinstance(value.children[1], Money):
                value.children[1] = value.children[1].amount
            obj.__dict__[self.field.name] = value
        else:
            if value:
                value = str(value)
            obj.__dict__[self.field.name] = self.field.to_python(value)


class CurrencyField(models.CharField):
    description = "A field which stores currency."

    def __init__(self, price_field=None, verbose_name=None, name=None,
                 default=DEFAULT_CURRENCY, **kwargs):
        if isinstance(default, Currency):
            default = default.code
        kwargs['max_length'] = 3
        self.price_field = price_field
        self.frozen_by_south = kwargs.pop('frozen_by_south', False)
        super(CurrencyField, self).__init__(verbose_name, name, default=default,
                                            **kwargs)

    def get_internal_type(self):
        return "CharField"

    def contribute_to_class(self, cls, name):
        if not self.frozen_by_south and not name in [f.name for f in cls._meta.fields]:
            super(CurrencyField, self).contribute_to_class(cls, name)


class MoneyField(models.DecimalField):
    description = "A field which stores both the currency and amount of money."

    def __init__(self, verbose_name=None, name=None,
                 max_digits=None, decimal_places=None,
                 default=None,
                 default_currency=DEFAULT_CURRENCY,
                 currency_choices=CURRENCY_CHOICES, **kwargs):

        nullable = kwargs.get('null', False)
        if default is None and not nullable:
            # Backwards compatible fix for non-nullable fields
            default = 0.0

        if isinstance(default, basestring):
            try:
                # handle scenario where default is formatted like:
                # 'amount currency-code'
                amount, currency = default.split(" ")
            except ValueError:
                # value error would be risen if the default is
                # without the currency part, i.e
                # 'amount'
                amount = default
                currency = default_currency
            default = Money(float(amount), Currency(code=currency))
        elif isinstance(default, (float, Decimal, int)):
            default = Money(default, default_currency)

        if not (nullable and default is None) and not isinstance(default, Money):
            raise Exception(
                "default value must be an instance of Money, is: %s" % str(
                    default))

        # Avoid giving the user hard-to-debug errors if they miss required attributes
        if max_digits is None:
            raise Exception(
                "You have to provide a max_digits attribute to Money fields.")

        if decimal_places is None:
            raise Exception(
                "You have to provide a decimal_places attribute to Money fields.")

        if not default_currency:
            default_currency = default.currency

        self.default_currency = default_currency
        self.currency_choices = currency_choices
        self.frozen_by_south = kwargs.pop('frozen_by_south', False)

        super(MoneyField, self).__init__(verbose_name, name, max_digits,
                                         decimal_places, default=default,
                                         **kwargs)

    def to_python(self, value):
        if isinstance(value, Expression):
            return value
        if isinstance(value, Money):
            value = value.amount
        if isinstance(value, tuple):
            value = value[0]
        return super(MoneyField, self).to_python(value)

    def get_internal_type(self):
        return "DecimalField"

    def contribute_to_class(self, cls, name):

        cls._meta.has_money_field = True

        # Don't run on abstract classes
        # Removed, see https://github.com/jakewins/django-money/issues/42
        #if cls._meta.abstract:
        #    return

        if not self.frozen_by_south:
            c_field_name = get_currency_field_name(name)
            # Do not change default=self.default_currency.code, needed
            # for south compat.
            c_field = CurrencyField(
                max_length=3, price_field=self,
                default=self.default_currency, editable=False,
                choices=self.currency_choices
            )
            c_field.creation_counter = self.creation_counter
            cls.add_to_class(c_field_name, c_field)

        super(MoneyField, self).contribute_to_class(cls, name)

        setattr(cls, self.name, MoneyFieldProxy(self))

    def get_db_prep_save(self, value, connection):
        if isinstance(value, Expression):
            return value
        if isinstance(value, Money):
            value = value.amount
        return super(MoneyField, self).get_db_prep_save(value, connection)

    def get_db_prep_lookup(self, lookup_type, value, connection,
                           prepared=False):
        if not lookup_type in SUPPORTED_LOOKUPS:
            raise NotSupportedLookup(lookup_type)
        value = self.get_db_prep_save(value, connection)
        return super(MoneyField, self).get_db_prep_lookup(lookup_type, value,
                                                          connection, prepared)

    def get_default(self):
        if isinstance(self.default, Money):
            frm = inspect.stack()[1]
            mod = inspect.getmodule(frm[0])
            # We need to return the numerical value if this is called by south
            if mod.__name__ == "south.db.generic":
                return float(self.default.amount)
            return self.default
        else:
            return super(MoneyField, self).get_default()

    def formfield(self, **kwargs):
        defaults = {'form_class': forms.MoneyField}
        defaults.update(kwargs)
        defaults['currency_choices'] = self.currency_choices
        return super(MoneyField, self).formfield(**defaults)

    def get_south_default(self):
        return '%s' % str(self.default)

    def get_south_default_currency(self):
        return '"%s"' % str(self.default_currency.code)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)

    ## South support
    def south_field_triple(self):
        "Returns a suitable description of this field for South."
        # Note: This method gets automatically with schemamigration time.
        from south.modelsinspector import introspector
        field_class = self.__class__.__module__ + "." + self.__class__.__name__
        args, kwargs = introspector(self)
        # We need to
        # 1. Delete the default, 'cause it's not automatically supported.
        kwargs.pop('default')
        # 2. add the default currency, because it's not picked up from the inspector automatically.
        kwargs['default_currency'] = "'%s'" % self.default_currency
        return field_class, args, kwargs

    ## Django 1.7 migration support
    def deconstruct(self):
        name, path, args, kwargs = super(MoneyField, self).deconstruct()

        if self.default:
            kwargs['default'] = self.default.amount
        if self.default_currency != DEFAULT_CURRENCY:
            kwargs['default_currency'] = self.default_currency
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
    add_introspection_rules(rules, ["^djmoney\.models\.fields\.CurrencyField"])
except ImportError:
    pass


def patch_managers(sender, **kwargs):
    """
    Patches models managers
    """
    from .managers import money_manager

    if hasattr(sender._meta, 'has_money_field'):
        for _id, name, manager in sender._meta.concrete_managers:
            setattr(sender, name, money_manager(manager))


class_prepared.connect(patch_managers)
