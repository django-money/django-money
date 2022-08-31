from decimal import Decimal

from djmoney.money import Money


def gen_money():
    return Money(Decimal(100), "USD")


try:
    from model_bakery import baker

    baker.generators.add("djmoney.models.fields.MoneyField", gen_money)
except ImportError:
    pass
