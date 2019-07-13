from djmoney.money import Money
from graphene.types import Scalar
from graphql.language import ast

from ..settings import DECIMAL_PLACES, BASE_CURRENCY


class MoneyField(Scalar):
    @staticmethod
    def serialize(money):
        if money is None or money == 0:
            money = Money(amount=0, currency=BASE_CURRENCY)

        if isinstance(money, Money):
            return f"{money.amount:.{DECIMAL_PLACES}f} {money.currency}"

        raise NotImplementedError

    @staticmethod
    def parse_literal(node):
        if isinstance(node, ast.StringValue):
            return MoneyField.parse_value(node.value)

    @staticmethod
    def parse_value(value):
        amount, currency = value.split(" ")
        return Money(amount=float(amount), currency=currency)


__all__ = ('MoneyField',)
