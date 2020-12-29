from django.utils.translation import override

import pytest

from djmoney.money import Money, get_current_locale


def test_repr():
    assert repr(Money("10.5", "USD")) == "<Money: 10.5 USD>"


def test_html_safe():
    assert Money("10.5", "EUR").__html__() == u"10.50\xa0€"


def test_html_unsafe():
    class UnsafeMoney(Money):
        def __str__(self):
            return "<script>"

    assert UnsafeMoney().__html__() == "&lt;script&gt;"


def test_default_mul():
    assert Money(10, "USD") * 2 == Money(20, "USD")


def test_default_truediv():
    assert Money(10, "USD") / 2 == Money(5, "USD")


def test_reverse_truediv_fails():
    with pytest.raises(TypeError):
        10 / Money(5, "USD")


@pytest.mark.parametrize("locale, expected", (("pl", "PL_PL"), ("pl_PL", "pl_PL")))
def test_get_current_locale(locale, expected):
    with override(locale):
        assert get_current_locale() == expected


def test_round():
    assert round(Money("1.69", "USD"), 1) == Money("1.7", "USD")


def test_configurable_decimal_number():
    # Override default configuration per instance
    assert str(Money("10.543", "USD", decimal_places=3)) == "$10.543"


def test_add_decimal_places():
    one = Money("1.0000", "USD", decimal_places=4)
    two = Money("2.000000005", "USD", decimal_places=10)

    result = one + two
    assert result.decimal_places == 10


def test_add_decimal_places_zero():
    two = Money("2.005", "USD", decimal_places=3)

    result = two + 0
    assert result.decimal_places == 3


def test_mul_decimal_places():
    """ Test __mul__ and __rmul__ """
    two = Money("1.0000", "USD", decimal_places=4)

    result = 2 * two
    assert result.decimal_places == 4

    result = two * 2
    assert result.decimal_places == 4


def test_fix_decimal_places():
    one = Money(1, "USD", decimal_places=7)
    assert one._fix_decimal_places(Money(2, "USD", decimal_places=3)) == 7
    assert one._fix_decimal_places(Money(2, "USD", decimal_places=30)) == 30


def test_fix_decimal_places_none():
    one = Money(1, "USD", decimal_places=7)
    assert one._fix_decimal_places(None) == 7


def test_fix_decimal_places_multiple():
    one = Money(1, "USD", decimal_places=7)
    assert one._fix_decimal_places(None, Money(3, "USD", decimal_places=8)) == 8
