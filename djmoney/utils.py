# -*- coding: utf-8 -*-
from django.db.models import F

from moneyed import Money

from ._compat import BaseExpression, set_expression_rhs, split_expression


def get_currency_field_name(name):
    return '%s_currency' % name


def get_amount(value):
    """
    Extracts decimal value from Money or Expression.
    """
    if isinstance(value, Money):
        return value.amount
    elif isinstance(value, BaseExpression) and not isinstance(value, F):
        return get_amount(value.value)
    return value


def prepare_expression(expr):
    """
    Prepares some complex money expression to be used in query.
    """
    lhs, rhs = split_expression(expr)
    amount = get_amount(rhs)
    set_expression_rhs(expr, amount)
    return lhs
