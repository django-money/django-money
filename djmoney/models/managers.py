from django.db import models
from django.db.models.query import QuerySet
from django.utils.encoding import smart_unicode
from fields import currency_field_name

__all__ = ('QuerysetWithMoney', 'MoneyManager',)


class QuerysetWithMoney(QuerySet):
    
    def _update_params(self, kwargs):
        from moneyed import Money
        from django.db.models.sql.constants import LOOKUP_SEP
        to_append = {}
        for name, value in kwargs.items():
            if isinstance(value, Money):
                path = name.split(LOOKUP_SEP)
                if len(path) > 1:
                    field_name = currency_field_name(path[0])
                else:
                    field_name = currency_field_name(name)
                to_append[name] = value.amount
                to_append[field_name] = smart_unicode(value.currency)
        kwargs.update(to_append)
        return kwargs
        
    def dates(self, *args, **kwargs):
        kwargs = self._update_params(kwargs)
        return super(QuerysetWithMoney, self).dates(*args, **kwargs)

    def distinct(self, *args, **kwargs):
        kwargs = self._update_params(kwargs)
        return super(QuerysetWithMoney, self).distinct(*args, **kwargs)

    def extra(self, *args, **kwargs):
        kwargs = self._update_params(kwargs)
        return super(QuerysetWithMoney, self).extra(*args, **kwargs)

    def get(self, *args, **kwargs):
        kwargs = self._update_params(kwargs)
        return super(QuerysetWithMoney, self).get(*args, **kwargs)

    def get_or_create(self, **kwargs):
        kwargs = self._update_params(kwargs)
        return super(QuerysetWithMoney, self).get_or_create(**kwargs)

    def filter(self, *args, **kwargs):
        kwargs = self._update_params(kwargs)
        return super(QuerysetWithMoney, self).filter(*args, **kwargs)

    def complex_filter(self, *args, **kwargs):
        kwargs = self._update_params(kwargs)
        return super(QuerysetWithMoney, self).complex_filter(*args, **kwargs)

    def exclude(self, *args, **kwargs):
        kwargs = self._update_params(kwargs)
        return super(QuerysetWithMoney, self).exclude(*args, **kwargs)

    def in_bulk(self, *args, **kwargs):
        kwargs = self._update_params(kwargs)
        return super(QuerysetWithMoney, self).in_bulk(*args, **kwargs)

    def iterator(self, *args, **kwargs):
        kwargs = self._update_params(kwargs)
        return super(QuerysetWithMoney, self).iterator(*args, **kwargs)

    def latest(self, *args, **kwargs):
        kwargs = self._update_params(kwargs)
        return super(QuerysetWithMoney, self).latest(*args, **kwargs)

    def order_by(self, *args, **kwargs):
        kwargs = self._update_params(kwargs)
        return super(QuerysetWithMoney, self).order_by(*args, **kwargs)

    def select_related(self, *args, **kwargs):
        kwargs = self._update_params(kwargs)
        return super(QuerysetWithMoney, self).select_related(*args, **kwargs)

    def values(self, *args, **kwargs):
        kwargs = self._update_params(kwargs)
        return super(QuerysetWithMoney, self).values(*args, **kwargs)


class MoneyManager(models.Manager):
    def get_query_set(self):
        return QuerysetWithMoney(self.model)
