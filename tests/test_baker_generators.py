import pytest
from model_bakery import baker

from djmoney.money import Money


pytestmark = pytest.mark.django_db


def test_baker():
    base_model = baker.make("ModelWithTwoMoneyFields")
    assert base_model.amount1 == Money(100, "USD")
