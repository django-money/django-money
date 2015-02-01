from functools import wraps

import django
from django.db.models.expressions import ExpressionNode, F

try:
    from django.utils.encoding import smart_unicode
except ImportError:
    # Python 3
    from django.utils.encoding import smart_text as smart_unicode

from djmoney.utils import get_currency_field_name


def _expand_money_params(kwargs):
    def get_clean_name(name):
        # Get rid of __lt, __gt etc for the currency lookup
        path = name.split(LOOKUP_SEP)
        if path[-1] in QUERY_TERMS:
            return LOOKUP_SEP.join(path[:-1])
        else:
            return name

    from moneyed import Money
    try:
        from django.db.models.constants import LOOKUP_SEP
    except ImportError:
        # Django < 1.5
        LOOKUP_SEP = '__'
    from django.db.models.sql.constants import QUERY_TERMS

    to_append = {}
    for name, value in kwargs.items():
        if isinstance(value, Money):
            clean_name = get_clean_name(name)
            to_append[name] = value.amount
            to_append[get_currency_field_name(clean_name)] = smart_unicode(
                value.currency)
        if isinstance(value, ExpressionNode):
            clean_name = get_clean_name(name)
            to_append['_'.join([clean_name, 'currency'])] = F('_'.join([value.name, 'currency']))

    kwargs.update(to_append)
    return kwargs


def understands_money(func):
    """
    Used to wrap a queryset method with logic to expand
    a query from something like:

    mymodel.objects.filter(money=Money(100,"USD"))

    To something equivalent to:

    mymodel.objects.filter(money=Decimal("100.0), money_currency="USD")
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        kwargs = kwargs.copy()
        kwargs = _expand_money_params(kwargs)
        return func(*args, **kwargs)

    return wrapper


RELEVANT_QUERYSET_METHODS = ['dates', 'distinct', 'extra', 'get',
                             'get_or_create', 'filter', 'complex_filter',
                             'exclude', 'in_bulk', 'iterator', 'latest',
                             'order_by', 'select_related', 'values']


def add_money_comprehension_to_queryset(qs):
    # Decorate each relevant method with understand_money in the queryset given
    for attr in RELEVANT_QUERYSET_METHODS:
        setattr(qs, attr, understands_money(getattr(qs, attr)))
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
            return add_money_comprehension_to_queryset(method(*args, **kwargs))

        # If we are being called by code pre Django 1.6, need
        # 'get_query_set'.
        if django.VERSION < (1, 6):
            get_query_set = get_queryset

    manager.__class__ = MoneyManager
    return manager
