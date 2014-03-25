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

    def decorator(*args, **kwargs):
        kwargs = _expand_money_params(kwargs)
        return func(*args, **kwargs)

    return decorator


RELEVANT_QUERYSET_METHODS = ['dates', 'distinct', 'extra', 'get',
                             'get_or_create', 'filter', 'complex_filter',
                             'exclude', 'in_bulk', 'iterator', 'latest',
                             'order_by', 'select_related', 'values']


def add_money_comprehension_to_queryset(qs):
    # Decorate each relevant method with understand_money in the queryset given
    list(map(lambda attr: setattr(qs, attr, understands_money(getattr(qs, attr))),
        RELEVANT_QUERYSET_METHODS))
    return qs


def money_manager(manager):
    """
    Wraps a model managers get_query_set method so that each query set it returns
    is able to work on money fields.

    We use this instead of a real model manager, in order to allow users of django-money to
    use other managers special managers while still doing money queries.
    """
    old_get_query_set = manager.get_query_set

    def get_query_set(*args, **kwargs):
        return add_money_comprehension_to_queryset(old_get_query_set(*args, **kwargs))

    manager.get_query_set = get_query_set

    if hasattr(manager, 'get_queryset'):
        # Django 1.6
        manager.get_queryset = get_query_set

    return manager
