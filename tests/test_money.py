from django.utils.translation import override

import pytest

from djmoney.money import DefaultMoney, Money, get_current_locale


def test_repr():
    assert repr(Money("10.5", "USD")) == "Money('10.5', 'USD')"


def test_legacy_repr():
    assert repr(Money("10.5", "USD", decimal_places_display=2)) == "Money('10.5', 'USD')"


def test_html_safe():
    assert Money("10.5", "EUR").__html__() == "€10.50"


def test_legacy_html_safe():
    assert Money("10.5", "EUR", decimal_places_display=2).__html__() == "10.50\xa0€"


def test_html_unsafe():
    class UnsafeMoney(Money):
        def __str__(self):
            return "<script>"

    assert UnsafeMoney().__html__() == "&lt;script&gt;"


def test_default_mul():
    assert Money(10, "USD") * 2 == Money(20, "USD")


def test_default_truediv():
    assert Money(10, "USD") / 2 == Money(5, "USD")
    assert Money(10, "USD") / Money(2, "USD") == 5


def test_reverse_truediv_fails():
    with pytest.raises(TypeError):
        10 / Money(5, "USD")


@pytest.mark.parametrize(
    "locale, expected",
    (
        ("pl", "PL_PL"),
        ("pl_PL", "pl_PL"),
    ),
)
def test_legacy_get_current_locale(locale, expected):
    with override(locale):
        assert get_current_locale(for_babel=False) == expected


@pytest.mark.parametrize(
    "locale, expected",
    (
        ("pl", "pl"),
        ("pl-pl", "pl_PL"),
        ("sv", "sv"),
        ("sv-se", "sv_SE"),
        ("en-us", "en_US"),
        ("en-gb", "en_GB"),
    ),
)
def test_get_current_locale(locale, expected):
    with override(locale):
        assert get_current_locale() == expected


def test_round():
    assert round(Money("1.69", "USD"), 1) == Money("1.7", "USD")


def test_configurable_decimal_number():
    # Override default configuration per instance, keeps human readable output to default
    mny = Money("10.543", "USD", decimal_places=3)
    assert str(mny) == "$10.54"
    assert mny.decimal_places == 3


def test_localize_decimal_places_default():
    # use default decimal display places from settings
    assert str(Money("10.543125", "USD")) == "$10.54"


def test_localize_decimal_places_overwrite():
    assert str(Money("10.543125", "USD", decimal_places_display=4)) == "$10.5431"


def test_localize_decimal_places_both():
    assert str(Money("10.543125", "USD", decimal_places=5, decimal_places_display=1)) == "$10.5"


def test_add_decimal_places():
    one = Money("1.0000", "USD", decimal_places=4)
    two = Money("2.000000005", "USD", decimal_places=10)

    result = one + two
    assert result.decimal_places == 10


def test_add_decimal_places_zero():
    two = Money("2.005", "USD", decimal_places=3)

    result = two + 0
    assert result.decimal_places == 3


@pytest.mark.parametrize("decimal_places", (1, 4))
@pytest.mark.parametrize(
    "operation",
    (
        lambda a, d: a * 2,
        lambda a, d: 2 * a,
        lambda a, d: a / 5,
        lambda a, d: a - Money("2", "USD", decimal_places=d, decimal_places_display=d),
        lambda a, d: Money("2", "USD", decimal_places=d, decimal_places_display=d) - a,
        lambda a, d: a + Money("2", "USD", decimal_places=d, decimal_places_display=d),
        lambda a, d: Money("2", "USD", decimal_places=d, decimal_places_display=d) + a,
        lambda a, d: -a,
        lambda a, d: +a,
        lambda a, d: abs(a),
        lambda a, d: 5 % a,
        lambda a, d: round(a),
        lambda a, d: a.round(),
    ),
)
def test_keep_decimal_places(operation, decimal_places):
    # Arithmetic operations should keep the `decimal_places` value
    amount = Money("1.0000", "USD", decimal_places=decimal_places, decimal_places_display=decimal_places)
    new = operation(amount, decimal_places)
    assert new.decimal_places == decimal_places
    assert new.decimal_places_display == decimal_places


def test_decimal_places_display_overwrite():
    number = Money("1.23456789", "USD")
    assert str(number) == "$1.23"
    number.decimal_places_display = 5
    assert str(number) == "$1.23457"
    number.decimal_places_display = None
    assert str(number) == "$1.23"


def test_sub_negative():
    # See GH-593
    total = DefaultMoney(0, "EUR")
    bills = (Money(8, "EUR"), Money(25, "EUR"))
    for bill in bills:
        total -= bill
    assert total == Money(-33, "EUR")


@pytest.mark.parametrize(
    "decimal_places_display, decimal_places",
    [
        [None, None],
        [0, 0],
        [1, 0],
        [4, 0],
        [0, 1],
        [1, 1],
        [4, 1],
        [0, 4],
        [1, 4],
        [4, 4],
        [None, 4],
        [None, 1],
        [None, 0],
        [4, None],
        [1, None],
        [0, None],
    ],
)
def test_proper_copy_of_attributes(decimal_places_display, decimal_places):
    one = Money(1, "EUR", decimal_places_display=decimal_places_display)

    assert one._decimal_places_display is decimal_places_display
    assert one.decimal_places == 2, "default value"

    two = Money(2, "EUR", decimal_places=decimal_places)

    assert two._decimal_places_display is None, "default value"
    assert two.decimal_places == decimal_places

    result = Money(3, "EUR")
    one._copy_attributes(two, result)

    assert result._decimal_places_display == decimal_places_display
    assert result.decimal_places == max(2, decimal_places) if decimal_places is not None else 2

    result = Money(0, "EUR")
    one._copy_attributes(Money(1, "EUR", decimal_places_display=3), result)

    assert result._decimal_places_display == max(3, decimal_places_display) if decimal_places_display is not None else 3

    result = Money(0, "EUR")
    one._copy_attributes(1, result)

    assert result._decimal_places_display == decimal_places_display
    assert result.decimal_places == 2

    result = Money(0, "EUR")
    two._copy_attributes(1, result)

    assert result._decimal_places_display is None
    assert result.decimal_places == decimal_places if decimal_places else 2
