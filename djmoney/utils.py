# coding: utf-8
from django import VERSION

from moneyed import Money

from ._compat import BaseExpression


get_currency_field_name = lambda name: "%s_currency" % name


def split_expression(expr):
    """
    Returns lhs and rhs of the expression.
    """
    if VERSION < (1, 8):
        return expr.children
    else:
        return expr.lhs, expr.rhs


def get_amount(value):
    """
    Extracts decimal value from Money or Expression.
    """
    if isinstance(value, Money):
        return value.amount
    elif isinstance(value, BaseExpression):
        return get_amount(value.value)
    return value
