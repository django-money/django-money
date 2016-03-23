# -*- coding: utf-8 -*-
from functools import wraps

from django import VERSION
from django.db.models import F
from django.db.models.query_utils import Q
from django.db.models.sql.constants import QUERY_TERMS
from django.db.models.sql.query import Query

from moneyed import Money

from .._compat import LOOKUP_SEP, BaseExpression, smart_unicode
from ..utils import get_currency_field_name, prepare_expression
from .fields import MoneyField


def _get_clean_name(name):

    # Get rid of __lt, __gt etc for the currency lookup
    path = name.split(LOOKUP_SEP)
    if path[-1] in QUERY_TERMS:
        return LOOKUP_SEP.join(path[:-1])
    else:
        return name


def _get_field(model, name):
    from django.db.models.fields import FieldDoesNotExist

    # Create a fake query object so we can easily work out what field
    # type we are dealing with
    qs = Query(model)
    opts = qs.get_meta()
    alias = qs.get_initial_alias()

    parts = name.split(LOOKUP_SEP)

    # The following is borrowed from the innards of Query.add_filter - it strips out __gt, __exact et al.
    num_parts = len(parts)
    if num_parts > 1 and parts[-1] in qs.query_terms:
        # Traverse the lookup query to distinguish related fields from
        # lookup types.
        for counter, field_name in enumerate(parts, 1):
            try:
                lookup_field = model._meta.get_field(field_name)
            except FieldDoesNotExist:
                # Not a field. Bail out.
                parts.pop()
                break
            # Unless we're at the end of the list of lookups, let's attempt
            # to continue traversing relations.
            if counter < num_parts:
                try:
                    model = lookup_field.rel.to
                except AttributeError:
                    # Not a related field. Bail out.
                    parts.pop()
                    break

    if VERSION < (1, 6):
        field = qs.setup_joins(parts, opts, alias, False)[0]
    else:
        field = qs.setup_joins(parts, opts, alias)[0]

    return field


def _expand_money_args(model, args):
    """
    Augments args so that they contain _currency lookups - ie.. Q() | Q()
    """
    for arg in args:
        if isinstance(arg, Q):
            for i, child in enumerate(arg.children):
                if isinstance(child, Q):
                    _expand_money_args(model, [child])
                elif isinstance(child, (list, tuple)):
                    name, value = child
                    if isinstance(value, Money):
                        clean_name = _get_clean_name(name)
                        arg.children[i] = Q(*[
                            child,
                            (get_currency_field_name(clean_name), smart_unicode(value.currency))
                        ])
                    if isinstance(value, (BaseExpression, F)):
                        field = _get_field(model, name)
                        if isinstance(field, MoneyField):
                            clean_name = _get_clean_name(name)
                            arg.children[i] = Q(*[
                                child,
                                (get_currency_field_name(clean_name), F(get_currency_field_name(value.name)))
                            ])
    return args


def _expand_money_kwargs(model, kwargs):
    """
    Augments kwargs so that they contain _currency lookups.
    """
    for name, value in list(kwargs.items()):
        if isinstance(value, Money):
            clean_name = _get_clean_name(name)
            kwargs[name] = value.amount
            kwargs[get_currency_field_name(clean_name)] = smart_unicode(value.currency)
        elif isinstance(value, (BaseExpression, F)) and \
                isinstance(_get_field(model, name), MoneyField):
            clean_name = _get_clean_name(name)
            if not isinstance(value, F):
                value = prepare_expression(value)
            kwargs[get_currency_field_name(clean_name)] = F(get_currency_field_name(value.name))
    return kwargs


def understands_money(model, func):
    """
    Used to wrap a queryset method with logic to expand
    a query from something like:

    mymodel.objects.filter(money=Money(100,"USD"))

    To something equivalent to:

    mymodel.objects.filter(money=Decimal("100.0), money_currency="USD")
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        args = _expand_money_args(model, args)
        kwargs = kwargs.copy()
        kwargs = _expand_money_kwargs(model, kwargs)
        return func(*args, **kwargs)

    return wrapper


RELEVANT_QUERYSET_METHODS = ['distinct', 'get', 'get_or_create', 'filter',
                             'exclude']


def add_money_comprehension_to_queryset(model, qs):
    # Decorate each relevant method with understand_money in the queryset given
    for attr in RELEVANT_QUERYSET_METHODS:
        setattr(qs, attr, understands_money(model, getattr(qs, attr)))
    return qs


def money_manager(manager):
    """
    Patches a model manager's get_queryset method so that each QuerySet it returns
    is able to work on money fields.

    This allow users of django-money to use other managers while still doing
    money queries.
    """

    # Need to dynamically subclass to add our behaviour, and then change
    # the class of 'manager' to our subclass.

    # Rejected alternatives:
    #
    # * A monkey patch that adds things to the manager instance dictionary.
    #   This fails due to complications with Manager._copy_to_model behaviour.
    #
    # * Returning a new MoneyManager instance (rather than modifying
    #   the passed in manager instance). This fails for reasons that
    #   are tricky to get to the bottom of - Manager does funny things.
    class MoneyManager(manager.__class__):

        def get_queryset(self, *args, **kwargs):
            # If we are calling code that is pre-Django 1.6, need to
            # spell it 'get_query_set'
            s = super(MoneyManager, self)
            method = getattr(s, 'get_queryset',
                             getattr(s, 'get_query_set', None))
            return add_money_comprehension_to_queryset(self.model, method(*args, **kwargs))

        # If we are being called by code pre Django 1.6, need
        # 'get_query_set'.
        if VERSION < (1, 6):
            get_query_set = get_queryset

    manager.__class__ = MoneyManager
    return manager
