# coding: utf-8
from moneyed import Money

from ._compat import BaseExpression


get_currency_field_name = lambda name: "%s_currency" % name


def get_amount(value):
    """
    Extracts decimal value from Money or Expression.
    """
    if isinstance(value, Money):
        return value.amount
    elif isinstance(value, BaseExpression):
        return get_amount(value.value)
    return value
