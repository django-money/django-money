from functools import wraps

import django
try:
    from django.db.models.expressions import BaseExpression, F
except ImportError:
    # Django < 1.8
    from django.db.models.expressions import ExpressionNode as BaseExpression, F
from django.db.models.sql.query import Query
from djmoney.models.fields import MoneyField
from django.db.models.query_utils import Q
from moneyed import Money


try:
    from django.utils.encoding import smart_unicode
except ImportError:
    # Python 3
    from django.utils.encoding import smart_text as smart_unicode

from djmoney.utils import get_currency_field_name

try:
    from django.db.models.constants import LOOKUP_SEP
except ImportError:
    # Django < 1.5
    LOOKUP_SEP = '__'

from django.db.models.sql.constants import QUERY_TERMS


def _get_clean_name(name):

    # Get rid of __lt, __gt etc for the currency lookup
    path = name.split(LOOKUP_SEP)
    if path[-1] in QUERY_TERMS:
        return LOOKUP_SEP.join(path[:-1])
    else:
        return name


def _get_field(model, name):
    if django.VERSION[0] >= 1 and django.VERSION[1] >= 8:
        # Django 1.8+ - can use something like 
        # expression.output_field.get_internal_field() == 'Money..'
        raise NotImplementedError("Django 1.8+ support is not implemented.")

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
        lookup_model = model
        for counter, field_name in enumerate(parts):
            try:
                lookup_field = lookup_model._meta.get_field(field_name)
            except FieldDoesNotExist:
                # Not a field. Bail out.
                parts.pop()
                break
            # Unless we're at the end of the list of lookups, let's attempt
            # to continue traversing relations.
            if (counter + 1) < num_parts:
                try:
                    lookup_model = lookup_field.rel.to
                except AttributeError:
                    # Not a related field. Bail out.
                    parts.pop()
                    break

    if django.VERSION[0] >= 1 and django.VERSION[1] in (6, 7):
        # Django 1.6-1.7
        field = qs.setup_joins(parts, opts, alias)[0]
    else:
        # Django 1.4-1.5
        field = qs.setup_joins(parts, opts, alias, False)[0]

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
                    if isinstance(value, BaseExpression):
                        field = _get_field(model, name)
                        if isinstance(field, MoneyField):
                            clean_name = _get_clean_name(name)
                            arg.children[i] = Q(*[
                                child, 
                                ('_'.join([clean_name, 'currency']), F(get_currency_field_name(value.name)))
                            ])
    return args


def _expand_money_kwargs(model, kwargs):
    """
    Augments kwargs so that they contain _currency lookups.
    """
    to_append = {}
    for name, value in kwargs.items():
        if isinstance(value, Money):
            clean_name = _get_clean_name(name)
            to_append[name] = value.amount
            to_append[get_currency_field_name(clean_name)] = smart_unicode(
                value.currency)
        if isinstance(value, BaseExpression):
            field = _get_field(model, name)
            if isinstance(field, MoneyField):
                clean_name = _get_clean_name(name)
                to_append['_'.join([clean_name, 'currency'])] = F(get_currency_field_name(value.name))

    kwargs.update(to_append)
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
        if django.VERSION < (1, 6):
            get_query_set = get_queryset

    manager.__class__ = MoneyManager
    return manager
