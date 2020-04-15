import graphene

from djmoney.money import Money
from graphene.types import InputObjectType, ObjectType, Scalar
from graphql.language import ast

from ..settings import DECIMAL_PLACES, BASE_CURRENCY


class StringMoneyField(Scalar):
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
            return StringMoneyField.parse_value(node.value)

    @staticmethod
    def parse_value(value):
        if isinstance(value, Money):
            return value

        amount, currency = value.split(" ")
        return Money(amount=float(amount), currency=currency)


class MoneyField(ObjectType):
    amount = graphene.Float(description="The numerical amount.")
    currency = graphene.String(description="The 3-letter ISO currency code.")
    str = StringMoneyField()


class MoneyFieldInput(InputObjectType):
    amount = graphene.Float(description="The numerical amount.")
    currency = graphene.String(description="The 3-letter ISO currency code.")

    def __str__(self):
        return f'{self.amount} {self.currency}'


__all__ = ('MoneyField', 'MoneyFieldInput', 'StringMoneyField')
