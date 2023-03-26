from decimal import Decimal
from textwrap import dedent
from unittest.mock import patch

from django.core.exceptions import ImproperlyConfigured

import pytest

from djmoney.contrib.exchange.exceptions import MissingRate
from djmoney.contrib.exchange.models import _get_rate, convert_money, get_rate
from djmoney.money import Currency, Money


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    "source, target, expected, queries",
    (
        ("USD", "USD", 1, 0),
        ("USD", "EUR", 2, 1),
        ("EUR", "USD", Decimal("0.5"), 1),
        (Currency("USD"), "USD", 1, 0),
        ("USD", Currency("USD"), 1, 0),
    ),
)
@pytest.mark.usefixtures("simple_rates")
def test_get_rate(source, target, expected, django_assert_num_queries, queries):
    with django_assert_num_queries(queries):
        assert get_rate(source, target) == expected


@pytest.mark.parametrize(
    "source, target, expected",
    (
        ("NOK", "SEK", Decimal("1.067732610555839085161462146")),
        ("SEK", "NOK", Decimal("0.9365640705489186883886537319")),
    ),
)
@pytest.mark.usefixtures("default_openexchange_rates")
def test_rates_via_base(source, target, expected, django_assert_num_queries):
    with django_assert_num_queries(1):
        assert get_rate(source, target) == expected


@pytest.mark.parametrize("source, target", (("NOK", "ZAR"), ("ZAR", "NOK"), ("USD", "ZAR"), ("ZAR", "USD")))
@pytest.mark.usefixtures("default_openexchange_rates")
def test_unknown_currency_with_partially_exiting_currencies(source, target):
    with pytest.raises(MissingRate, match=f"Rate {source} \\-\\> {target} does not exist"):
        get_rate(source, target)


@pytest.mark.parametrize("source, target", (("USD", "EUR"), ("SEK", "ZWL")))
def test_unknown_currency(source, target):
    with pytest.raises(MissingRate, match=f"Rate {source} \\-\\> {target} does not exist"):
        get_rate(source, target)


def test_string_representation(backend):
    assert str(backend) == backend.name


@pytest.mark.usefixtures("simple_rates")
def test_cache():
    with patch("djmoney.contrib.exchange.models._get_rate", wraps=_get_rate) as original:
        assert get_rate("USD", "USD") == 1
        assert original.call_count == 0
        assert get_rate("USD", "EUR") == 2
        assert original.call_count == 1
        assert get_rate("USD", "EUR") == 2
        assert original.call_count == 1


def test_bad_configuration(settings):
    settings.INSTALLED_APPS.remove("djmoney.contrib.exchange")
    with pytest.raises(ImproperlyConfigured):
        convert_money(Money(1, "USD"), "EUR")


def test_without_installed_exchange(testdir):
    """
    If there is no 'djmoney.contrib.exchange' in INSTALLED_APPS importing `Money` should not cause a RuntimeError.
    Details: GH-385.
    """
    testdir.mkpydir("money_app")
    testdir.makepyfile(
        app_settings="""
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'test.db',
        }
    }
    INSTALLED_APPS = ['djmoney']
    SECRET_KEY = 'foobar'
    """
    )
    result = testdir.runpython_c(
        dedent(
            """
    import os
    os.environ['DJANGO_SETTINGS_MODULE'] = 'app_settings'
    from django import setup

    setup()
    from djmoney.money import Money
    print(Money(1, 'USD'))
    """
        )
    )
    result.stdout.fnmatch_lines(["$1.00"])
