from django.db import models
from django.utils.encoding import smart_unicode
from exceptions import Exception
from moneyed import Money, Currency, DEFAULT_CURRENCY
from djmoney import forms
from djmoney.forms.widgets import CURRENCY_CHOICES

from decimal import Decimal

__all__ = ('MoneyField', 'currency_field_name', 'NotSupportedLookup')

currency_field_name = lambda name: "%s_currency" % name
SUPPORTED_LOOKUPS = ('exact', 'lt', 'gt', 'lte', 'gte')

class NotSupportedLookup(Exception):
    def __init__(self, lookup):
        self.lookup = lookup
    def __str__(self):
        return "Lookup '%s' is not supported for MoneyField" % self.lookup


class MoneyPatched(Money):
    def __float__(self):
         return float(self.amount)
         
         
class MoneyFieldProxy(object):
    def __init__(self, field):
        self.field = field
        self.currency_field_name = currency_field_name(self.field.name)
    
    def _money_from_obj(self, obj):
        value = obj.__dict__[self.field.name], obj.__dict__[self.currency_field_name]
        if value[0] is None:
            return None
        return MoneyPatched(amount=value[0], currency=value[1])
    
    def __get__(self, obj, type=None):
        if obj is None:
            raise AttributeError('Can only be accessed via an instance.')
        if not isinstance(obj.__dict__[self.field.name], Money):
            obj.__dict__[self.field.name] = self._money_from_obj(obj)
        return obj.__dict__[self.field.name]
    
    def __set__(self, obj, value):
        if isinstance(value, tuple):
            value = Money2(amount=value[0], currency=value[1])
        if isinstance(value, Money):
            obj.__dict__[self.field.name] = value.amount  
            setattr(obj, self.currency_field_name, smart_unicode(value.currency))
        else:
            obj.__dict__[self.field.name] = self.field.to_python(value) 

         
class CurrencyField(models.CharField):
    
    def __init__(self, price_field=None, verbose_name=None, name=None, default=DEFAULT_CURRENCY, **kwargs):
        if isinstance(default, Currency):
            default = default.code
        kwargs['max_length'] = 3
        self.price_field = price_field
        super(CurrencyField, self).__init__(verbose_name, name, default=default, **kwargs)
    
    def get_internal_type(self): 
        return "CharField"

class MoneyField(models.DecimalField):
    
    def __init__(self, verbose_name=None, name=None, 
                 max_digits=None, decimal_places=None,
                 default=Money(0.0, DEFAULT_CURRENCY),
                 default_currency=DEFAULT_CURRENCY,
                 currency_choices=CURRENCY_CHOICES, **kwargs):
        if isinstance(default, basestring):
            amount, currency = default.split(" ")
            default = Money(float(amount), Currency(code=currency))
        if isinstance(default, float):
            default = Money(default, default_currency)
        if not isinstance(default, Money):
            raise Exception("default value must be an instance of Money, is: %s" % str(default))
            
        # Avoid giving the user hard-to-debug errors if they miss required attributes
        if max_digits is None:
            raise Exception("You have to provide a max_digits attribute to Money fields.")
        
        if decimal_places is None:
            raise Exception("You have to provide a decimal_places attribute to Money fields.")
        
        if not default_currency:
            default_currency = default.currency
        self.default_currency = default_currency
        self.currency_choices = currency_choices
        self.frozen_by_south = kwargs.pop('frozen_by_south', None)
        
        super(MoneyField, self).__init__(verbose_name, name, max_digits, decimal_places, default=default, **kwargs)
    
    def to_python(self, value):
        if isinstance(value, Money):
            value = value.amount
        if isinstance(value, tuple):
            value = value[0]
        return super(MoneyField, self).to_python(value)
    
    def get_internal_type(self):
        return "DecimalField"
    
    def contribute_to_class(self, cls, name):
        c_field_name = currency_field_name(name)
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
        
        from managers import money_manager

        if getattr(cls, '_default_manager', None):
            cls._default_manager = money_manager(cls._default_manager)
        elif hasattr(cls, 'objects'):
            cls.objects = money_manager(cls.objects)
        else:
            cls.objects = money_manager(models.Manager)
        
    def get_db_prep_save(self, value, connection):
        if isinstance(value, Money):
            value = value.amount
        return super(MoneyField, self).get_db_prep_save(value, connection)
    
    def get_db_prep_lookup(self, lookup_type, value, connection, prepared=False):
        if not lookup_type in SUPPORTED_LOOKUPS: 
            raise NotSupportedLookup(lookup_type)
        value = self.get_db_prep_save(value)
        return super(MoneyField, self).get_db_prep_lookup(lookup_type, value, connection, prepared)
    
    def get_default(self):
        if isinstance(self.default, Money):
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
        return '\"%s\"' % str(self.default_currency.code)

## South support
try:
    from south.modelsinspector import add_introspection_rules
    
    rules = [
        ((MoneyField,),
         [], # No positional args
         {
             'default_currency':('get_south_default_currency',{}),
             'default': ("get_south_default", {},)
         }),
        ((CurrencyField,),
         [],  # No positional args
         {
         }),
    ]
    
    add_introspection_rules(rules, ["^djmoney\.models"])
except ImportError:
    pass
