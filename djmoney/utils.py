from django.db.models import F
from django.db.models.expressions import BaseExpression

from djmoney.money import Money, Currency
from moneyed import Money as OldMoney, get_currency

MONEY_CLASSES = (Money, OldMoney)


def get_currency_field_name(name, field=None):
    if field and getattr(field, "currency_field_name", None):
        return field.currency_field_name
    return "%s_currency" % name


def get_amount(value):
    """
    Extracts decimal value from Money or Expression.
    """
    if isinstance(value, MONEY_CLASSES):
        return value.amount
    elif isinstance(value, BaseExpression) and not isinstance(value, F):
        return get_amount(value.value)
    return value


def prepare_expression(expr):
    """
    Prepares some complex money expression to be used in query.
    """
    if isinstance(expr.rhs, F):
        # Money(...) + F('money')
        target, return_value = expr.lhs, expr.rhs
    else:
        # F('money') + Money(...)
        target, return_value = expr.rhs, expr.lhs
    amount = get_amount(target)
    target.value = amount
    return return_value


def old_currency_to_new_currency(old_currency):
    return Currency(
        code=old_currency.code,
        countries=old_currency.countries,
        numeric=old_currency.numeric,
        name=old_currency.name,
    )


def get_currency_by_name(name):
    old_currency = get_currency(name)
    return old_currency_to_new_currency(old_currency)
